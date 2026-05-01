import os
from pathlib import Path

def list_dir(path: str) -> dict:
    try:
        p = Path(path)
        if not p.exists():
            return {"error": f"Path not found: {path}"}
        if not p.is_dir():
            return {"error": f"Not a directory: {path}"}
        items = []
        for item in sorted(p.iterdir()):
            kind = "dir" if item.is_dir() else "file"
            items.append({"name": item.name, "type": kind})
        return {"path": str(path), "items": items, "count": len(items)}
    except Exception as e:
        return {"error": str(e)}
