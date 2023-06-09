import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
from flask_cors import CORS

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Data/vancouver.sqlite", connect_args={'check_same_thread': False}, echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# # Save reference to the table
crime = Base.classes.crime
rental = Base.classes.rental

# #################################################
# Flask Setup
# #################################################
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/crime/(year)<br/>"
        f"# Query to return crime data by Specific Year<br/>"
        f"<br/>"
        f"/api/v1.0/crime/(year)/(typeofcrime)<br/>"
        f"# Query to return crime data by Specific Year and Type of Crime<br/>"
        f"<br/>"
        f"/api/v1.0/crimetype/(year)<br/>"
        f"# Query to return grouped crime data for specific year<br/>"
        f"<br/>"
        f"/api/v1.0/crimetypewoyear/<br/>"
        f"#Query to return grouped crime data for each year separately<br/>"
        f"<br/>"
        f"/api/v1.0/crimeall/<br/>"
        f"# Query to return total crimes for all years<br/>"
        f"<br/>"
        f"/api/v1.0/crimeall/(typeofcrime)<br/>"
        f"# Query to return specific crime count for all years<br/>"
        f"<br/>"
        f"/api/v1.0/neighbourhood/(year)<br/>"
        f"# Query to return rental data by Specific Year<br/>"
        f"<br/>"
        f"/api/v1.0/neighbourhood/(year)/(neighbourhood)<br/>"
        f"# Query to return rental data only by Specific Year for specific Neighbourhood<br/>"
        f"<br/>"
        f"/api/v1.0/neighbourhoodunits<br/>"
        f"# Query to return total rental units for all Years<br/>"
        f"<br/>"
        f"/api/v1.0/neighbourhoodmedrent<br/>"
        f"# Query to return average rental price for all Years<br/>"

    )

#############################################
# Query to return crime data by Specific Year
#############################################

@app.route("/api/v1.0/crime/<year>")
def crimeyear(year):
    #Create session link from Python to the database
    session = Session(engine)

    """Return Vancouver crime data by specific year"""
    #Query of crime dataset
    results = session.query(crime.Year, crime.Type, crime.Month, crime.Latitude, crime.Longitude).filter(crime.Year == int(year))

    session.close()

    crime_rows = [{"year": result[0], "crime_type": result[1], "crime_month": result[2], "crime_latitude" : result[3], "crime_longitude": result[4]} for result in results]

    return jsonify(crime_rows)

################################################################
# Query to return crime data by Specific Year and Type of Crime
################################################################

@app.route("/api/v1.0/crime/<year>/<typeofcrime>")
def crime_type(year, typeofcrime):
    #Create session link from Python to the database
    session = Session(engine)

    """Return Vancouver crime data from specified year and specified type of crime"""
    #Query of crime dataset
    crime_year = session.query(crime.Year, crime.Type, crime.Month, crime.Latitude, crime.Longitude).\
        filter(crime.Year == int(year))
    
    results = crime_year.filter(crime.Type == typeofcrime)

    session.close()

    crime_rows = [{"year": result[0], "crime_month": result[2], "crime_latitude" : result[3], "crime_longitude": result[4]} for result in results]

    return jsonify(crime_rows)

################################################################
# Query to return grouped crime data for specific year
################################################################

@app.route("/api/v1.0/crimetype/<year>")
def crime_type_group(year):
    #Create session link from Python to the database
    session = Session(engine)

    """Query to return grouped crime data for specific year"""
    #Query of crime dataset
    results = session.query(crime.Type, func.count(crime.Type)).\
        filter(crime.Year == int(year)).group_by(crime.Type).all()
    
    session.close()

    crime_rows = [{"crime_type": result[0], "count": result[1]} for result in results]

    return jsonify(crime_rows)

################################################################
# Query to return grouped crime data for each year separately
################################################################

@app.route("/api/v1.0/crimetypewoyear/")
def crime_type_woyear():
    #Create session link from Python to the database
    session = Session(engine)

    """Query to return grouped crime data for each year separately"""
    #Query of crime dataset
    results = session.query(crime.Year, crime.Type, func.count(crime.Type)).\
        group_by(crime.Year, crime.Type).all()
    
    session.close()

    crime_rows = [{"crime_year" : result[0], "crime_type": result[1], "count": result[2]} for result in results]

    return jsonify(crime_rows)

##############################################
# Query to return total crimes for all years
##############################################

@app.route("/api/v1.0/crimeall/")
def crime_all_group():
    #Create session link from Python to the database
    session = Session(engine)

    """Query to return total crimes for specific all years"""
    #Query of crime dataset
    results = session.query(crime.Year, crime.Type, func.count(crime.Type)).\
        group_by(crime.Year).all()
    
    session.close()

    crime_rows = [{"year": result[0], "count": result[2]} for result in results]

    return jsonify(crime_rows)

