from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api import auth ,organization,item,audit


app = FastAPI(title="Multi-Tenant App")


@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(auth.router)
app.include_router(organization.router)
app.include_router(item.router)
app.include_router(audit.router)



