from db.session import SessionLocal
from sqlalchemy import text

def kill_my_idle_tx():
    db = SessionLocal()
    try:
        # Terminate all idle-in-transaction sessions FOR THE CURRENT DATABASE USER
        # This is allowed in many managed DBs even without SUPERUSER
        query = text("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE state = 'idle in transaction'
              AND usename = CURRENT_USER
              AND pid <> pg_backend_pid()
        """)
        results = db.execute(query).fetchall()
        print(f"Force terminated {len(results)} of your own idle sessions.")
        
        # Check active locks
        query2 = text("""
            SELECT count(*) FROM pg_locks WHERE NOT granted
        """)
        res2 = db.execute(query2).scalar()
        print(f"Outstanding ungranted locks: {res2}")
        
        db.commit()
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    kill_my_idle_tx()
