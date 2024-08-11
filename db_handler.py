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
    conn = connect("data")

    with conn:
        conn.execute("""INSERT INTO leaderboard (tag, score)
                     VALUES (?, ?)""", (tag, score))

    conn.close()
