import mysql.connector

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger("database")


def get_conn():
    return mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DB,
    )


def init_db():
    """Database + table dono auto-create karta hai."""
    from . import models
    conn = mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DB}")
    cur.execute(f"USE {settings.MYSQL_DB}")
    cur.execute(models.SCHEMA)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"MySQL database ready: {settings.MYSQL_DB}")


def insert_incident(incident: dict, frame_url: str = None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO incidents (type, severity, message, camera, zone, worker_id, frame_url) "
        "VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (incident.get("type"), incident.get("severity"), incident.get("message"),
         incident.get("camera"), incident.get("zone"), incident.get("worker_id"), frame_url),
    )
    conn.commit()
    cur.close()
    conn.close()


def fetch_incidents(limit: int = 50):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, type, severity, message, camera, zone, created_at "
        "FROM incidents ORDER BY id DESC LIMIT %s",
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": i, "type": t, "severity": sev, "message": msg,
            "camera": cam, "zone": zone,
            "time": str(created)[11:16] if created else "—",
        }
        for (i, t, sev, msg, cam, zone, created) in rows
    ]