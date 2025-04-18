#!/usr/bin/env python3
from jobs import get_job_by_id, get_job_ids, update_job_status, add_job, update_result
import queue
from hotqueue import HotQueue
import redis
import time
import os
import json
import logging
from typing import List, Tuple

redis_ip = os.environ.get('REDIS_IP')
log_level = os.environ.get('LOG_LEVEL')

rd = redis.Redis(host=redis_ip, port=6379, db=0)
q = HotQueue("queue", host=redis_ip, port=6379, db=1)
logging.basicConfig(level=log_level)

@q.worker
def exoplanets_per_method(jid: str) -> None:
    '''
    Return a dictionary that consists of number of exoplanets found per discovery
    method, filtered from a range of years

    Args:
        jid (str): ID of the job requesting
    Returns: none
    '''
    method_dict = {}
    job_dict = get_job_by_id(jid)
    start = job_dict['start']
    end = job_dict['end']
    update_job_status(jid, "in progress")
    
    #Check for wrong jid
    message = "Error: no job found for given ID"
    if message in job_dict:
        logging.error(f'Error: no job found for given ID')
    else:
    
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
        
    update_result(jid, method_dict)
    update_job_status(jid, "complete")
    return

exoplanets_per_method()
