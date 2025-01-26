from pathlib import Path

root = Path(__file__).parent.parent
badges_dir = root / "badges"
badges_dir.mkdir(exist_ok=True)

for folder in root.iterdir():
    if not folder.name.startswith("coverage-badge"):
        continue

    version = folder.name.removeprefix("coverage-badge-").removesuffix(".svg")
    actual_file = folder / "coverage.svg"
    new_file = badges_dir / f"{version}.svg"
    new_file.write_bytes(actual_file.read_bytes())

    actual_file.unlink(missing_ok=True)
    folder.rmdir()