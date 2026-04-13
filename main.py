from fastapi import FastAPI
import pymysql
from pymysql.cursors import DictCursor
from app.middleware.tenant import TenantIsolationMiddleware
from app.routers import appointments, auth, billing, clinical, diagnoses, imaging, lab, patients, prescriptions, referrals, vital_signs, wa

app = FastAPI()
app.add_middleware(TenantIsolationMiddleware)

app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(appointments.router)
app.include_router(clinical.router)
app.include_router(diagnoses.router)
app.include_router(vital_signs.router)
app.include_router(prescriptions.router)
app.include_router(lab.router)
app.include_router(imaging.router)
app.include_router(referrals.router)
app.include_router(billing.router)
app.include_router(wa.router)

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
