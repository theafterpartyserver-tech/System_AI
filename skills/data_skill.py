"""
Data Skill - Data processing and analysis
"""

def parse_csv_like(data: str, delimiter: str = ',') -> list:
    """Parse CSV-like data"""
    lines = data.strip().split('\n')
    return [line.split(delimiter) for line in lines]

def statistics(numbers: list) -> dict:
    """Calculate statistics for a list of numbers"""
    if not numbers:
        return {"error": "Empty list"}
    n = len(numbers)
    mean = sum(numbers) / n
    variance = sum((x - mean) ** 2 for x in numbers) / n
    std_dev = variance ** 0.5
    return {
        "count": n,
        "sum": sum(numbers),
        "mean": mean,
        "min": min(numbers),
        "max": max(numbers),
        "std_dev": std_dev
    }

SKILL_METADATA = {
    "name": "data_skill",
    "version": "1.0.0",
    "description": "Data processing and statistical analysis",
    "functions": ["parse_csv_like", "statistics"],
    "tags": ["data", "analysis", "statistics"]
}
