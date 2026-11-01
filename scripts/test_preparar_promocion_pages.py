"""Pruebas nuevas de promoción/rollback Git; sin Flutter, red ni sitio público."""

import contextlib
import json
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from scripts import preparar_promocion_pages as pages


class PromotionTests(unittest.TestCase):
    def metadata(self):
        run = {"id": pages.RUN, "head_sha": pages.WORKFLOW_SHA, "repository": {"full_name": pages.REPOSITORY},
               "head_repository": {"full_name": pages.REPOSITORY}, "event": "push", "head_branch": pages.WORK_BRANCH,
               "path": ".github/workflows/ensayo-pages.yml", "status": "completed", "conclusion": "success"}
        artifact = {"id": pages.ARTIFACT, "name": f"pages-candidate-{pages.RUN}-1", "expired": False,
                    "workflow_run": {"id": pages.RUN, "head_sha": pages.WORKFLOW_SHA}, "digest": "sha256:" + pages.ZIP_SHA}
        return run, artifact

    def archive(self, path, change=None, extra=None):
        files = {".nojekyll": b"", "source-revision.txt": (pages.SOURCE_SHA + "\n").encode(),
                 "index.html": b"test", "main.dart.js": b"synthetic"}
        files.update({f"assets/fixture-{i}.bin": bytes([i]) for i in range(38)})
        manifest = pages.tree_manifest(files)
        evidence = {"passed": True, "published": False, "workflow_sha": pages.WORKFLOW_SHA, "source_sha": pages.SOURCE_SHA,
                    "run": f"https://github.com/{pages.REPOSITORY}/actions/runs/{pages.RUN}",
                    "secret_scan": {"gitleaks": "8.30.1", "exit_code": 0},
                    "bundle_manifest_sha256": pages.digest(json.dumps(manifest, sort_keys=True).encode()),
                    "base_href": "/AS_202620_PROYECTO_CAMPUSMARKET/", "api": "https://campusmarket.iscoutb.dev"}
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("files.sha256.json", json.dumps(manifest))
            archive.writestr("result.json", json.dumps(evidence))
            for name, content in files.items():
                archive.writestr("site/" + name, change if name == "main.dart.js" and change is not None else content)
            if extra:
                archive.writestr(*extra)
        return pages.digest(path.read_bytes()), evidence["bundle_manifest_sha256"], files

    def test_metadata_requires_exact_run_repository_artifact_and_success(self):
        run, artifact = self.metadata()
        pages.validate_metadata(run, artifact)
        for key, value in (("head_sha", "a" * 40), ("conclusion", "failure"), ("event", "pull_request")):
            changed = {**run, key: value}
            with self.subTest(key=key), self.assertRaises(pages.Blocked):
                pages.validate_metadata(changed, artifact)
        with self.assertRaises(pages.Blocked):
            pages.validate_metadata(run, {**artifact, "digest": "sha256:" + "0" * 64})

    def test_zip_hash_is_checked_before_parsing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "original.zip"
            path.write_bytes(b"tampered-not-a-zip")
            with patch.object(pages.zipfile, "ZipFile") as parse, self.assertRaisesRegex(pages.Blocked, "ZIP original modificado"):
                pages.verify_zip(path)
            parse.assert_not_called()

    def test_exact_archive_preserves_hidden_and_binary_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "original.zip"
            zip_sha, manifest_sha, expected = self.archive(path)
            with patch.object(pages, "ZIP_SHA", zip_sha), patch.object(pages, "MANIFEST_SHA", manifest_sha):
                files, manifest = pages.verify_zip(path)
            self.assertEqual(files, expected)
            self.assertEqual(manifest, pages.tree_manifest(expected))
            self.assertIn(".nojekyll", files)

    def test_corrupted_file_inside_zip_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "original.zip"
            zip_sha, manifest_sha, _ = self.archive(path, change=b"different compiled bytes")
            with patch.object(pages, "ZIP_SHA", zip_sha), patch.object(pages, "MANIFEST_SHA", manifest_sha), self.assertRaisesRegex(pages.Blocked, "Archivo no corresponde"):
                pages.verify_zip(path)

    def test_additional_files_and_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "original.zip"
            for extra in (("site/../../private", b"bad"), ("site/CNAME", b"other.invalid")):
                zip_sha, manifest_sha, _ = self.archive(path, extra=extra)
                with patch.object(pages, "ZIP_SHA", zip_sha), patch.object(pages, "MANIFEST_SHA", manifest_sha), self.assertRaises(pages.Blocked):
                    pages.verify_zip(path)
            link = zipfile.ZipInfo("site/link")
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            zip_sha, manifest_sha, _ = self.archive(path, extra=(link, b"/private"))
            with patch.object(pages, "ZIP_SHA", zip_sha), patch.object(pages, "MANIFEST_SHA", manifest_sha), self.assertRaises(pages.Blocked):
                pages.verify_zip(path)

    def test_pages_source_domain_and_https_must_remain_unchanged(self):
        good = {"build_type": "legacy", "source": {"branch": "gh-pages", "path": "/"}, "html_url": pages.URL, "https_enforced": True, "cname": None}
        pages.validate_pages(good)
        for key, value in (("source", {"branch": "master", "path": "/docs"}), ("https_enforced", False), ("cname", "custom.invalid")):
            with self.subTest(key=key), self.assertRaises(pages.Blocked):
                pages.validate_pages({**good, key: value})

    def test_gh_pages_cannot_be_a_push_target(self):
        refs = {pages.BACKUP: pages.OLD, pages.CANDIDATE: "a" * 40, "gh-pages": "b" * 40}
        with patch.object(pages, "git") as execute, self.assertRaises(pages.Blocked):
            pages.push_staging(refs)
        execute.assert_not_called()

    def test_concurrent_publication_change_stops_before_push(self):
        refs = {pages.BACKUP: pages.OLD, pages.CANDIDATE: "a" * 40, pages.ROLLBACK: "b" * 40}
        with patch.object(pages, "remote_head", return_value="c" * 40), patch.object(pages, "git") as execute, self.assertRaises(pages.Blocked):
            pages.push_staging(refs)
        execute.assert_not_called()

    def test_only_auxiliary_refs_are_pushed_without_force(self):
        refs = {pages.BACKUP: pages.OLD, pages.CANDIDATE: "a" * 40, pages.ROLLBACK: "b" * 40}
        def head(branch):
            return pages.OLD if branch == pages.PUBLISH_BRANCH else refs[branch]
        with patch.object(pages, "remote_head", side_effect=head), patch.object(pages, "git") as execute:
            pages.push_staging(refs)
        pushed = next(call.args for call in execute.call_args_list if call.args[0] == "push")
        self.assertEqual(pushed[:3], ("push", "--atomic", "origin"))
        self.assertFalse(any("gh-pages" in arg or "--force" in arg for arg in pushed))

    def test_git_candidate_rollback_and_bundle_recover_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.chdir(directory):
            pages.git("init", "--initial-branch=gh-pages", ".")
            old = {"index.html": b"old site", ".nojekyll": b"", "assets/blob.bin": b"\0\xffprevious"}
            for name, content in old.items():
                path = Path(name); path.parent.mkdir(exist_ok=True, parents=True); path.write_bytes(content)
            pages.git("add", ".")
            pages.git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-m", "Old public snapshot")
            previous = pages.git("rev-parse", "HEAD")
            old_tree = pages.git("rev-parse", "HEAD^{tree}")
            new = {**old, "index.html": b"new site", "assets/added.bin": b"\0\xfeapproved"}
            index = Path(directory) / "candidate.index"
            new_tree = pages.write_tree(new, index)
            candidate = pages.create_commit(new_tree, previous, "Candidate")
            rollback = pages.create_commit(old_tree, candidate, "Restore previous tree")
            self.assertEqual(pages.read_tree(candidate), new)
            self.assertEqual(pages.read_tree(rollback), old)
            self.assertEqual(pages.git("show", "-s", "--format=%P", rollback), candidate)
            self.assertEqual(pages.git("rev-parse", "gh-pages"), previous)
            refs = {pages.BACKUP: previous, pages.CANDIDATE: candidate, pages.ROLLBACK: rollback}
            for name, sha in refs.items():
                pages.git("update-ref", "refs/heads/" + name, sha)
            bundle = Path(directory) / "recovery.bundle"
            pages.git("bundle", "create", str(bundle), *["refs/heads/" + name for name in refs])
            recovery = Path(directory) / "restored.git"
            pages.git("init", "--bare", str(recovery))
            pages.git("--git-dir=" + str(recovery), "fetch", str(bundle), *["refs/heads/" + name + ":refs/heads/" + name for name in refs])
            for name, sha in refs.items():
                self.assertEqual(pages.git("--git-dir=" + str(recovery), "rev-parse", "refs/heads/" + name), sha)


if __name__ == "__main__":
    unittest.main()
