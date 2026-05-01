"""
Math Skill - Arithmetic and mathematical operations
"""

def calculate_expression(expression: str) -> float:
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)
        return result
    except Exception as e:
        return {"error": str(e)}

def solve_quadratic(a: float, b: float, c: float) -> dict:
    """Solve quadratic equation ax^2 + bx + c = 0"""
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return {"error": "No real solutions"}
    x1 = (-b + discriminant**0.5) / (2*a)
    x2 = (-b - discriminant**0.5) / (2*a)
    return {"x1": x1, "x2": x2}

SKILL_METADATA = {
    "name": "math_skill",
    "version": "1.0.0",
    "description": "Mathematical operations and calculations",
    "functions": ["calculate_expression", "solve_quadratic"],
    "tags": ["math", "science", "education"]
}
