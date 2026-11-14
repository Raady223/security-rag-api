"""The one tool the model may call: a read-only lookup in the techniques table."""

import json
import re
from pathlib import Path

from google.genai import types
from sqlalchemy.orm import Session

from app.models import Technique

TECHNIQUE_ID = re.compile(r"^T\d{4}(\.\d{3})?$")  # T1110 or T1110.003

# What the model sees: name, description, and a JSON schema for the arguments.
GET_TECHNIQUE = types.FunctionDeclaration(
    name="get_technique",
    description=(
        "Look up a MITRE ATT&CK technique by its ID and return its official "
        "name, tactic and a short description."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "technique_id": {
                "type": "string",
                "description": "ATT&CK technique ID, e.g. T1110 or T1110.003",
            }
        },
        "required": ["technique_id"],
    },
)


def get_technique(db: Session, technique_id: str) -> dict:
    """The real Python function behind the declaration. SELECT only, never writes."""
    tid = str(technique_id).strip().upper()
    if not TECHNIQUE_ID.match(tid):  # model output is untrusted input: validate it
        return {"error": f"invalid technique id: {technique_id!r}"}
    row = db.get(Technique, tid)
    if row is None:
        return {"error": f"technique {tid} not found"}
    return {"technique_id": row.technique_id, "name": row.name,
            "tactic": row.tactic, "description": row.description}


def run_tool(db: Session, name: str, args: dict) -> dict:
    """Dispatch a function call from the model to our code. Unknown names are refused."""
    if name == "get_technique":
        return get_technique(db, args.get("technique_id", ""))
    return {"error": f"unknown tool: {name}"}


def seed_techniques(db: Session) -> None:
    """Load the techniques table from JSON. Upsert, so it is safe on every startup."""
    data = json.loads((Path(__file__).parent / "seed" / "techniques.json").read_text())
    for item in data:
        db.merge(Technique(**item))
    db.commit()
