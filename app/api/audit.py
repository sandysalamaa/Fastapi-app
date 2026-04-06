from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import StreamingResponse

from app.db.dependency import get_db
from app.core.rbac import require_role
from app.services.audit_service import get_audit_logs, get_today_logs
from app.services.ai_service import ask_ai, ask_ai_stream 

router = APIRouter(prefix="/organizations/{org_id}/audit-logs", tags=["Audit"])


# to get all logs (admin only)
@router.get("")
async def get_logs(
    org_id: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin"))
):
    logs = await get_audit_logs(db, org_id)

    return [
        {
            "id": log.id,
            "action": log.action,
            "user_id": log.user_id,
            "data": log.extra_data,
            "created_at": log.created_at
        }
        for log in logs
    ]


# to ask AI chatbot (stream + non-stream)
@router.post("/ask")
async def ask_logs(
    org_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_role("admin"))
):
    logs = await get_today_logs(db, org_id)

    # to stream mode
    if data.get("stream"):

        async def generator():
            async for chunk in ask_ai_stream(logs, data["question"]):
                yield chunk

        return StreamingResponse(generator(), media_type="text/plain")

    # to normal mode
    else:
        answer = await ask_ai(logs, data["question"])
        return {"answer": answer}