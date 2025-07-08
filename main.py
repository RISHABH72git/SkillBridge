import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
import models
from database import engine
from routes import router

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")
    os.makedirs("uploads/pdfs", exist_ok=True)
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    yield  # control passes to FastAPI app
    print("Shutting down application...")


# Create app with lifespan
app = FastAPI(lifespan=lifespan)
app.include_router(router)
