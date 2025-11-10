# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import predictions, analytics, training

app = FastAPI(title="NBA AI Prediction API")

# ✅ Allow your frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://nba-ai.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(predictions.router)
app.include_router(analytics.router)
app.include_router(training.router)

@app.get("/")
def root():
    return {"message": "NBA AI Backend Running"}
