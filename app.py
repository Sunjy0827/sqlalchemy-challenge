# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



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
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")

def precipitation():
    the_most_recent_date = session.query(Measurement.date).order_by((Measurement.date).desc()).first()
    conv_the_most_recent_date = dt.datetime.strptime(the_most_recent_date[0], '%Y-%m-%d')
    one_year_ago = conv_the_most_recent_date - dt.timedelta(days=366)
    precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")

def stations():
    station_query = session.query(Station.station).all()
    stations = list(np.ravel(station_query))
    return jsonify(stations=stations)


@app.route("/api/v1.0/tobs")

def temp_monthly():
    the_most_recent_date = session.query(Measurement.date).order_by((Measurement.date).desc()).first()
    conv_the_most_recent_date = dt.datetime.strptime(the_most_recent_date[0], '%Y-%m-%d')
    one_year_ago = conv_the_most_recent_date - dt.timedelta(days=366)
    tob_query = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= one_year_ago).all()
    temps = list(np.ravel(tob_query))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
        sel = [func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)]
        
        if not end:
            results = session.query(*sel).filter(Measurement.date <= start).all()
            temps = list(np.ravel(results))
            return jsonify(temps)
        
        results = session.query(*sel).filter(Measurement.date >= start, Measurement.date <= end).all
        temps = list(np.ravel(results))
        return jsonify(temps=temps)

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)