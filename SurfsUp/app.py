from flask import Flask, json, jsonify
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import inspect
import numpy as np

engine = create_engine("sqlite:///./Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def home():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/2016-01-01/<br/>"
        f"/api/v1.0/2016-01-01/2016-12-31/"
    )


@app.route('/api/v1.0/precipitation/')
def precipitation():
    
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    last_year = dt.datetime.strptime(recent_date, '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= last_year).\
    order_by(Measurement.date).all()

    precipitation_dict = dict(results)
    print(f"Results for Precipitation : {precipitation_dict}")
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations/")
def stations():
	stations = session.query(Station.station, Station.name).all()
	all_stations = []
	for station in stations:
		station_dict = {}
		station_dict["Station"] = station.station
		station_dict["Station Name"] = station.name
		all_stations.append(station_dict)
	return jsonify(all_stations)

@app.route('/api/v1.0/tobs/')
def tobs():
	last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
	date_query_results = list(np.ravel(last_date))
	date_split = date_query_results[0].split('-')
	current_year = dt.date(int(date_split[0]), int(date_split[1]), int(date_split[2]))

	# Design a query to retrieve the last 12 months of precipitation data.
	last_year = current_year - dt.timedelta(days=365)
	tobs = session.query(Measurement.station, Measurement.date, Measurement.tobs).\
							filter(Measurement.date > last_year).order_by(Measurement.date)
	tobs_data = []
	for tobs in tobs:
		tobs_dict = {}
		tobs_dict["Station"] = tobs.station
		tobs_dict[tobs.date] = tobs.tobs
		tobs_data.append(tobs_dict)
	return jsonify(tobs_data)

@app.route("/api/v1.0/<start>/")
def daily_normals(start):
    print(start)
    daily_tobs = [func.min(Measurement.tobs),\
                    func.avg(Measurement.tobs),\
					func.max(Measurement.tobs)]
    daily_query = session.query(Measurement.date,*daily_tobs).\
				filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
				group_by(Measurement.date)	

    daily_temp_data = []
    for daily_temp in daily_query:
        (date, min_temp, avg_temp, max_temp) = daily_temp
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temp Min"] = min_temp
        temp_dict["Temp Avg"] = avg_temp
        temp_dict["Temp Max"] = max_temp
        daily_temp_data.append(temp_dict)
    
    return jsonify(daily_temp_data)

@app.route('/api/v1.0/<start>/<end>/')
def daily_normals2(start,end):
	daily_tobs = [func.min(Measurement.tobs),\
					func.avg(Measurement.tobs),\
					func.max(Measurement.tobs)]
	daily_query = session.query(Measurement.date,*daily_tobs).\
				filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
				filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
				group_by(Measurement.date)

	# Convert query results into a json dictionary
	daily_temp_data = []
	for daily_temp in daily_query:
		(t_date2, t_min2, t_avg2, t_max2) = daily_temp
		temp_dict = {}
		temp_dict["Date"] = t_date2
		temp_dict["Temp Min"] = t_min2
		temp_dict["Temp Avg"] = t_avg2
		temp_dict["Temp Max"] = t_max2
		daily_temp_data.append(temp_dict)

	return jsonify(daily_temp_data)

if __name__ == "__main__":
    app.run(debug=True)