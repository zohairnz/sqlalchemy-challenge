# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from dateutil.relativedelta import relativedelta

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


#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

#Task 1
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start date in YYYY-MM-DD fortmat]<br/>"
        f"/api/v1.0/[start date in YYYY-MM-DD fortmat]/[end date in YYYY-MM-DD fortmat]<br/>"
    )

#Task 2
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the data set.
    date_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    
    # Calculate the date one year from the last date in data set.
    d = dt.datetime.strptime(date_recent, "%Y-%m-%d")
    last_date = d.date() - relativedelta(years=1)
    
    # Perform a query to retrieve the data and precipitation scores
    data = session.query(Measurement.date, Measurement.prcp).\
                    filter(func.strftime("%Y-%m-%d", Measurement.date) >= last_date).\
                    all()
    
    # Store the precipitation data in an empty list with every row as dictionary
    precipitation_data = []
    for date, prcp in data:
        prcp_data = {}
        prcp_data[date] = prcp
        precipitation_data.append(prcp_data)
    
    # Close Session
    session.close()
    
    return jsonify(precipitation_data)

#Task 3
@app.route("/api/v1.0/stations")
def stations():
    
     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query all stations
    sel = [Station.station,
       Station.name,
       Station.latitude,
       Station.longitude,
       Station.elevation]
    stations_all = session.query(*sel).all()
    
    # Store all the stations information in an empty list
    stations = []
    for station, name, latitude, longitude, elevation in stations_all:
        station_data = {}
        station_data['station'] = station
        station_data['name'] = name
        station_data['latitude'] = latitude
        station_data['longitude'] = longitude
        station_data['elevation'] = elevation
        
        stations.append(station_data)
        
    # Close Session
    session.close()
        
    return jsonify(stations)

#Task 4
@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the data set.
    date_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    
    # Calculate the date one year from the last date in data set.
    d = dt.datetime.strptime(date_recent, "%Y-%m-%d")
    last_date = d.date() - relativedelta(years=1)

    # Perform a query to retrieve the data for station USC00519281 and its temperature for last 12 months
    data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == 'USC00519281').\
                    filter(func.strftime("%Y-%m-%d", Measurement.date) >= last_date).\
                    all()
    
    # Store the temperature data in an empty list with every row as dictionary
    temperature_data = []
    for date, tobs in data:
        temp_data = {}
        temp_data[date] = tobs
        temperature_data.append(temp_data)
    
    # Close Session
    session.close()
    
    return jsonify(temperature_data)

#Task 5
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def range(start, end=None):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Create an empty dict to store the highest, lowest and average temperature for the given date(s)
    result = {}
    
    # Create a list of elements which will be returned from the query
    sel = [func.min(Measurement.tobs),
           func.max(Measurement.tobs),
           func.avg(Measurement.tobs)]
    
    # Check if end date is provided 
    if end == None:
        
        # Create a query to find the highest, lowest and average temperature with a given start date
        results = session.query(*sel).\
                            filter(Measurement.date >= start).\
                            all()
        
    else:
        
        # Create a query to find the highest, lowest and average temperature with a given date range
        results = session.query(*sel).\
                            filter(Measurement.date >= start).\
                            filter(Measurement.date <= end).\
                            all()
        
    # Close Session
    session.close()
    
    # Save the results in a dictionary
    result['Lowest Temperature'] = results[0][0]
    result['Highest Temperature'] = results[0][1]
    result['Average Temperature'] = results[0][2]
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)