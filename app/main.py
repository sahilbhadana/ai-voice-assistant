from fastapi import FastAPI
from app.api.routes import router
from app.db.database import engine, Base
from app.api.ai_routes import router as ai_router
from app.api.ai_booking_routes import router as ai_booking_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Voice Assistant API is running"}

app.include_router(router)
app.include_router(ai_router)
app.include_router(ai_booking_router)