import re

import mysql.connector

from ..config import settings
from ..utils.logger import get_logger

logger = get_logger("database")


def _safe_db_name() -> str:
    """SQL-injection safe: sirf alphanumeric + underscore allowed."""
    if not re.fullmatch(r"[A-Za-z0-9_]+", settings.MYSQL_DB):
        raise ValueError(f"Unsafe MySQL database name: {settings.MYSQL_DB}")
    return settings.MYSQL_DB


def get_conn():
    return mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=_safe_db_name(),
    )


def init_db():
    from . import models
    name = _safe_db_name()
    conn = mysql.connector.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
    )
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS `{name}`")
    cur.execute(f"USE `{name}`")
    cur.execute(models.INCIDENTS_TABLE)
    cur.execute(models.DAILY_STATS_TABLE)
    cur.execute(models.ALERT_COOLDOWNS_TABLE)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"MySQL database ready: {name}")


def insert_incident(incident: dict, frame_url: str = None) -> bool:
    try:
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
        return True
    except Exception as e:
        logger.error(f"insert_incident failed: {e}")
        return False


def fetch_incidents(limit: int = 50):
    try:
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
    except Exception as e:
        logger.error(f"fetch_incidents failed: {e}")
        return []


def upsert_daily_stats(stats: dict) -> bool:
    try:
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
        return True
    except Exception as e:
        logger.error(f"upsert_daily_stats failed: {e}")
        return False


def fetch_trends(days: int = 7):
    """DONO trends same date-range (last N days) use karte hain."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT stat_date, total_workers, compliant_workers FROM daily_stats "
            "WHERE stat_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY) ORDER BY stat_date",
            (days,),
        )
        comp_rows = cur.fetchall()
        cur.execute(
            "SELECT DATE(created_at), SUM(type='PPE'), SUM(type='FIRE'), SUM(type='SMOKE') "
            "FROM incidents WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY) "
            "GROUP BY DATE(created_at) ORDER BY DATE(created_at)",
            (days,),
        )
        inc_rows = cur.fetchall()
        cur.close()
        conn.close()
        return {
            "complianceTrend": [
                {"day": d.strftime("%a"), "value": round(c / t * 100) if t else 0}
                for (d, t, c) in comp_rows
            ],
            "incidentTrend": [
                {"day": d.strftime("%a"), "ppe": int(p or 0), "fire": int(f or 0), "smoke": int(s or 0)}
                for (d, p, f, s) in inc_rows
            ],
        }
    except Exception as e:
        logger.error(f"fetch_trends failed: {e}")
        return {"complianceTrend": [], "incidentTrend": []}


def get_cooldown(key: str):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT last_seen FROM alert_cooldowns WHERE ckey=%s", (key,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        return float(row[0]) if row else None
    except Exception as e:
        logger.error(f"get_cooldown failed: {e}")
        return None


def set_cooldown(key: str, ts: float) -> None:
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO alert_cooldowns (ckey, last_seen) VALUES (%s,%s) "
            "ON DUPLICATE KEY UPDATE last_seen=VALUES(last_seen)",
            (key, ts),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"set_cooldown failed: {e}")