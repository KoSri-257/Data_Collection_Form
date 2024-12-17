import logging, uvicorn
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from database import get_db, create_tables
from services import post_info, get_info 
from schema import Create, Response
from platform_table import populate_platform_info
from config import HOST, PORT, LOG_LEVEL
from contextlib import asynccontextmanager

logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()  # Creates tables if they don't exist
    populate_platform_info()  # Populate PlatformInfo table with predefined values
    logger.info("Startup event completed successfully")
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/')
def root():
    return {'message': 'Connection established successfully'}

@app.post("/info_input", response_model=Response, status_code=201)
def info_input(input_data: Create, db: Session = Depends(get_db)):
    response_data = post_info(input_data, db)
    return Response(**response_data, **input_data.model_dump())

@app.get("/info_output/{eid}",status_code=200)
def info_output(eid: str, db: Session = Depends(get_db)):
    response_data = get_info(eid, db)
    return response_data

if __name__ == "__main__":
    logger.info("Starting the API server...")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)
