from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func


# connect to the database
# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)


# Save references to each table
measurement = Base.classes.measurement

Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine) 

app = Flask(__name__)

# home route
@app.route("/")

def home():
    return(
        f"<h2>Welcome to the Hawaii Climate Analysis Local API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/end"
    )

# /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precip():
    # return the previous year's precipitation as a json
    # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #previousYear

# Perform a query to retrieve the data and precipitation scores
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= previousYear).all()

    session.close()
    #dictionary with date as the key and the precipitation (prcp) as the value
    precipitation = {date: prcp for date, prcp in results}
    # convert to a json
    return jsonify(precipitation)

# /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    # show a list of stations
    # Perform a query to retrieve the names of the stations
    results = session.query(Station.station).all()
    session.close()
    
    stationList = list(np.ravel(results))

    # convert to a json and display
    return jsonify(stationList)

# /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def temperature():
    # return the previous year temperatures
     # Calculate the date one year from the last date in data set.
    previousYear = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    #previousYear

# Perform a query to retrieve the temperature from the most active station from the past year
    results = session.query(measurement.date, measurement.tobs).\
            filter(measurement.station == 'USC00519281').\
            filter(measurement.date >= previousYear).all()

    session.close()

    temperatureList = list(np.ravel(results))

    # return the list of temperatures 
    return jsonify(temperatureList)

# /api/v1.0/start/end and /api/v1.0/start routes
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):

    # select statement
    selection = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]

    if not end:
        startDate = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*selection).filter(measurement.date >= startDate).all()

        session.close()

        temperatureList = list(np.ravel(results))

        # return the list of temperatures 
        return jsonify(temperatureList)

    else:

        startDate = dt.datetime.strptime(start, "%m%d%Y")
        endDate = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*selection)\
            .filter(measurement.date >= startDate)\
            .filter(measurement.date <= endDate).all()

        session.close()

        temperatureList = list(np.ravel(results))

        # return the list of temperatures 
        return jsonify(temperatureList)

## app launcher

if __name__ == '__main__':
    app.run(debug=True)