#######################################################
# Query to return Specific crime count for  all years
#######################################################

@app.route("/api/v1.0/crimeall/<typeofcrime>")
def crime_year_group(typeofcrime):
    #Create session link from Python to the database
    session = Session(engine)

    """# Query to return specific crime count for  all years"""
    #Query of crime dataset
    results = session.query(crime.Year, crime.Type, func.count(crime.Type)).\
        filter(crime.Type == typeofcrime).group_by(crime.Year).all()
    
    session.close()

    crime_rows = [{"year": result[0], "count": result[2]} for result in results]

    return jsonify(crime_rows)

###############################################
# Query to return rental data by Specific Year
###############################################

@app.route("/api/v1.0/neighbourhood/<year>")
def neighbourhood(year):
    #Create session link from Python to the database
    session = Session(engine)

    neighbourhoods = ["Southeast Vancouver", "Marpole", "Westside/Kerrisdale", "University Endowment Lands", "Mount Pleasant/Renfrew Heights", "South Granville/Oak", "Kitsilano/Point Grey", "East Hastings", "Downtown", "English Bay", "West End/Stanley Park"]

    """Return Vancouver rental data for specific year"""
    #Query of crime dataset
    results = session.query(rental.Year, rental.Neighbourhood, rental.PercentVacancyRate, rental.PercentAvailabilityRate, rental.AverageRentinDollars, rental.MedianRentinDollars, rental.PercentChange, rental.Units).\
    filter(rental.Year == year).filter(rental.Neighbourhood.in_(neighbourhoods))

    session.close()

    rental_rows = [{"year": result[0], "neighbourhood": result[1], "vacancy_rate_percent": result[2], "availability_rate_percent" : result[3], "average_rent_dollars": result[4], "median_rent_dollars": result[5], "percent_change": result[6], "units": result[7]} for result in results]

    return jsonify(rental_rows)

###############################################################################
# Query to return rental data only by Specific Year for specific Neighbourhood
###############################################################################

@app.route("/api/v1.0/neighbourhood/<year>/<neighbourhood>")
def neighbourhood_area(year, neighbourhood):
    #Create session link from Python to the database
    session = Session(engine)

    """Return Vancouver rental data for specified year and neighbourhood"""
    #Query of crime dataset
    results = session.query(rental.Year, rental.Neighbourhood, rental.PercentVacancyRate, rental.PercentAvailabilityRate, rental.AverageRentinDollars, rental.MedianRentinDollars, rental.PercentChange, rental.Units).\
    filter(rental.Year == year).filter(rental.Neighbourhood == neighbourhood)

    session.close()

    rental_rows = [{"year": result[0], "neighbourhood": result[1], "vacancy_rate_percent": result[2], "availability_rate_percent" : result[3], "average_rent_dollars": result[4], "median_rent_dollars": result[5], "percent_change": result[6], "units": result[7]} for result in results]

    return jsonify(rental_rows)

####################################################
# Query to return total rental units for all Years
####################################################

@app.route("/api/v1.0/neighbourhoodunits")
def neighbourhood_units_all():
    #Create session link from Python to the database
    session = Session(engine)
    
    neighbourhoods = ["Southeast Vancouver", "Marpole", "Westside/Kerrisdale", "University Endowment Lands", "Mount Pleasant/Renfrew Heights", "South Granville/Oak", "Kitsilano/Point Grey", "East Hastings", "Downtown", "English Bay", "West End/Stanley Park"]

    """# Query to return total rental units for all Years"""
    #Query of crime dataset
    results = session.query(rental.Year, rental.Units, func.sum(rental.Units)).\
        filter(rental.Neighbourhood.in_(neighbourhoods)).\
        group_by(rental.Year).all()
        
        

    session.close()

    rental_rows = [{"year": result[0], "total units": result[2]} for result in results]

    return jsonify(rental_rows)

##############################################################
# Query to return rental price per neighbourhood for all Years
##############################################################

@app.route("/api/v1.0/neighbourhoodmedrent")
def neighbourhood_medrent_all():
    #Create session link from Python to the database
    session = Session(engine)

    neighbourhoods = ["Southeast Vancouver", "Marpole", "Westside/Kerrisdale", "University Endowment Lands", "Mount Pleasant/Renfrew Heights", "South Granville/Oak", "Kitsilano/Point Grey", "East Hastings", "Downtown", "English Bay", "West End/Stanley Park"]

    """# Query to return rental price per neighbourhood for all Years"""
    #Query of crime dataset
    results = session.query(rental.Year, rental.Neighbourhood, rental.MedianRentinDollars).\
        filter(rental.Neighbourhood.in_(neighbourhoods))

    session.close()

    rental_rows = [{"year": result[0], "Neighbourhood": result[1], "median rental price": result[2]} for result in results]

    return jsonify(rental_rows)


if __name__ == '__main__':
    app.run(debug=True)

