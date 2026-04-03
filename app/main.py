from fastapi import FastAPI

from app.models import user, record, refresh_token  # noqa: F401


from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.records import router as records_router

app = FastAPI(
    title="Finance Backend",
    description="Finance data processing and access control API",
    version="1.0.0",
)




@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(records_router)