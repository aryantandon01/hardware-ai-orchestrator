# test_json.py
import json
from src.knowledge.standards_db import ComplianceStandardDoc

# Test one file at a time
with open('src/data/standards/aec_q100.json', 'r') as f:
    data = json.load(f)
    
try:
    doc = ComplianceStandardDoc(**data)
    print("✅ AEC-Q100 JSON is valid!")
    print(doc)
except Exception as e:
    print(f"❌ Validation error: {e}")
