from sqlalchemy.orm import Session
from . import models
from . import schemas
import csv
from datetime import datetime
from sqlalchemy import func
import re
from geoalchemy2.shape import to_shape
from geoalchemy2.functions import ST_X, ST_Y, ST_MakePoint, ST_SnapToGrid


def read_trips(db):
    db_trips = db.query(models.Trip).all()

    trips = []
    for db_trip in db_trips:
        trip = schemas.Trip(
            id=db_trip.id,
            region=db_trip.region,
            datetime=db_trip.datetime.isoformat(),  # convert datetime to string
            origin_coord=to_shape(db_trip.origin_coord).__geo_interface__,  # convert to GeoJSON
            destination_coord=to_shape(db_trip.destination_coord).__geo_interface__,  # convert to GeoJSON
            datasource=db_trip.datasource
        )
        trips.append(trip)
    return trips

def read_grouped_trips(db):
    db_trips = db.query(models.GroupedTrip).all()

    trips = []
    for db_trip in db_trips:
        trip = schemas.GroupedTrip(
            region=db_trip.region,
            origin_coord=to_shape(db_trip.origin_coord).__geo_interface__,  # convert to GeoJSON
            destination_coord=to_shape(db_trip.destination_coord).__geo_interface__,  # convert to GeoJSON
            time_group=db_trip.time_group,
            average_hour=db_trip.average_hour,
            count=db_trip.count
        )
        trips.append(trip)
    return trips

def load_csv(file_path: str, db: Session, commit_function: callable):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        num_rows = 0

        for row in reader:
            region, origin_coord_str, destination_coord_str, datetime_str, datasource = row
            datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

            # Parse coordinates from strings
            origin_coord = parse_point(origin_coord_str)
            destination_coord = parse_point(destination_coord_str)

            db_trip = models.Trip(
                region=region,
                datetime=datetime_obj,
                origin_coord=func.ST_MakePoint(origin_coord[0], origin_coord[1]),
                destination_coord=func.ST_MakePoint(destination_coord[0], destination_coord[1]),
                datasource=datasource,
            )

            db.add(db_trip)
            num_rows += 1
        commit_function(db, num_rows)
    return num_rows

def load_grouped_trips(db: Session, commit_function: callable):
    num_rows = 0
    results = (
        db.query(
            models.Trip.region,
            ST_X(ST_SnapToGrid(models.Trip.origin_coord, 1)).label('origin_x'),
            ST_Y(ST_SnapToGrid(models.Trip.origin_coord, 1)).label('origin_y'),
            ST_X(ST_SnapToGrid(models.Trip.destination_coord, 1)).label('dest_x'),
            ST_Y(ST_SnapToGrid(models.Trip.destination_coord, 1)).label('dest_y'),
            func.floor(func.extract('hour', models.Trip.datetime) / 2).label('time_group'),
            func.avg(func.extract('hour', models.Trip.datetime)).label('average_hour'),
            func.count(models.Trip.id).label('count')
        )
        .group_by(
            models.Trip.region,
            'origin_x',
            'origin_y',
            'dest_x',
            'dest_y',
            'time_group',
        )
        .all()
    )
    

    grouped_trips = [
        schemas.GroupedTrip(
            region=result.region, 
            origin_coord={'type': 'Point', 'coordinates': [result.origin_x, result.origin_y]},
            destination_coord={'type': 'Point', 'coordinates': [result.dest_x, result.dest_y]},
            time_group=result.time_group,
            average_hour=result.average_hour,
            count=result.count
        )
        for result in results
    ]

    for trip in grouped_trips:
        db_trip = models.GroupedTrip(
            region=trip.region,
            origin_coord='SRID=4326;POINT({} {})'.format(trip.origin_coord.coordinates[0], trip.origin_coord.coordinates[1]),
            destination_coord='SRID=4326;POINT({} {})'.format(trip.destination_coord.coordinates[0], trip.destination_coord.coordinates[1]),
            time_group=trip.time_group,
            average_hour=trip.average_hour,
            count=trip.count
        )
        db.add(db_trip)
        num_rows += 1
    commit_function(db, num_rows)


    return num_rows

def get_weekly_average(db: Session, min_longitude: float, max_longitude: float, min_latitude: float, max_latitude: float, region: str):
    bounding_box = func.ST_MakeEnvelope(min_longitude, min_latitude, max_longitude, max_latitude, 4326)
    results = (
        db.query(
            func.count(models.Trip.id).label("trips_count"), 
            func.extract('week', models.Trip.datetime).label("week")
        )
        .filter(
            models.Trip.region == region,
            func.ST_Within(models.Trip.origin_coord, bounding_box),
            func.ST_Within(models.Trip.destination_coord, bounding_box),
        )
        .group_by(
            func.extract('week', models.Trip.datetime)
        )
        .subquery()
    )

    weekly_average = db.query(func.avg(results.c.trips_count)).scalar()
    return {"weekly average": weekly_average}


def parse_point(point_str):
    # Parse a string in the format "POINT (x y)" and return [x, y]
    match = re.match(r"POINT \(([-0-9.]+) ([-0-9.]+)\)", point_str)
    if match:
        return [float(coord) for coord in match.groups()]
    else:
        raise ValueError(f"Invalid point string: {point_str}")
    
