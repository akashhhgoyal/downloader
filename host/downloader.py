import subprocess
import os
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

# Load .env
load_dotenv()

# ================= MYSQL CONNECTION =================

def get_db_connection():

    db_host = os.getenv("DB_HOST")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    if not all([db_host, db_user, db_password, db_name]):
        raise Exception("Database environment variables missing in .env")

    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )


def log_to_db(conversation_id, status, message):

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO download_logs 
        (conversation_id, status, message, created_at)
        VALUES (%s, %s, %s, %s)
        """

        cursor.execute(query, (
            str(conversation_id),
            str(status),
            str(message),
            datetime.now()
        ))

        conn.commit()

        print(f"DB LOG SAVED → {conversation_id} ({status})")

    except Exception as e:
        print("❌ DB Log Error:", str(e))

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


# ================= DOWNLOADER =================

def run_downloader(conversation_id, channel_type):

    try:
        if channel_type == "Single Channel":
            script = "single_channel.py"
        else:
            script = "dual_channel.py"

        command = ["python", "-u", script, str(conversation_id)]

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(timeout=600)
        output = stdout.strip()

        if "SUCCESS:" in output:
            log_to_db(conversation_id, "SUCCESS", output)
            return True, output
        else:
            error_msg = stderr.strip() if stderr else output
            log_to_db(conversation_id, "FAILED", error_msg)
            return False, error_msg

    except subprocess.TimeoutExpired:
        process.kill()
        log_to_db(conversation_id, "TIMEOUT", "Recording took too long")
        return False, "Timeout: recording took too long"

    except Exception as e:
        log_to_db(conversation_id, "ERROR", str(e))
        return False, str(e)
