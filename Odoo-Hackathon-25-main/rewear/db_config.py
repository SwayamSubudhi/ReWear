import psycopg2

def connect():
    conn = psycopg2.connect(
        dbname="rew_community",
        user="postgres",
        password="himanshu@2005",   # replace with your actual password
        host="localhost",
        port="5432"
    )
    return conn