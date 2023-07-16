from db import create_connection


def get_next_id(table, column):
    connection = create_connection()
    cursor = connection.cursor()

    query = f"SELECT MAX({column}) FROM {table}"
    cursor.execute(query)

    max_id = cursor.fetchone()[0]

    next_id = int(max_id) + 1 if max_id else 1

    cursor.close()
    connection.close()

    return next_id
