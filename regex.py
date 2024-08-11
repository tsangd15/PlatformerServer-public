import re

# raw regex expression: ^ADD_ENTRY \([A-Z][A-Z][A-Z], [0-9]+\)$

pattern_addentry = re.compile("^ADD_ENTRY \\([A-Z][A-Z][A-Z], [0-9]+\\)$")
pattern_get10 = re.compile("^GET_ENTRIES \\(10\\)$")


def match_addentry(expression):
    """Checks if the given expression matches the ADD_ENTRY regex.
    Format: ADD_ENTRY (x, y)
    where x is a three letter fully capitalised word
    where y is an integer"""
    results = pattern_addentry.fullmatch(expression)

    # results returns None if no match
    # results returns match object if match
    if results is not None:
        return True
    return False


def match_get10(expression):
    """Checks if the given expression matches the GET_ENTRIES regex.
    Format: GET_ENTRIES (10)

    This regex matches exactly. 10 entries is only allowed to be retrieved
    from the database as the leaderboard only displays 10, it doesn't need any
    more than that. This may be altered to allow for a different number of
    entries in future."""
    results = pattern_get10.fullmatch(expression)

    # results returns None if no match
    # results returns match object if match
    if results is not None:
        return True
    return False
