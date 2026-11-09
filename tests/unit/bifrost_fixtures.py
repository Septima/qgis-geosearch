"""Loading the recorded Bifrost exchanges (tests/tools/record_bifrost.py)."""

import json
import os

from geosearch_dk.bifrost import (
    PROPOSED_TYPES,
    TYPES,
    collect_rows,
    membership_from_response,
    plan_search,
)

FIXTURES = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "fixtures", "bifrost"
)


def fixture_names():
    return sorted(f[:-5] for f in os.listdir(FIXTURES) if f.endswith(".json"))


def load(name):
    with open(os.path.join(FIXTURES, name + ".json"), encoding="utf-8") as f:
        return json.load(f)


def plan_for(data):
    case = data["case"]
    types = TYPES + PROPOSED_TYPES if case["proposed"] else TYPES
    return plan_search(
        case["text"], case["selected"], case["kommunefilter"], types=types
    )


def members_for(data, plan):
    """The membership sets the plugin would have built from the recorded pages."""
    members = {t: set() for t in plan.membership_targets}
    for per_target in data["memberships"].values():
        for target, pages in per_target.items():
            for page in pages:
                members[target] |= membership_from_response(page["response"])[0]
    return members


def result_for(name):
    data = load(name)
    plan = plan_for(data)
    responses = [ex["response"] for ex in data["requests"]]
    return collect_rows(plan, responses, members_for(data, plan))
