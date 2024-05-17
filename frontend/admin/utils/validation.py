def validate_id(node_id: str) -> bool:
    lower = lambda c: c.isalpha() and c.islower()
    allowed = lambda c: lower(c) or c.isdigit() or c == "-"

    for i, c in enumerate(node_id):
        if i == 0 and not lower(c):
            return False

        if not allowed(c):
            return False

    return True
