#!/usr/bin/env python3
import requests
import logging
logging.basicConfig(level='DEBUG')
import json
from typing import List, Tuple
#import time
#import sys
#import math
from flask import Flask, request, send_file
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

# Route to return average number of planets per system
@app.route('/planets/average_planets', methods=['GET'])
def avg_planets_per_system() -> str:
    '''
    This function calculates and returns the average number of planets per star system.

    Args: None
    Returns:
        output (str): a string describing the average number of planets per system
    '''
    list_of_dicts = return_exoplanet_data()
    system_planet_counts = {}

    for planet in list_of_dicts:
        try:
            hostname = planet["hostname"]
        except KeyError:
            continue

        if hostname not in system_planet_counts:
            system_planet_counts[hostname] = 1
        else:
            system_planet_counts[hostname] += 1

    total_systems = len(system_planet_counts)
    total_planets = sum(system_planet_counts.values())

    if total_systems == 0:
        return "No star systems found to compute average.\n"

    average = total_planets / total_systems
    output = f"The average number of planets per system is {average:.2f}\n"
    return output

# Route to return average number of stars per system
@app.route('/systems/average_stars', methods=['GET'])
def avg_stars_per_system() -> str:
    '''
    This function calculates and returns the average number of stars per star system.

    Args: None
    Returns:
        output (str): a string describing the average number of stars per system
    '''
    list_of_dicts = return_exoplanet_data()
    system_star_counts = {}

    for planet in list_of_dicts:
        try:
            hostname = planet["hostname"]
            stars = planet["sy_snum"]
        except KeyError:
            continue

        # Only record one star count per unique hostname
        if hostname not in system_star_counts:
            # Validate that stars is a number
            if isinstance(stars, (int, float)):
                system_star_counts[hostname] = stars

    total_systems = len(system_star_counts)
    total_stars = sum(system_star_counts.values())

    if total_systems == 0:
        return "No systems with valid star count found.\n"

    average = total_stars / total_systems
    output = f"The average number of stars per system is {average:.2f}\n"
    return output

#Route to post a new job
@app.route('/jobs', methods=['POST'])
def post_job() -> dict:
    '''
    This posts a new job to the job database with user defined parameters

    Args: none. This function assumes the user's POST command included a JSON-
        decipherable string with a value for "planet" corresponding to planet
        name
    Returns:
        job_dict (dict): the dictionary containing the info of the job just posted
    '''
    content = request.get_json()
    try:
        def_planet = return_planets()[0] #Default value
    except IndexError:
        logging.error("Database is empty! Did you forget to load the data?")
        return {"Database is empty! Did you forget to load the data?": 0}

    #Check if input is valid
    #This try/except block should catch any key or type errors
    try:
        planet = content["pl_name"]
    except (TypeError, KeyError):
        print("Input invalid: defaulting to planet " + str(def_planet))
        planet = def_planet
    #Check if input is a planet
    if(not (planet in return_planets())):
        print("Planet invalid: defaulting to planet " + str(def_planet))
        planet = def_planet
    
    return add_job(planet)

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

@app.route('/download/<string:jid>', methods=['GET'])
def download(jid: str):
    '''
    This function returns the path to download the resultant image for a finished
    job

    Args:
        jid (str): the job's ID as a string
    Returns:
        a warning message, or the filepath where to find the image
    '''
    #check if jid is valid
    if jid in get_job_ids():
        if get_job_by_id(jid)["status"] == "complete":
            path = f'/app/{jid}.png'
            with open(path, 'wb') as f:
                f.write(get_result(jid))
            return send_file(path, mimetype='image/png', as_attachment=True)
        else:
            return "Job not finished yet\n"
    else:
        return "Invalid job ID\n"

@app.route('/help', methods=['GET'])
def help_route() -> str:
    '''
    Returns a list of all available routes with their descriptions and example curl commands.
    
    Args: None
    Returns:
        help_text (str): help text with descriptions and curl examples for each route
    '''
    help_text = """

Routes:
-------
1. GET /data
   - Description: Returns all exoplanet data from Redis.
   - curl: curl http://localhost:5000/data

2. GET /planets
   - Description: Returns a list of all planet names.
   - curl: curl http://localhost:5000/planets

3. GET /planets/<pl_name>
   - Description: Returns data for a specific planet. Replace <pl_name> with planet name.
   - curl: curl http://localhost:5000/planets/<pl_name>

4. GET /planets/number
   - Description: Returns the total number of planets in the dataset.
   - curl: curl http://localhost:5000/planets/number

5. GET /planets/facilities
   - Description: Returns a count of discovery facilities.
   - curl: curl http://localhost:5000/planets/facilities

6. GET /planets/years
   - Description: Returns a count of planets discovered by year.
   - curl: curl http://localhost:5000/planets/years

7. GET /planets/methods
   - Description: Returns a count of discoveries by method.
   - curl: curl http://localhost:5000/planets/methods

8. GET /planets/average_planets 
   - Description: Returns the average number of planets per system. 
   - curl: curl http://localhost:5000/planets/average_planets

9. GET /systems/average_stars 
   - Description: Returns the average number of stars per system. 
   - curl: curl http://localhost:5000/systems/average_stars

10. GET /jobs
   - Description: Lists all submitted jobs.
   - curl: curl http://localhost:5000/jobs

11. GET /jobs/<id>
   - Description: Returns the input parameters and job type for a specific job. Replace <id> with job ID.
   - curl: curl http://localhost:5000/jobs/<id>

12. GET /download/<id>
    - Description: Returns the result of a completed job. Replace <id> with job ID.
    - curl: curl http://localhost:5000/download/<id>

13. GET /help
    - Description: Shows this help message with all available routes.
    - curl: curl http://localhost:5000/help

14. POST /data
    - Description: Load exoplanet data into Redis.
    - curl: curl -X POST http://localhost:5000/data

15. POST /jobs
    - Description: Submit a job with parameters in JSON format.
    - curl: curl -X POST -H "Content-Type: application/json" -d '{"pl_name":"Kepler-22 b"}' http://localhost:5000/jobs

16. DELETE /data
    - Description: Remove all data from Redis.
    - curl: curl -X DELETE http://localhost:5000/data

"""
    return help_text

#Debugging route
@app.route('/debug', methods=['GET'])
def debug_route() -> str:
    return "Hello world!\n"

def main():
    #Run Flask
    app.run(debug=True, host='0.0.0.0')

if __name__ == '__main__':
    main()
