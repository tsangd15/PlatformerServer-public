"""Database Handler Module"""
import sqlite3


class Database():
    def __init__(self, db_name) -> None:
        self.conn = sqlite3.connect(f"{db_name}.db")

    # def add_table(self):
        # """Add a table to the database."""
        # try:
        #     with self.conn:
        #         self.conn.execute("""CREATE TABLE leaderboard
        #                           (tag text,
        #                           score integer)""")
        # except sqlite3.ProgrammingError as err:  # catch table already exists
        #     # in event of exception, transaction rolled back
        #     print(f"ProgrammingError: {err}")

        # connection object context manager only commits/rollbacks
        # transactions so it needs to be closed manually
        # self.conn.close()

    def get_top(self, quantity):
        """Return the top x scores from the database (in descending order)."""
        cur = self.conn.cursor()
        with self.conn:
            # get the top x scores from leaderboard ordered by score in
            # descending order
            self.conn.execute("""SELECT * FROM leaderboard
                                ORDER BY score DESC
                                LIMIT ?""", (quantity,))

            print(cur.fetchall())

        print(cur.fetchall())
        return cur.fetchall()

    def add_entry(self, tag, score):
        """Add an entry into the leaderboard table."""
        with self.conn:
            self.conn.execute("""INSERT INTO leaderboard (tag, score)
                              VALUES (?, ?)""", (tag, score))

    def close(self):
        """Close the Connection object."""
        self.conn.close()
