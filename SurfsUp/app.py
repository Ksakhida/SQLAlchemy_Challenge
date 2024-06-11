# Import the dependencies.
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt




#################################################
# Database Setup
#################################################


# Create the database connection
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################

# Create the Flask app
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
     

    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.date(2017, 8 ,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).all()

    session.close()

    # Create a dictionary from the row data and append to a list
    precipitation_dict = {str(date): prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_dict)


# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    
    # Perform a query to retrieve all the stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(results))

    return jsonify(stations_list)


# # Define the tobs route
@app.route("/api/v1.0/tobs")
def tobs():

    # Calculate the date 1 year ago from the last data point in the database
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)


   # Query the dates and temperature observations of the most-active station for the previous year of data
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= query_date).all()

    session.close()

  # Convert the query results to a list of dictionaries
    tobs_list =[]
    for date, tobs in results:
        tobs_list.append({date: tobs})

    return jsonify(tobs_list)

   
# Define the start route
@app.route("/api/v1.0/<start>")
def start(start):
    
    #  Date format this api point expects as user input.
    start = dt.datetime.strptime(start, "%Y-%m-%d")

    # Query the min, max, and average temperatures for all dates >= start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary from the row data
    temp_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }

    return jsonify(temp_dict)
    

# Define the start/end route
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    #  Date format this api point expects as user input.
    start = dt.datetime.strptime(start, "%Y-%m-%d")
    end = dt.datetime.strptime(end, "%Y-%m-%d")

    # Query the min, max, and average temperatures for dates between start and end
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # Create a dictionary from the row data
    temp_dict = {
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }

    return jsonify(temp_dict)



if __name__ == "__main__":
    app.run(debug=True)
