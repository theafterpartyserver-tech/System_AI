# Run this to add discovery command to main.py
import sys
sys.path.insert(0, '.')
from core.discovery_engine import DiscoveryEngine
from pathlib import Path

engine = DiscoveryEngine(Path('.'))
engine.discover_all()
print(engine.generate_summary())
