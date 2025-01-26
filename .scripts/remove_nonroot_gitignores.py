from pathlib import Path

root = Path(__file__).parent.parent
for file in root.rglob("*.gitignore"):
    print(file)
    if file.parent != root:
        file.unlink()
        print("Removed")