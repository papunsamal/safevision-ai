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
    cur.execute(models.INCIDENTS_TABLE)
    cur.execute(models.DAILY_STATS_TABLE)
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
        "SELECT id, type, severity, message, camera, zone, frame_url, created_at "
        "FROM incidents ORDER BY id DESC LIMIT %s",
        (limit,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": i, "type": t, "severity": sev, "message": msg,
            "camera": cam, "zone": zone, "frame_url": furl,
            "time": str(created)[11:16] if created else "—",
        }
        for (i, t, sev, msg, cam, zone, furl, created) in rows
    ]


def upsert_daily_stats(stats: dict):
    """Aaj ke din ka latest analysis snapshot save karo."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO daily_stats (stat_date, total_workers, compliant_workers, "
        "ppe_violations, fire_incidents, smoke_incidents) "
        "VALUES (CURDATE(),%s,%s,%s,%s,%s) "
        "ON DUPLICATE KEY UPDATE total_workers=VALUES(total_workers), "
        "compliant_workers=VALUES(compliant_workers), ppe_violations=VALUES(ppe_violations), "
        "fire_incidents=VALUES(fire_incidents), smoke_incidents=VALUES(smoke_incidents)",
        (stats.get("totalWorkers", 0), stats.get("compliantWorkers", 0),
         stats.get("ppeViolations", 0), stats.get("fireIncidents", 0),
         stats.get("smokeIncidents", 0)),
    )
    conn.commit()
    cur.close()
    conn.close()


def fetch_trends(days: int = 7):
    """REAL reports ke liye MySQL se 7-din ke trends."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT stat_date, total_workers, compliant_workers FROM daily_stats "
        "ORDER BY stat_date DESC LIMIT %s", (days,))
    comp_rows = cur.fetchall()
    cur.execute(
        "SELECT DATE(created_at), SUM(type='PPE'), SUM(type='FIRE'), SUM(type='SMOKE') "
        "FROM incidents WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY) "
        "GROUP BY DATE(created_at) ORDER BY DATE(created_at)", (days,))
    inc_rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "complianceTrend": [
            {"day": d.strftime("%a"), "value": round(c / t * 100) if t else 0}
            for (d, t, c) in reversed(comp_rows)
        ],
        "incidentTrend": [
            {"day": d.strftime("%a"), "ppe": int(p or 0), "fire": int(f or 0), "smoke": int(s or 0)}
            for (d, p, f, s) in inc_rows
        ],
    }