ALLOWED = {
    'new': {'confirmed', 'ignored'},
    'confirmed': {'in_progress', 'ignored'},
    'in_progress': {'fixed', 'ignored'},
    'fixed': {'reopened'},
    'ignored': {'reopened'},
    'reopened': {'in_progress', 'ignored'},
}


def validate_transition(current_state: str, new_state: str) -> bool:
    return new_state in ALLOWED.get(current_state, set())
