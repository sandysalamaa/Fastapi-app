from sqlalchemy import select
from app.models.audit_log import AuditLog
from datetime import datetime, date

async def get_audit_logs(db, org_id: int):
    result = await db.execute(
        select(AuditLog).where(AuditLog.org_id == org_id)
    )

    return result.scalars().all()



async def get_today_logs(db, org_id: int):
    today = date.today()

    result = await db.execute(
        select(AuditLog).where(
            AuditLog.org_id == org_id,
            AuditLog.created_at >= datetime(today.year, today.month, today.day)
        )
    )

    return result.scalars().all()