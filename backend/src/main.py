# backend/src/main.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
import logging
from core.database import engine, Base, async_session
from core.initial_data import create_initial_data
from fastapi.staticfiles import StaticFiles

# Import Routers
from modules.plan.routers import router as plan_router
from modules.user.routers import router as user_router
from modules.auth.routers import router as auth_router
from modules.admin.routers import router as admin_router
from modules.ai.routers import router as ai_router
from modules.product.routers import router as product_router
from modules.upload.routers import router as upload_router
# Logger setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Secure and Scalable FastAPI Project")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


origins = [settings.FRONTEND_URL]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        await create_initial_data(session)
# Middleware for Exception Handling
@app.middleware("http")
async def exception_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "Internal Server Error"}
        )

# Register Routers
app.include_router(plan_router)
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(product_router)
app.include_router(upload_router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Secure and Scalable FastAPI Project"}
