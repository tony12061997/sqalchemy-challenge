import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Import the dependencies.



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
   
# Query to retrieve the last 12 months of precipitation data
    results = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )

    # Create a dictionary with date as the key and prcp as the value
    precipitation_dict = {date: prcp for date, prcp in results}

    return jsonify(precipitation_dict)

if __name__ == "__main__":
    app.run(debug=True)
   

    
    

@app.route("/api/v1.0/stations")
def stations():
# Query to retrieve all stations
    results = session.query(Station.station).all()

    # Convert the results to a list
    stations_list = [result[0] for result in results]

    # Return the list as JSON
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    #query
    # Find the most active station
    most_active_station = (
        session.query(Measurement.station, func.count(Measurement.station))
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()
    )

    if most_active_station:
        # Extract the station ID
        most_active_station_id = most_active_station[0]

        # Calculate the most recent date
        most_recent_date = session.query(func.max(Measurement.date)).filter_by(station=most_active_station_id).scalar()
        most_recent_date_dt = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')

        # Calculate the date one year ago from the most recent date
        one_year_ago = most_recent_date_dt - dt.timedelta(days=365)

        # Query to retrieve the dates and temperature observations of the most active station for the previous year
        results = (
            session.query(Measurement.date, Measurement.tobs)
            .filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago)
            .all()
        )

        # Create a list of dictionaries with date and tobs
        temperature_data = [{"date": date, "temperature": tobs} for date, tobs in results]

        # Return the list as JSON
        return jsonify(temperature_data)
    else:
        return jsonify({"message": "No data found for the most active station."})

    
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start(start=None,end=None):
   # Convert start and end dates to datetime objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    end_date = dt.datetime.strptime(end, "%Y-%m-%d") if end else None

    # Query to retrieve minimum, average, and maximum temperature for the specified range
    if end_date:
        results = (
            session.query(
                func.min(Measurement.tobs).label("min_temperature"),
                func.avg(Measurement.tobs).label("avg_temperature"),
                func.max(Measurement.tobs).label("max_temperature"),
            )
            .filter(Measurement.date >= start_date, Measurement.date <= end_date)
            .all()
        )
    else:
        results = (
            session.query(
                func.min(Measurement.tobs).label("min_temperature"),
                func.avg(Measurement.tobs).label("avg_temperature"),
                func.max(Measurement.tobs).label("max_temperature"),
            )
            .filter(Measurement.date >= start_date)
            .all()
        )

    # Extract the results
    temp_stats = {
        "min_temperature": results[0].min_temperature,
        "avg_temperature": results[0].avg_temperature,
        "max_temperature": results[0].max_temperature,
    }

    # Return the results as JSON
    return jsonify(temp_stats)



if __name__ == '__main__':
    app.run(debug=True)