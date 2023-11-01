# Import the necessary dependencies
from flask import Flask, jsonify
import datetime as dt
from dateutil.relativedelta import relativedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

# Create a Flask app
app = Flask(__name__)

# Create an engine to connect to the SQLite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect the database and create a base
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create references to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a session to interact with the database
session = Session(engine)

# Define your routes

# Route 1: Homepage
@app.route('/')
def home():
    return (
        f"Welcome to the Climate App API!<br/><br/>"
        f"Available Routes:<br/>"
        f"<a href='/api/v1.0/precipitation'>/api/v1.0/precipitation</a>: Precipitation data for the last 12 months.<br/>"
        f"<a href='/api/v1.0/stations'>/api/v1.0/stations</a>: List of weather stations.<br/>"
        f"<a href='/api/v1.0/tobs'>/api/v1.0/tobs</a>: Temperature observations from the most active station for the last year.<br/>"
        f"/api/v1.0/&lt;start&gt;: Min, Max, and Avg temperature for dates starting from the specified date.<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;: Min, Max, and Avg temperature for a date range.<br/>"
    )

# Route 2: Precipitation Data
@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year ago from the most recent data point
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - relativedelta(years=1)

    # Query to retrieve the precipitation data for the last year
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Create a dictionary of date as the key and precipitation as the value
    prcp_dict = {date: prcp for date, prcp in prcp_data}

    return jsonify(prcp_dict)

# Route 3: List of Stations
@app.route('/api/v1.0/stations')
def stations():
    # Query to retrieve a list of stations
    station_data = session.query(Station.station, Station.name).all()
    stations_list = [{"station": station, "name": name} for station, name in station_data]

    return jsonify(stations_list)

# Route 4: Temperature Observations for the Most Active Station (USC00519281)
@app.route('/api/v1.0/tobs')
def tobs():
    # Calculate the date one year ago from the most recent data point
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    last_date = dt.datetime.strptime(last_date, '%Y-%m-%d')
    one_year_ago = last_date - relativedelta(years=1)

    # Query to retrieve temperature observations for the most active station for the last year
    tobs_data = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == 'USC00519281',
        Measurement.date >= one_year_ago
    ).all()

    # Create a list of dictionaries with date and temperature observations
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)

# Route 5: Min, Max, and Avg Temperatures for a Date Range
@app.route('/api/v1.0/<start>/<end>')
def temp_stats_date_range(start, end):
    # Convert start and end date parameters to datetime objects
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')
    end_date = dt.datetime.strptime(end, '%Y-%m-%d')

    # Query to retrieve temperature statistics for the date range
    temp_stats = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.max(Measurement.tobs).label('max_temp'),
        func.avg(Measurement.tobs).label('avg_temp')
    ).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    # Create a dictionary for the temperature statistics
    temp_stats_dict = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
        'min_temp': temp_stats[0].min_temp,
        'max_temp': temp_stats[0].max_temp,
        'avg_temp': temp_stats[0].avg_temp
    }

    return jsonify(temp_stats_dict)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
