# main.py
# The heart of the backend — FastAPI app configuration and startup

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models  # Import models so SQLAlchemy registers them before creating tables

# ─── Create all database tables on startup ───
# This is safe to call repeatedly — it only creates tables if they don't exist
Base.metadata.create_all(bind=engine)

# ─── Initialize FastAPI app ───
app = FastAPI(
    title="Helping Hands API",
    description="Connecting elderly people with volunteers for daily assistance",
    version="1.0.0",
    docs_url="/docs",        # Swagger UI — visit http://localhost:8000/docs to test APIs
    redoc_url="/redoc",
)

# ─── CORS Middleware ───
# This allows the frontend (running on a different port) to call the backend
# In production, replace "*" with your actual frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # e.g. ["https://your-app.netlify.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Register all route modules ───
from routers import users, requests
app.include_router(users.router)
app.include_router(requests.router)


# ─── Health check endpoint ───
@app.get("/")
def root():
    return {
        "message": "🤝 Helping Hands API is running!",
        "docs": "/docs",
        "status": "healthy"
    }


# ─── Run directly with: python main.py ───
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
