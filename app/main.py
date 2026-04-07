from fastapi import FastAPI
from app.api.routes import router
from app.db.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI Voice Assistant API is running"}

app.include_router(router)