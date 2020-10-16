# add dependencies
from flask import Flask
from flask import jsonify

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String, Float, and_, Date, desc, func

import pandas as pd
import os
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import time



# database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables    
Base.prepare(engine, reflect=True)


measurement = Base.classes.measurement
station = Base.classes.station


#flask setup
app = Flask(__name__)

# Define homepage
@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations <br/>"
        f"/api/v1.0/tobs <br/>"
        f"/api/v1.0/<start> <br/>"
        f"/api/v1.0/<start>/<end>"
    )
# preciptiation route
#Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
@app.route("/api/v1.0/precipitation")
def precipitationdata():
    """Return a list of precipitation by date"""
    
    session = Session(engine)
    results = session.query(measurement.prcp, measurement.date).all()

    # close the session to end the communication with the database
    session.close()

    #Return the JSON representation of your dictionary.
    prcp_results = {val:key for (key,val) in results}

    # print(prcp_results)
    return jsonify(prcp_results)


#Return a JSON list of stations from the dataset.@app.route("/api/v1.0/stations")
@app.route('/api/v1.0/stations')
def stationdata():
    """Return a list of all stations"""
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()
    #print(results)
    station_results = list(np.ravel(results))
    #print(station_results)
    return jsonify(station_results)

#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def active_station():
    """Return information of most active station"""
    #start_date = dt.date(2015, 7, 8)
    session = Session(engine)
    end_date = dt.date(2015, 7, 18)
    last_year = end_date - dt.timedelta(365)
    high_activity = 'USC00511918'
    #active_stations = session.query(measurement.station, func.count(measurement.date)).group_by(measurement.station)
    
    highactivestation_yrtemp = session.query(measurement.date, measurement.tobs).filter(and_(measurement.date<=end_date, measurement.date>=last_year),measurement.station ==high_activity).all()
    session.close()
    act_results = list(np.ravel(highactivestation_yrtemp))
    #print(station_results)
    return jsonify(act_results)

#start route
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_date(start):    
    session = Session(engine)
    print(f"\n\n\nincoming start: {start}")
    print(f"type: {type(start)}\n\n\n")
    starttemp_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).all()
    session.close()
    return jsonify(starttemp_data)

#start and end route
#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def range_date(start,end):
    session = Session(engine)
    stendtemp_data = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(and_(measurement.date >= start, measurement.date <= end)).all()
    session.close()
    return jsonify(stendtemp_data)

if __name__ == "__main__":
    app.run(debug=True)