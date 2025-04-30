#!/usr/bin/env python3
from jobs import get_job_by_id, get_job_ids, update_job_status, add_job, update_result
import queue
from hotqueue import HotQueue
import redis
import time
import os
import json
import logging
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple

redis_ip = os.environ.get('REDIS_IP')
log_level = os.environ.get('LOG_LEVEL')

rd = redis.Redis(host=redis_ip, port=6379, db=0)
q = HotQueue("queue", host=redis_ip, port=6379, db=1)
logging.basicConfig(level=log_level)

def plot_image(jid: str, planet_data: dict, hostname: str, 
               host_data: List[dict]) -> None:
    '''
    Plot the planetary system, using data from the Redis database

    Args:
        jid (str): the job's ID as a string
        planet_data (dict): the dict containing all of the planet's info
        hostname (str): the name of the planetary system containing the planet
        host_data (list[dict]): a list of all dicts with the same hostname
    Returns: none
    '''
    
    system = hostname
    
    try:
        n_stars = planet_data["sy_snum"]
    except KeyError:
        n_stars = 1 #Default value
    
    STAR_CONST = 1090 #this will be in terms of solar radii. 1090 is a good
    # number for the plot

    star_size, star_color, y_s = [], [], []
    #r is an arbitrary "radius" - only use is in making sure the stars don't
    #overlap, but it's not perfect
    r = .1 * (n_stars-1)
    x_s = np.random.rand(n_stars)
    x_s = x_s.tolist()

    for i in range(n_stars):
        #Find stellar radius
        try:
            st_rad = planet_data["st_rad"]
        except KeyError:
            st_rad = 1

        star_size.append(st_rad * STAR_CONST)
        
        #Stellar temperature tells us its "color" - red for cooler and blue
        #for hotter.
        try:
            st_teff = planet_data["st_teff"]
        except KeyError:
            st_teff = 5772 #Sun's temperature in Kelvin - default
        if st_teff < 5000:
            star_color.append('lightcoral')
        elif st_teff > 10000:
            star_color.append('paleturquoise')
        else:
            star_color.append('gold')
        
        #Generate random coordinates for the stars (if there are more than 1)
        x_s[i] = (x_s[i] * r * 2) - r
        y_s.append(np.sqrt((r*r) - (x_s[i]*x_s[i])))
        if np.random.rand() < 0.5:
            y_s[i] = y_s[i] * -1
    
    try:
        n_planets = planet_data["sy_pnum"]
    except KeyError:
        n_planets = 1 #Default value

    P_SIZE = 10 #in terms of earth radii
    P_ORBIT = 10 #in terms of earth semi-major axes, or aus

    p_size, p_orbit, p_color, y_p = [], [], [], []
    x_p = np.random.rand(n_planets)
    x_p = x_p.tolist()

    for i in range(n_planets):
        #Find planet's radius for each planet
        try:
            pl_rade = host_data[i]["pl_rade"]
        except KeyError:
            pl_rade = 1
        
        p_size.append(pl_rade * P_SIZE)
        
        #Find planet's semi-major axis
        try:
            pl_orbsmax = host_data[i]["pl_orbsmax"]
        except KeyError:
            pl_orbsmax = 1

        orbit = pl_orbsmax * P_ORBIT
        p_orbit.append(orbit)
        
        #Generate random coordinates for the planets
        x_p[i] = (x_p[i] * orbit * 2) - orbit
        y_p.append(np.sqrt((orbit*orbit) - (x_p[i]*x_p[i])))
        if np.random.rand() < 0.5:
            y_p[i] = y_p[i]*-1
        p_color.append('slategray')
    
    #Now concatenate lists to scatter
    x = x_s + x_p
    y = y_s + y_p
    size = star_size + p_size
    color = star_color + p_color
    
    title = "Visual of Planetary System " + hostname
    filename = "/" + hostname + ".png"
    o_int = int(np.max(p_orbit) + 1) #This sets the scale
    
    plt.scatter(x, y, size, color)
    plt.xticks([-1*o_int, 0, o_int])
    plt.yticks([-1*o_int, 0, o_int])
    plt.title(title)
    plt.xlabel("Distances not to scale.")
    plt.savefig(filename)

    with open (filename, 'rb') as f:
        img = f.read()

    update_result(jid, img)

@q.worker
def work(jid: str) -> None:
    '''
    Return a diagram of the planetary system given a planet name

    Args:
        jid (str): ID of the job requesting
    Returns: none
    '''
    job_dict = get_job_by_id(jid)   
    update_job_status(jid, "in progress")
    
    planet_data = {}
    hostname = ""
    host_data = []
    indices = len(rd.keys())

    #Check for wrong jid
    message = "Error: no job found for given ID"
    if message in job_dict:
        logging.error(f'Error: no job found for given ID')
        #No need to update result
    else:
        planet = job_dict["planet"]
        
        #Get data for this planet
        for i in range(indices):
            #iterate through each dictionary
            temp = json.loads(rd.get(i))
            try:
                pl_name = temp["pl_name"]
                if planet == pl_name:
                    planet_data = temp
            except KeyError:
                logging.error(f'Invalid key')

        #Get hostname
        try:
            hostname = planet_data["hostname"]
        except KeyError:
            logging.error(f'Invalid key')

        #Get all dictionaries for all planets with same hostname
        for i in range(indices):
            temp = json.loads(rd.get(i))
            try:
                h = temp["hostname"]
                if hostname == h:
                    host_data.append(temp)
            except KeyError:
                logging.error(f'Invalid key')

        #Each entry has a hostname and planet name, KeyErrors are unexpected here

        plot_image(jid, planet_data, hostname, host_data)
        
    update_job_status(jid, "complete")
    return

work()
