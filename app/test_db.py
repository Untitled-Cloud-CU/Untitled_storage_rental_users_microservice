from app.database import engine

def test_connection():
    try:
        conn = engine.connect()
        print("SUCCESS: Connected to Cloud SQL!")
        conn.close()
    except Exception as e:
        print("FAILED:", e)

test_connection()
