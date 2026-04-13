from fastapi import FastAPI
import pymysql
from pymysql.cursors import DictCursor

app = FastAPI()

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='rootroot',
        database='salvio_tenant_template',
        cursorclass=DictCursor
    )

@app.get("/")
def root():
    return {"message": "Salvio API running", "status": "ok"}

@app.get("/tables")
def list_tables():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
    conn.close()
    return {"tables": [list(t.values())[0] for t in tables]}