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
    # if input is valid
    if add_entry_input_validation(tag, score):
        # connect to database
        conn = connect("data")
        cur = conn.cursor()

        with conn:
            # return row with same tag (if it exists)
            existing_row = add_entry_return_rows(cur, tag)

            # if empty, a row with that tag doesn't exist
            if existing_row == []:
                # insert new row with new tag and score
                add_entry_new_row(conn, tag, score)

            # otherwise row with that tag exists
            else:
                # retrieve old score
                old_score = existing_row[0][1]

                # check new score bigger than old score
                if score > old_score:
                    # update row with new score
                    add_entry_update_row(conn, tag, score)

        conn.close()
        return True

    return False


def add_entry_input_validation(tag, score):
    """Carry out input validation on tag and score.
    Returns True if input valid, False if not valid."""
    if not(isinstance(tag, str) and isinstance(score, int)):
        print(f"add_entry: typeerror - tag={type(tag)}, " +
              f"score={type(score)}")
    elif len(tag) != 3:
        print("add_entry: tag not 3 characters long")
    elif score < 0:
        print(f"add_entry: invalid score, {score}")
    elif not tag.isupper():
        print(f"add_entry: tag isn't 100% uppercase, tag={tag}")
    elif not tag.isalpha():
        print(f"add_entry: tag characters not letters, tag={tag}")
    else:
        return True
    return False


def add_entry_return_rows(cur, tag):
    """Query database for rows with the given tag.
    Returns a list of rows in the form of tuples that have the given tag."""
    # query db for any rows with input tag
    cur.execute("""SELECT * FROM leaderboard
                WHERE tag = ?""", (tag,))
    # query result is a list of tuples, each tuple is a row
    # e.g. [("TAG", 45), ("QWE", 67)]
    existing_row = cur.fetchall()  # save query result in variable

    return existing_row


def add_entry_new_row(conn, tag, score):
    """Add a new row to the leaderboard table with the given tag and score."""
    conn.execute("""INSERT INTO leaderboard (tag, score)
                VALUES (?, ?)""", (tag, score))


def add_entry_update_row(conn, tag, score):
    """Update an existing row that has a given tag in the leaderboard table
    with the given score."""
    conn.execute("""UPDATE leaderboard
                    SET score = ?
                    WHERE tag = ?""", (score, tag))
