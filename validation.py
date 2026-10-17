import json
ALLOWED_CATEGORY={"delay","damaged","missing","billing","other"}
ALLOWED_PRIORITY={"P1","P2","P3","P4"}
REQUIRED={"category","priority","summary","needs_human"}

def validate(raw):
    data=json.loads(raw) if isinstance(raw,str) else raw
    assert isinstance(data,dict)
    assert set(data)==REQUIRED
    assert data["category"] in ALLOWED_CATEGORY
    assert data["priority"] in ALLOWED_PRIORITY
    assert isinstance(data["summary"],str) and 0 < len(data["summary"].split()) <= 25
    assert isinstance(data["needs_human"],bool)
    return True
