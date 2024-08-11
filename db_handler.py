"""Database Handler Module"""
import sqlite3


def connect(db_name):
    """Return a database Connection object."""
    conn = sqlite3.connect(f"{db_name}.db")
    return conn


def get_top(quantity):
    """Return the top x scores from the database (in descending order).
    The data is returned as a list of tuples. E.g. [("ABC", 74)]"""
    conn = connect("data")
    cur = conn.cursor()
    with conn:
        # get the top x scores from leaderboard ordered by score in
        # descending order
        cur.execute("""SELECT * FROM leaderboard
                    ORDER BY score DESC
                    LIMIT ?""", (quantity,))

    results = cur.fetchall()

    conn.close()
    return results


def add_entry(tag, score):
    """Add an entry into the leaderboard table."""
    # input validation
    if not(isinstance(tag, str) and isinstance(score, int)):
        raise Exception(f"add_entry: typeerror - tag={type(tag)}, " +
                        f"score={type(score)}")
    elif len(tag) != 3:
        raise Exception("add_entry: tag not 3 characters long")
    elif score < 0:
        raise Exception(f"add_entry: invalid score, {score}")
    elif not(tag.isupper()):
        raise Exception(f"add_entry: tag isn't 100% uppercase, tag={tag}")
    elif not(tag.isalpha()):
        raise Exception(f"add_entry: tag characters not letters, tag={tag}")

    conn = connect("data")

    with conn:
        conn.execute("""INSERT INTO leaderboard (tag, score)
                     VALUES (?, ?)""", (tag, score))

    conn.close()
