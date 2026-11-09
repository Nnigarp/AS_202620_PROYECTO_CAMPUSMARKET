#!/usr/bin/env bash
set -euo pipefail
task_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$task_root"
cm_gradle_zip=$(python3 - <<'PY'
import hashlib
import os
from pathlib import Path
properties = dict(line.split("=", 1) for line in Path("frontend/campusmarket/android/gradle/wrapper/gradle-wrapper.properties").read_text().splitlines() if "=" in line)
url = properties["distributionUrl"].replace("\\:", ":")
assert url == "https://services.gradle.org/distributions/gradle-8.14-all.zip"
assert properties["distributionBase"] == properties["zipStoreBase"] == "GRADLE_USER_HOME"
assert properties["distributionPath"] == properties["zipStorePath"] == "wrapper/dists"
# Gradle PathAssembler uses MD5/base36 for the cache directory, not integrity.
number = int.from_bytes(hashlib.md5(url.encode(), usedforsecurity=False).digest(), "big")
cache_key = ""
while number:
    number, digit = divmod(number, 36)
    cache_key = "0123456789abcdefghijklmnopqrstuvwxyz"[digit] + cache_key
home = Path(os.environ.get("GRADLE_USER_HOME", str(Path.home() / ".gradle")))
directory = home / "wrapper/dists/gradle-8.14-all" / cache_key
directory.mkdir(parents=True, exist_ok=True)
print(directory / "gradle-8.14-all.zip")
PY
)
trap 'rm -f "$cm_gradle_zip.part"' EXIT
if ! curl --fail --location --retry 3 --connect-timeout 15 --max-time 120 --retry-max-time 180 --output "$cm_gradle_zip.part" "https://downloads.gradle.org/distributions/gradle-8.14-all.zip"; then
  curl --fail --location --retry 3 --connect-timeout 15 --max-time 120 --retry-max-time 180 --header "Accept: application/octet-stream" --output "$cm_gradle_zip.part" "https://api.github.com/repos/gradle/gradle-distributions/releases/assets/249401399"
fi
printf '%s  %s\n' 'efe9a3d147d948d7528a9887fa35abcf24ca1a43ad06439996490f77569b02d1' "$cm_gradle_zip.part" | sha256sum --check -
mv "$cm_gradle_zip.part" "$cm_gradle_zip"
# The unchanged wrapper installs the verified ZIP; no .ok marker or test result is fabricated.
