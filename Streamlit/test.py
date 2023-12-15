import psycopg2

# Replace these with your database credentials
db_host = 'final-project.cg4vo6ofeasg.us-east-1.rds.amazonaws.com'  # e.g., mydbinstance.c6c4d1abcdef.us-east-1.rds.amazonaws.com
db_name = 'final_project'
db_user = 'postgres'
db_password = 'postgres'


try:
    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=5432  # Default PostgreSQL port is 5432
    )
    cursor = conn.cursor()
    print("Connected to the database!")
except Exception as e:
    print(f"Error: {e}")


create_table_query = """
CREATE TABLE IF NOT EXISTS patient (
    id serial PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    age INT,
    has_insurance BOOLEAN,
    insurance VARCHAR(255),
    gender VARCHAR(10),
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255)
);
"""

try:
    cursor.execute(create_table_query)
    conn.commit()
    print("Table 'patient' created successfully!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")

create_table_query = """
CREATE TABLE IF NOT EXISTS doctor (
    id serial PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    practice VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255)
);
"""

try:
    cursor.execute(create_table_query)
    conn.commit()
    print("Table 'doctor' created successfully!")
except Exception as e:
    conn.rollback()
    print(f"Error: {e}")


SQL_QUERY = '''
SELECT * FROM doctor;
'''
cursor.execute(SQL_QUERY)
print(cursor.fetchall())


SQL_QUERY = '''
SELECT * FROM patient;'''
cursor.execute(SQL_QUERY)
print(cursor.fetchall())