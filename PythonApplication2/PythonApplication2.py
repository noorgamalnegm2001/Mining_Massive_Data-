
import calendar
from datetime import timedelta, date
import duckdb


def daterange(start_date, end_date):
    for day_number in range((end_date - start_date).days):
        yield start_date + timedelta(days=day_number)


def populate(conn, start, years):
    fo
import calendar
from datetime import date, timedelta
import duckdb


# Create one row for a date
def add_date(conn, day):
    exists = conn.execute(
        "SELECT COUNT(*) FROM isotable WHERE date = ?",
        [day]
    ).fetchone()[0]

    if exists == 0:
        conn.execute("""
            INSERT INTO isotable
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            day,
            day.day,
            int(day.strftime("%j")),
            day.isocalendar()[1],
            day.month,
            day.isocalendar()[2],
            day.year,
            str(day.isocalendar()[0]) + "-"
                + str(day.isocalendar()[1]).zfill(2),
            calendar.isleap(day.year)
        ])


# Create the table
start = int(input("Starting year: "))
years = int(input("Number of years: "))

conn = duckdb.connect("time.duckdb")

conn.execute("DROP TABLE IF EXISTS isotable")

conn.execute("""
    CREATE TABLE isotable (
        date DATE PRIMARY KEY,
        dayofmonth INTEGER,
        dayofyear INTEGER,
        week INTEGER,
        month INTEGER,
        weekday INTEGER,
        year INTEGER,
        yweek VARCHAR(10),
        isleapyear BOOLEAN
    )
""")


# Fill the table with dates
day = date(start, 1, 1)
end = date(start + years, 1, 1)

while day < end:
    add_date(conn, day)
    day = day + timedelta(days=1)


# --------------------------------------------------
# (a) Add the four required dates
# --------------------------------------------------

print("\n(a) Required dates:")

required_dates = [
    date(2019, 12, 31),
    date(2020, 12, 31),
    date(2021, 1, 1),
    date(2027, 1, 1)
]

for day in required_dates:
    add_date(conn, day)

    print(conn.execute("""
        SELECT *
        FROM isotable
        WHERE date = ?
    """, [day]).fetchall())


columns = [
    "date", "dayofmonth", "dayofyear", "week",
    "month", "weekday", "year", "yweek", "isleapyear"
]


# --------------------------------------------------
# (c) Find all single-column functional dependencies
# --------------------------------------------------

print("\n(c) Single-column functional dependencies:")

for A in columns:
    for B in columns:
        if A != B:

            result = conn.execute(f"""
                SELECT COUNT(*)
                FROM (
                    SELECT "{A}"
                    FROM isotable
                    GROUP BY "{A}"
                    HAVING COUNT(DISTINCT "{B}") > 1
                )
            """).fetchone()[0]

            if result == 0:
                print(A, "->", B)


# --------------------------------------------------
# (d) Find all keys containing two columns
# --------------------------------------------------

print("\n(d) Two-column candidate keys:")

for i in range(len(columns)):
    for j in range(i + 1, len(columns)):

        A = columns[i]
        B = columns[j]

        pair_duplicates = conn.execute(f"""
            SELECT COUNT(*)
            FROM (
                SELECT "{A}", "{B}"
                FROM isotable
                GROUP BY "{A}", "{B}"
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]

        A_duplicates = conn.execute(f"""
            SELECT COUNT(*)
            FROM (
                SELECT "{A}"
                FROM isotable
                GROUP BY "{A}"
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]

        B_duplicates = conn.execute(f"""
            SELECT COUNT(*)
            FROM (
                SELECT "{B}"
                FROM isotable
                GROUP BY "{B}"
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]

        if pair_duplicates == 0:
            if A_duplicates > 0 and B_duplicates > 0:
                print("(", A, ",", B, ")")


# --------------------------------------------------
# (e) Find non-key pairs that determine another column
# --------------------------------------------------

print("\n(e) Non-key functional dependencies:")

for i in range(len(columns)):
    for j in range(i + 1, len(columns)):

        A = columns[i]
        B = columns[j]

        pair_duplicates = conn.execute(f"""
            SELECT COUNT(*)
            FROM (
                SELECT "{A}", "{B}"
                FROM isotable
                GROUP BY "{A}", "{B}"
                HAVING COUNT(*) > 1
            )
        """).fetchone()[0]

        if pair_duplicates > 0:

            for C in columns:
                if C != A and C != B:

                    pair_result = conn.execute(f"""
                        SELECT COUNT(*)
                        FROM (
                            SELECT "{A}", "{B}"
                            FROM isotable
                            GROUP BY "{A}", "{B}"
                            HAVING COUNT(DISTINCT "{C}") > 1
                        )
                    """).fetchone()[0]

                    A_result = conn.execute(f"""
                        SELECT COUNT(*)
                        FROM (
                            SELECT "{A}"
                            FROM isotable
                            GROUP BY "{A}"
                            HAVING COUNT(DISTINCT "{C}") > 1
                        )
                    """).fetchone()[0]

                    B_result = conn.execute(f"""
                        SELECT COUNT(*)
                        FROM (
                            SELECT "{B}"
                            FROM isotable
                            GROUP BY "{B}"
                            HAVING COUNT(DISTINCT "{C}") > 1
                        )
                    """).fetchone()[0]

                    if pair_result == 0:
                        if A_result > 0 and B_result > 0:
                            print(A, ",", B, "->", C)

conn.close()
