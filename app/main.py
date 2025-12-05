from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.summarize_api import router as summarize_router
from app.routes.evaluate_api import router as evaluate_router
from app.routes.export_api import router as export_router

app = FastAPI()

# ========= CORS FIX =========
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # http://localhost:5173
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= ROUTES =========
app.include_router(summarize_router, prefix="/summary")
app.include_router(evaluate_router, prefix="/evaluate")
app.include_router(export_router, prefix="/export")


@app.get("/")
def root():
    return {"status": "running", "message": "Audit Summary AI Backend Ready"}
