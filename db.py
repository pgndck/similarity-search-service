import psycopg2
from psycopg2 import Error


def create_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            database="similarity_db",
            user="pgndck",
            password="reply.io",
            host="localhost",
            port="5432"
        )
        print("Connection to PostgreSQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection
