"""Comprueba enlaces Markdown locales y las ocho columnas de aspectos, sin red.

Requisito de ejecución: markdown-it-py==3.0.0. No consulta GitHub, sitios
públicos ni datos de aplicación; los enlaces externos solo se enumeran.
"""
import argparse
import collections
import json
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


def slug(text):
    text = text.lower().strip()
    return ''.join(c for c in text if c in '-_ ' or unicodedata.category(c)[0] in 'LNM').replace(' ', '-')


def anchors(path):
    text = path.read_text(encoding='utf-8-sig')
    result = set(re.findall(r'(?:id|name)=[\"\']([^\"\']+)[\"\']', text))
    tokens = MarkdownIt().enable('table').parse(text)
    counts = collections.Counter()
    for index, token in enumerate(tokens):
        if token.type == 'heading_open':
            inline = tokens[index + 1]
            title = ''.join(child.content for child in (inline.children or []) if child.type in ('text', 'code_inline'))
            base = slug(title)
            candidate = base if not counts[base] else base + '-' + str(counts[base])
            counts[base] += 1
            result.add(candidate)
    return result


def scan(root):
    internal, external = [], []
    files = sorted(root.rglob('*.md'))
    files = [p for p in files if '.git' not in p.parts and not any(s in p.parts for s in ('build', '.dart_tool', 'node_modules', '.venv'))]
    cache = {}
    for path in files:
        tokens = MarkdownIt().enable('table').parse(path.read_text(encoding='utf-8-sig'))
        current_line = 1
        for token in tokens:
            if token.map:
                current_line = token.map[0] + 1
            if token.type != 'inline':
                continue
            for child in token.children or []:
                url = child.attrGet('href') if child.type == 'link_open' else child.attrGet('src') if child.type == 'image' else None
                if url is None:
                    continue
                row = {'source': str(path.relative_to(root)), 'line': current_line, 'target': url}
                parsed = urlsplit(url)
                if parsed.scheme in ('http', 'https'):
                    external.append(row)
                    continue
                if parsed.scheme or url.startswith('//'):
                    continue
                destination = root / unquote(parsed.path).lstrip('/') if parsed.path.startswith('/') else path.parent / unquote(parsed.path)
                destination = destination.resolve() if parsed.path else path
                row['resolved'] = str(destination.relative_to(root)) if destination.is_relative_to(root) else str(destination)
                row['state'] = 'OK'
                if not destination.is_relative_to(root):
                    row['state'] = 'OUTSIDE_REPOSITORY'
                elif not destination.exists():
                    row['state'] = 'MISSING_PATH'
                elif parsed.fragment:
                    if destination.is_dir():
                        destination = destination / 'README.md'
                    if destination.suffix.lower() == '.md' and destination.exists():
                        if destination not in cache:
                            cache[destination] = anchors(destination)
                        fragment = unquote(parsed.fragment)
                        lines = re.fullmatch(r'L(\d+)(?:-L(\d+))?', fragment)
                        if lines and parsed.query == 'plain=1':
                            if max(int(n) for n in lines.groups() if n) > len(destination.read_text(encoding='utf-8-sig').splitlines()):
                                row['state'] = 'MISSING_LINE'
                        elif fragment not in cache[destination]:
                            row['state'] = 'MISSING_ANCHOR'
                internal.append(row)
    return {'markdown_files': len(files), 'internal_count': len(internal), 'external_count': len(external), 'internal': internal, 'external': external}


def check_aspects(root):
    """Comprueba las matrices ID/Aspecto; excluye tablas auxiliares de riesgos."""
    path = root / 'docs/aspectos.md'
    if not path.exists():
        return {'tables': 0, 'rows': 0, 'failures': ['Falta docs/aspectos.md']}
    source = path.read_text(encoding='utf-8-sig')
    source_lines = source.splitlines()
    tokens = MarkdownIt().enable('table').parse(source)
    tables, rows, failures = 0, 0, []
    current, cells, table_rows = [], [], []
    table_range = [0, 0]
    for token in tokens:
        if token.type == 'table_open':
            table_rows = []
            table_range = token.map
        elif token.type == 'tr_open':
            current, cells = [], []
        elif token.type in ('th_open', 'td_open'):
            cells = []
        elif token.type == 'inline':
            cells.append(token.content)
        elif token.type in ('th_close', 'td_close'):
            current.append(''.join(cells))
        elif token.type == 'tr_close':
            table_rows.append(current)
        elif token.type == 'table_close' and table_rows and table_rows[0][:2] == ['ID', 'Aspecto']:
            tables += 1
            expected = ['ID', 'Aspecto', 'Requisito', 'C4', 'ADR', 'Código', 'Pruebas', 'Evidencia']
            if table_rows[0] != expected:
                failures.append(f'Tabla {tables}: cabecera diferente de las ocho columnas canónicas')
            # CommonMark completa celdas faltantes e ignora las sobrantes al parsear.
            # Contrastar también las columnas escritas impide aceptar ese truncado.
            for line_number in range(*table_range):
                raw_cells = re.split(r'(?<!\\)\|', source_lines[line_number].strip())
                if raw_cells and not raw_cells[0]:
                    raw_cells.pop(0)
                if raw_cells and not raw_cells[-1]:
                    raw_cells.pop()
                if len(raw_cells) != 8:
                    failures.append(f'Línea {line_number + 1}: {len(raw_cells)} columnas escritas, se exigen ocho')
            for row in table_rows[1:]:
                rows += 1
                if len(row) != 8 or any(not cell.strip() for cell in row):
                    failures.append(f'Tabla {tables}, fila {row[0]}: columna vacía o número incorrecto')
    if not tables:
        failures.append('No se encontró la matriz de aspectos')
    return {'tables': tables, 'rows': rows, 'failures': failures}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path, nargs='?', default=Path(__file__).resolve().parents[1])
    parser.add_argument('--out', type=Path, help='Informe JSON opcional, fuera del árbol auditado')
    args = parser.parse_args()
    report = scan(args.root.resolve())
    table_check = check_aspects(args.root.resolve())
    report['aspects'] = table_check
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    failures = [r for r in report['internal'] if r['state'] != 'OK']
    print(json.dumps({'markdown_files': report['markdown_files'], 'internal': report['internal_count'], 'external': report['external_count'], 'external_unique': len({r['target'] for r in report['external']}), 'failures': failures, 'aspects': table_check}, ensure_ascii=False))
    sys.exit(1 if failures or table_check['failures'] else 0)
