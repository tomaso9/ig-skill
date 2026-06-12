"""
Session state helper for the ig-code skill.

The state file lives next to the input document: <doc_base>_IG_session.json.
All state reads/writes go through this script so the workflow never embeds
JSON boilerplate in the conversation.

Usage:
    python session.py <doc_path> init
    python session.py <doc_path> get
    python session.py <doc_path> set <key> <value> [<key> <value> ...]

`init` creates the state file with defaults (input_path, input_type, and the
skill version from the VERSION file next to this script).

`set` parses each value as JSON where possible (true/false/null, numbers,
arrays, objects, quoted strings); anything that fails to parse is stored as
a plain string. Examples:

    python session.py doc.pdf set current_step 4
    python session.py doc.pdf set coding_level "IG Extended"
    python session.py doc.pdf set multi_agent_mode true
    python session.py doc.pdf set output_formats '["csv", "ig_parser"]'
    python session.py doc.pdf set batch_config '{"total_statements": 80, "batch_size": 25, "num_batches": 4, "completed_batches": 0}'
"""

import json
import os
import sys

DEFAULT_STATE = {
    "input_path": None,
    "input_type": None,
    "skill_version": None,
    "coding_level": None,
    "output_formats": [],
    "multi_agent_mode": None,
    "compute_metrics": None,
    "selected_metrics": [],
    "statement_list_path": None,
    "current_step": "1",
    "batch_config": None,
}


def state_path(doc_path):
    return os.path.splitext(doc_path)[0] + "_IG_session.json"


def read_version():
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION")
    try:
        with open(version_file, encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "unknown"


def load(doc_path):
    with open(state_path(doc_path), encoding="utf-8") as f:
        return json.load(f)


def save(doc_path, state):
    with open(state_path(doc_path), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def show(state):
    print(json.dumps(state, indent=2))


def cmd_init(doc_path):
    state = dict(DEFAULT_STATE)
    state["input_path"] = doc_path
    state["input_type"] = os.path.splitext(doc_path)[1].lower().lstrip(".")
    state["skill_version"] = read_version()
    save(doc_path, state)
    print(f"Session state initialized: {state_path(doc_path)}")
    show(state)


def cmd_get(doc_path):
    show(load(doc_path))


def cmd_set(doc_path, pairs):
    if len(pairs) % 2 != 0:
        print("ERROR: set requires <key> <value> pairs", file=sys.stderr)
        sys.exit(1)
    state = load(doc_path)
    for key, raw in zip(pairs[0::2], pairs[1::2]):
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            value = raw
        state[key] = value
    save(doc_path, state)
    updated = ", ".join(f"{k}={state[k]!r}" for k in pairs[0::2])
    print(f"State updated: {updated}")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)
    doc_path, command = argv[0], argv[1]
    if command == "init":
        cmd_init(doc_path)
    elif command == "get":
        cmd_get(doc_path)
    elif command == "set":
        cmd_set(doc_path, argv[2:])
    else:
        print(f"ERROR: unknown command {command!r} (expected init/get/set)", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main(sys.argv[1:])
