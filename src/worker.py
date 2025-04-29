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

def plot_image(jid, planet):
    '''
    Plot the planetary system, using data from the Redis database

    Args:
        jid (str): the job's ID as a string
        planet (str): the planet's name as a string
    Returns: none
    '''
    #Required info fields from redis:
    #hostname
    #number of stars
    #stellar radius
    #stellar temp
    #number of planets
    #planet radius FOR EACH in hostname
    #orbit semi-major axis FOR EACH in hostname
    #also some will be sparsely populated
    
    #planet -> get dict -> also get hostname
    #list of dicts for all of hostname -> get planetary data

    system = "system"
    n_stars = 1 #pull this from redis
    STAR_CONST = 1090 #these are in terms of solar masses, some constant
    #populate lists according to n_stars
    star_size, star_color, y_s = [], [], []
    r = .1 * (n_stars-1)
    x_s = np.random.rand(n_stars)
    x_s = x_s.tolist()
    for i in range(n_stars):
        star_size.append(1 * STAR_CONST)
        #redis
        star_color.append('gold')
        #probably use some if/else logic, use either temp or spectral type?
        #if there's multiple stars (same data)... let's make it so there is a 
        #radius that depends on n_stars
        x_s[i] = (x_s[i] * r * 2) - r
        y_s.append(np.sqrt((r*r) - (x_s[i]*x_s[i])))
        if np.random.rand() < 0.5:
            y_s[i] = y_s[i] * -1
    
    n_planets = 1 #redis
    P_SIZE = 10
    P_ORBIT = 1
    p_size, p_orbit, p_color, y_p = [], [], [], []
    x_p = np.random.rand(n_planets)
    x_p = x_p.tolist()
    for i in range(n_planets):
        p_size.append(1 * P_SIZE)
        #redis
        orbit = 1 * P_ORBIT
        p_orbit.append(orbit)
        #redis
        x_p[i] = (x_p[i] * orbit * 2) - orbit
        y_p.append(np.sqrt((orbit*orbit) - (x_p[i]*x_p[i])))
        if np.random.rand() < 0.5:
            y_p[i] = y_p[i]*-1
        p_color.append('blue')
    
    x = x_s + x_p
    y = y_s + y_p
    size = star_size + p_size
    color = star_color + p_color
    
    title = "Visual of Planetary System " + system
    filename = "/" + system + ".png"
    o_int = int(np.max(p_orbit) + 1)
    
    plt.scatter(x, y, size, color)
    plt.xticks([-1*o_int, 0, o_int])
    plt.yticks([-1*o_int, 0, o_int])
    plt.title(title)
    plt.xlabel("Distances not to scale.")
    plt.savefig(filename)

    with open (filename, 'rb') as f:
        img = f.read()

    update_result(jid, filename, img)

q.worker
def work(jid: str) -> None:
    '''
    Return a diagram of the planetary system given a planet name

    Args:
        jid (str): ID of the job requesting
    Returns: none
    '''
    method_dict = {}
    job_dict = get_job_by_id(jid)
    planet = job_dict['planet']
    update_job_status(jid, "in progress")
    
    planet_data = {}
    host_data = []
    incides = len(rd.keys())

    #Check for wrong jid
    message = "Error: no job found for given ID"
    if message in job_dict:
        logging.error(f'Error: no job found for given ID')
    else:
        plot_image(jid, planet)
        '''
        #First get data from rdb - every data point that falls in date range
        #Then populate with data and return
        
        for i in range(len(rd.keys())):
            #iterate through each dictionary
            temp = json.loads(rd.get(i))
            
            disc_year = 0
            try:
                disc_year = temp["disc_year"]
            except KeyError:
                logging.error(f'Invalid key')
            
            if((disc_year < start) or (disc_year > end)):
                continue
            #Out of bounds
        
            method = ""
            try:
                method = temp["discoverymethod"]
            except KeyError:
                logging.error(f'Invalid key')
                
            if (method_dict.get(method, 0) == 0):
                method_dict[method] = 1
            else:
                method_dict[method] += 1
        '''
    update_job_status(jid, "complete")
    return

work()
