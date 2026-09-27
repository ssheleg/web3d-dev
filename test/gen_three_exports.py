#!/usr/bin/env python3
"""Snapshot the public surface of the pinned three.js release into test/fixtures.

Online half (runs `npm pack`), deliberately outside `npm test`, which stays offline. The
snapshot it writes is what `test/validate.py` checks every code block against, so an import
that does not exist in the pinned release fails the gate — `bloom` imported from `three/tsl`
was that exact bug, caught by eye on 2026-09-27 and by nothing else.

    python3 test/gen_three_exports.py            # rewrites test/fixtures/three-exports.json
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "test"))
from validate import THREE_PIN  # noqa: E402  one pin, one home

OUT = ROOT / "test" / "fixtures" / "three-exports.json"


def export_names(src: str) -> set[str]:
    names: set[str] = set()
    for block in re.findall(r"export\s*\{([^}]*)\}", src):
        for part in block.split(","):
            part = part.strip()
            if not part:
                continue
            names.add(part.split(" as ")[-1].strip())
    names |= set(re.findall(r"export\s+(?:default\s+)?(?:async\s+)?(?:function\*?|class|const|let|var)\s+([A-Za-z_$][\w$]*)", src))
    if re.search(r"export\s+default", src):
        names.add("default")
    return names


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["npm", "pack", f"three@{THREE_PIN}", "--silent"], cwd=tmp, check=True,
                       capture_output=True)
        tgz = next(Path(tmp).glob("three-*.tgz"))
        with tarfile.open(tgz) as tf:
            tf.extractall(tmp, filter="data")
        pkg = Path(tmp) / "package"
        build = pkg / "build"
        surface = {
            "three": sorted(export_names((build / "three.core.js").read_text())
                            | export_names((build / "three.module.js").read_text())),
            "three/webgpu": sorted(export_names((build / "three.core.js").read_text())
                                   | export_names((build / "three.webgpu.js").read_text())),
            "three/tsl": sorted(export_names((build / "three.tsl.js").read_text())),
        }
        addons = {}
        for f in sorted((pkg / "examples" / "jsm").rglob("*.js")):
            rel = f.relative_to(pkg / "examples" / "jsm").as_posix()
            addons[rel] = sorted(export_names(f.read_text(errors="ignore")))
    doc = {"three": THREE_PIN, "generated_by": "test/gen_three_exports.py",
           "modules": surface, "addons": addons}
    OUT.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}: " + ", ".join(f"{k} {len(v)}" for k, v in surface.items())
          + f", addons {len(addons)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
