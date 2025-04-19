#!/usr/bin/env python3
import requests
import logging
logging.basicConfig(level='DEBUG')
import json
from typing import List, Tuple
#import time
#import sys
#import math
from flask import Flask, request
import redis
import os
from datetime import date
from jobs import add_job, get_job_by_id, get_job_ids, get_result

#Instantiate Flask object
app = Flask(__name__)
#Instantiate Redis object
#path /data will be mounted on the port when the container is composed
redis_ip = os.environ.get('REDIS_IP')
log_level = os.environ.get('LOG_LEVEL')
rd = redis.Redis(host=redis_ip, port=6379, db=0)
logging.basicConfig(level=log_level)

#Load the exoplanet data to Redis database from the web
@app.route('/data', methods=['POST'])
def load_exoplanet_data() -> str:
    '''
    This function loads the exoplanet dataset into the Redis container, so that it
    is accessible in the user's local "/data" folder.

    Args: None
    Returns:
        output (str): a string that tells user whether method was successful
    '''

    list_of_dicts = []
    try:
        response = requests.get(url="https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+*+from+ps+where+default_flag=1&format=json")
        list_of_dicts = response.json()
        #this response readily gives us the list of dicts we need
    except ConnectionError:
        logging.error(f'Data not found at url')
        return "Data load failed\n"
    except KeyError:
        logging.error(f'Data in incorrect format')
        return "Data load failed\n"

    #save to Redis - since Redis is unordered, iterate through indices and use
    #json.dumps() to load it to Redis and json.loads() to take it out
    for i in range(len(list_of_dicts)):
        rd.set(i, json.dumps(list_of_dicts[i]))

    return "Data load succeeded\n"

#Return all data as a JSON list
@app.route('/data', methods=['GET'])
def return_exoplanet_data() -> List[dict]:
    '''
    This function returns the entire exoplanet dataset.

    Args: None
    Returns:
        list_of_dicts (list[dict]): a list of dictionaries containing the entire
            exoplanet dataset
    '''
    list_of_dicts = []
    indices = 0
    try:
        indices = len(rd.keys())
    except ConnectionError:
        logging.error(f'Database not found')

    #load data from Redis database
    for i in range(indices):
        try:
            list_of_dicts.append(json.loads(rd.get(i)))
            #in case of error, append empty key-value pair
        except (TypeError, json.decoder.JSONDecodeError):
            list_of_dicts.append({})

    return list_of_dicts

#Delete all data from Redis
@app.route('/data', methods=['DELETE'])
def delete_exoplanet_data() -> str:
    '''
    This function deletes all exoplanet data from the Redis database, and 
    consequently, from the user's local "/data" folder:

    Args: None
    Returns:
        output (str): a string that tells user whether method was successful
    '''
    indices = 0
    try:
        indices = len(rd.keys())
    except ConnectionError:
        logging.error(f'Database not found')
        return "Deletion failed\n"

    for i in range(indices):
        rd.delete(i)

    if(len(rd.keys()) == 0):
        return "Deletion succeeded\n"
    else:
        return "Deletion failed\n"

#Return json-formatted list of all planet names
@app.route('/planets', methods=['GET'])
def return_planets() -> list:
    '''
    This function returns all the pl_name fields as a json-formatted list.

    Args: None
    Returns:
        planets (list): a list of all planet name strings
    '''
    planets = []
    indices = 0
    try:
        indices = len(rd.keys())
    except ConnectionError:
        logging.error(f'Database not found')

    for i in range(indices):
        dict_i = {}
        try:
            dict_i = json.loads(rd.get(i))
        except (TypeError, json.decoder.JSONDecodeError):
            continue
        try:
            planets.append(dict_i["pl_name"])
        except KeyError:
            continue

    return planets

#Return all data for a given planet name
@app.route('/planets/<string:pl_name>', methods=['GET'])
def return_planet_info(pl_name: str) -> dict:
    '''
    This functions returns all available data for a planet given its name.

    Args:
        pl_name (string): a string corresponding to the name of the planet
    Returns:
        data (dict): a dictionary containing the data for the planet whose was
        given
    '''
    data = {}
    indices = 0
    try:
        indices = len(rd.keys())
    except ConnectionError:
        logging.error(f'Database not found')

    #let's check whether id is a valid id using the return_planets() function
    planet_list = return_planets()
    if((pl_name in planet_list) == False):
        return {"Planet name not found": 0}
    else:
        #iterate through database
        for i in range(indices):
            data = {}
            is_planet = False
            try:
                data = json.loads(rd.get(i))
            except (TypeError, json.decoder.JSONDecodeError):
                continue
            try:
                is_planet = (data["pl_name"] == pl_name)
            except KeyError:
                continue
            if(is_planet):
                return data

#Route to return number of planets
@app.route('/planets/number', methods=['GET'])
def num_planets() -> str:
    '''
    This function returns the number of planets.

    Args: none
    Returns:
        output (str): a simple string that returns the number of planets
    '''
    planet_list = return_planets()
    num = len(planet_list)
    output = "There are " + str(num) + " exoplanets in the database.\n"
    return output

