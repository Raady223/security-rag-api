from app.tools import get_technique, run_tool


def test_finds_technique(db):
    result = get_technique(db, "T1110.003")
    assert result["name"] == "Password Spraying"
    assert result["tactic"] == "Credential Access"


def test_normalises_id(db):
    assert get_technique(db, "  t1486 ")["name"] == "Data Encrypted for Impact"


def test_unknown_id_returns_error_not_exception(db):
    assert get_technique(db, "T9999") == {"error": "technique T9999 not found"}


def test_rejects_malformed_id(db):
    assert "invalid technique id" in get_technique(db, "1; DROP TABLE techniques")["error"]


def test_unknown_tool_is_refused(db):
    assert run_tool(db, "delete_everything", {}) == {"error": "unknown tool: delete_everything"}
