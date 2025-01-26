# pyright: basic

from __future__ import annotations

import errno
import os, shutil
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
        return float(f"{self.major}{self.minor}")

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}"


def main():
    raw_versions: list[tuple[Path, VersionInfo]] = []
    for folder in root.iterdir():
        if not folder.is_dir():
            continue
        if folder.name.startswith("coverage_report_"):
            version = VersionInfo.from_str(folder.name.removeprefix("coverage_report_"))
            raw_versions.append((folder, version))
        else:
            try:
                version = VersionInfo.from_str(folder.name)
            except ValueError:
                pass
            else:
                print(f"Deleting {folder}")
                shutil.rmtree(folder)

    for folder, ver in raw_versions:
        folder.rename(root / str(ver))
        print(f"Renamed {folder.name} to {ver} @ folder")

    versions = sorted(
        [ver for _, ver in raw_versions], key=lambda ver: ver.to_float(), reverse=True
    )
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
