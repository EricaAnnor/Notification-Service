from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .routers import register,notifications

@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(register)
app.include_router(notifications)




@app.get("/start")
async def start():
    return {"messsage":"welcome"}