#Route to return number of exoplanets found per facility
@app.route('/planets/facilities', methods=['GET'])
def planets_per_facility() -> dict:
    '''
    This function returns a dictionary with each facility name and the number of
    planets discovered there.

    Args: none
    Returns:
        data (dict): a dictionary containing information about how many planets
        were discovered at each facility
    '''
    #Retrieve data from rd, iterate through list of dicts
    #Then populate the dict with data and return
    list_of_dicts = return_exoplanet_data()
    facility_dict = {}

    for i in list_of_dicts:
        try:
            facility = i["disc_facility"]
        except KeyError:
            #Possible that some dictionaries (i) have no value for "disc_facility"
            #because the data is sparsely populated - in this case, skip
            continue
        if(facility_dict.get(facility, 0) == 0):
            facility_dict[facility] = 1
        else:
            facility_dict[facility] += 1
    return facility_dict

#Route to return number of exoplanets found per year
@app.route('/planets/years', methods=['GET'])
def planets_per_year() -> dict:
    '''
    This function returns a dictionary with each year and the number of planets
    discovered that year.

    Args: none
    Returns:
        data (dict): a dictionary containing information about how many planets
        were discovered each year
    '''
    #Retrieve data from rd, iterate through list of dicts
    #Then populate the dict with data and return
    list_of_dicts = return_exoplanet_data()
    year_dict = {}

    for i in list_of_dicts:
        try:
            year = i["disc_year"]
        except KeyError:
            #Possible that some dictionaries (i) have no value for "disc_year"
            #because the data is sparsely populated - in this case, skip
            continue
        if(year_dict.get(year, 0) == 0):
            year_dict[year] = 1
        else:
            year_dict[year] += 1
    return year_dict

#Route to return number of exoplanets found per method
@app.route('/planets/methods', methods=['GET'])
def planets_per_method() -> dict:
    '''
    This function returns a dictionary with each method and the number of planets
    discovered via each method.

    Args: none
    Returns:
        data (dict): a dictionary containing information about how many planets
        were discovered via each discovery method
    '''
    #Retrieve data from rd, iterate through list of dicts
    #Then populate the dict with data and return
    list_of_dicts = return_exoplanet_data()
    method_dict = {}

    for i in list_of_dicts:
        try:
            method = i["discoverymethod"]
        except KeyError:
            #Possible that some dictionaries (i) have no value for 
            #"discoverymethod" because the data is sparsely populated - in this
            #case, skip
            continue
        if(method_dict.get(method, 0) == 0):
            method_dict[method] = 1
        else:
            method_dict[method] += 1
    return method_dict

#Route to post a new job
@app.route('/jobs', methods=['POST'])
def post_job() -> str:
    '''
    This posts a new job to the job database with user defined parameters

    Args: none. This function assumes the user's POST command included a JSON-
        decipherable string with integer values for "start" and "end",
        corresponding to the years the user wishes to retrieve data from
    Returns:
        job_dict (dict): the dictionary containing the info of the job just posted
    '''
    content = request.get_json()
    #The last valid index will be the current year
    current_date = date.today()
    current_year = current_date.year
    start = 1992
    end = current_year
    
    #Check if input is valid
    #This try/except block should catch any key or type errors
    try:
        start = content["start"]
    except (TypeError, KeyError):
        print("Input invalid: defaulting to start year 1992")
    try:
        end = content["end"]
    except (TypeError, KeyError):
        print("Input invalid: defaulting to end year " + str(current_year))

    #Check if input fits data range
    if(not (isinstance(start, int)) or 
       ((start < 1992) or (start > current_year))):
        print("Start year invalid: defaulting to 1992")
        start = 1992
    if(not (isinstance(end, int)) or ((end < 1992) or (end > current_year))):
        print("End year invalid: defaulting to current year")
        end = current_year
    if(end < start):
        print("End year invalid: defaulting to " + str(start))
        end = start

    return add_job(start, end)

#Route to get all existing job ids
@app.route('/jobs', methods=['GET'])
def get_job_id_list() -> list:
    '''
    This returns a list of all existing job IDs

    Args: none
    Returns:
        job_list (list): a list of all existing job IDs
    '''
    return get_job_ids()

#Route to get job information for a specific job id
@app.route('/jobs/<string:jid>', methods=['GET'])
def get_job_info(jid: str) -> dict:
    '''
    This returns a dict of the job information given the job ID

    Args:
        jid (str): the job's ID as a string
    Returns:
        job_dict (dict): the dictionary containing all the job information
    '''
    return get_job_by_id(jid) 

#Route to get job result for a specific job id
@app.route('/results/<string:jid>', methods=['GET'])
def get_job_result(jid: str) -> dict:
    '''
    This returns the output of the job given the job ID

    Args:
        jid (str): the job's ID as a string
    Returns:
        result_dict (dict): the dictionary containing all the results from a job
    '''
    return get_result(jid)

#Debugging route
@app.route('/debug', methods=['GET'])
def debug_route() -> str:
    return "Hello world!"

def main():
    #Run Flask
    app.run(debug=True, host='0.0.0.0')

if __name__ == '__main__':
    main()
