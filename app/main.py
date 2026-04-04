from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import user, record, refresh_token  # noqa: F401
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.records import router as records_router
from app.routers.dashboard import router as dashboard_router

app = FastAPI(
    title="Finance Backend API",
    description="""
    A finance dashboard backend supporting role-based access control,
    financial record management, and aggregated analytics.
    
    ## Roles
    - **Admin** — Full access to records and user management
    - **Analyst** — Read access to records and dashboard insights  
    - **Viewer** — Dashboard summary access only
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(records_router)
app.include_router(dashboard_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Check if the API is running."""
    return {"status": "ok"}