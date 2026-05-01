from typing import Dict, Any

def tool_noop() -> Dict[str, Any]:
    return {"status": "ok", "message": "No operation performed."}