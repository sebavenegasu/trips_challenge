from fastapi import FastAPI, Depends, WebSocket
from sqlalchemy.orm import Session
from sqlalchemy import text, event
from sqlalchemy.engine import Engine

from . import models, controllers, schemas
from .database import SessionLocal, engine
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi import BackgroundTasks

import asyncio
from .websocket_utils import websocket_endpoint, commit_and_notify


app = FastAPI()

active_connections = set()

app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# WebSocket para notificar cambios
@app.websocket("/ws")
async def websocket_endpoint_wrapper(websocket: WebSocket):
    await websocket_endpoint(websocket)

# startup
@app.on_event("startup")
def startup():
    with SessionLocal() as session:
        models.Base.metadata.create_all(engine)
        session.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    return {"message": "Data loaded successfully"}

# cargar datos de csv
@app.post("/load_csv")
def load_data(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    num_rows = controllers.load_csv('data/trips.csv', db, commit_and_notify)
    # Añade la tarea al fondo de tareas
    background_tasks.add_task(commit_and_notify, db, num_rows) 
    return {"message": "Data loaded successfully"}

@app.post("/load_grouped")
def load_grouped(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    num_rows_grouped = controllers.load_grouped_trips(db, commit_and_notify)
    # Añade la tarea al fondo de tareas
    background_tasks.add_task(commit_and_notify, db, num_rows_grouped)
    return {"message": "Data loaded successfully"}


# mostrar trips agrupados
@app.get("/")
def read_root(db: Session = Depends(get_db)):
    grouped_trips = controllers.read_grouped_trips(db)

    return grouped_trips


# trips normales
@app.get("/trips", response_model=List[schemas.Trip])  # use the schema instead of the model
def get_trips(db: Session = Depends(get_db)):
    return controllers.read_trips(db)

# trips agrupados
@app.get("/grouped_trips", response_model=List[schemas.GroupedTrip])  # use the schema instead of the model
def get_grouped_trips(db: Session = Depends(get_db)):
    return controllers.read_grouped_trips(db)

# promedio semanal
@app.post("/weekly_average", response_model=dict)
def weekly_average(
    request: schemas.WeeklyAverageRequest,
    db: Session = Depends(get_db),
):
    return controllers.get_weekly_average(db, request.min_longitude, request.max_longitude, request.min_latitude, request.max_latitude, request.region)

