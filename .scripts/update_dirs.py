# pyright: basic

from __future__ import annotations

import errno
import os
import re
from pathlib import Path
from typing import Literal, NamedTuple

import jinja2

scripts_dir = Path(__file__).parent
root = scripts_dir.parent

index_fp = root / "index.html"


class VersionInfo(NamedTuple):
    major: int
    minor: int

    @classmethod
    def from_str(cls, raw: str) -> VersionInfo:
        major, minor = raw.split(".")
        return cls(
            major=int(major),
            minor=int(minor),
        )

    def to_float(self) -> float:
        return float(
            f"{self.major}{self.minor}"
        )

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"

def main():
    unsorted_versions = []
    for folder in root.iterdir():
        if folder.is_dir() and folder.name.startswith("coverage_report_"):
            version = VersionInfo.from_str(folder.name.removeprefix("coverage_report_"))
            folder.rename(root / str(version))
            print(f"Renamed {folder.name} to {version} @ {folder}")
            unsorted_versions.append(version)

    versions = sorted(unsorted_versions, key=lambda ver: ver.to_float(), reverse=True)
    print(f"Versions: {', '.join([str(v) for v in versions])}")
    
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(scripts_dir))
    template = env.get_template("template.html")
    code = template.render(versions=versions)

    with index_fp.open("w", encoding="UTF-8") as f:
        f.write(code)

    print(f"Wrote to {index_fp!r}")
    print(code)


if __name__ == "__main__":
    main()
