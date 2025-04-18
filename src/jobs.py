#!/usr/bin/env python3
import json
import uuid
import redis
import os
import logging
from datetime import date
from hotqueue import HotQueue

_redis_ip = os.environ.get('REDIS_IP')
_redis_port = '6379'
_log_level = os.environ.get('LOG_LEVEL')

rd = redis.Redis(host=_redis_ip, port=6379, db=0)
q = HotQueue("queue", host=_redis_ip, port=6379, db=1)
jdb = redis.Redis(host=_redis_ip, port=6379, db=2)
res = redis.Redis(host=_redis_ip, port=6379, db=3)
logging.basicConfig(level=_log_level)

def _generate_jid() -> str:
    '''
    Generates a pseudo-random id for a job

    Args: None
    Returns:
        jid (str): a string that will be the ID for a job
    '''
    return str(uuid.uuid4())

def _instantiate_job(jid: str, status: str, start: int, end: int) -> dict:
    '''
    Generates a description of a job object as a dictionary

    Args:
        jid (str): a string that is the ID for a job
        status (str): the status of that job
        start (int): starting value of data (discovery year), must be within 1992
            and current year
        end (int): ending value of data (discovery year), must be within 1992
            and current year
    Returns:
        job_dict (dict): a dictionary containing all the args
    '''
    return {'id': jid,
            'status': status,
            'start': start,
            'end': end}

def _save_job(jid: str, job_dict: dict) -> None:
    '''
    Save job object in Redis job database

    Args:
        jid (str): a string that is the ID for the job, also its index in jdb
        job_dict (dict): the dictionary containing all the job information
    Returns: none
    '''
    logging.info(f'Job saved')
    jdb.set(jid, json.dumps(job_dict))
    return

def _queue_job(jid: str) -> None:
    '''
    Add job to Redis queue

    Args:
        jid (str): a string that is the ID for the job
    Returns: none
    '''
    logging.info(f'Job queued')
    q.put(jid)
    return

def _add_result(jid: str) -> None:
    '''
    Update the result of a completed job to database "res"

    Args:
        jid (str): a string that is the ID for the job
    Returns: none
    '''
    temp_str = "\"This job has not been finished yet. Please check on job status with route \/jobs\""
    #Default return for an unfinished job
    res.set(jid, temp_str)
    return

def add_job(start: int, end: int, status="submitted") -> dict:
    '''
    The function that generates ID and job description and adds it to the queue

    Args:
        start: starting value of data (discovery year)
        end: ending value of data (discovery year)
        status (str): the status of that job, by default, "submitted"
    Returns:
        job_dict (dict): the dictionary containing all the job information
    '''
    jid = _generate_jid()
    job_dict = _instantiate_job(jid, status, start, end)
    _save_job(jid, job_dict) #save to jdb
    _queue_job(jid) #now add to queue
    _add_result(jid) #now add it to results database
    return job_dict

def get_job_by_id(jid: str) -> dict:
    '''
    Returns the job dictionary given its jid

    Args:
        jid (str): a string that is the ID for the job
    Returns:
        job_dict (dict): the dictionary containing all the job information
    '''
    try:
        job_dict = json.loads(jdb.get(jid))
    except TypeError:
        #If none found, this will return None and throw a type error
        return {"Error: no job found for given ID": 0}
    return job_dict

def get_job_ids() -> list:
    '''
    Returns a list of all job IDs

    Args: none
    Returns:
        jid_list (list): a list of all job IDs
    '''
    jid_list_encoded = jdb.keys()
    #decode from bytes to str
    jid_list = []
    if (len(jid_list_encoded) > 0):
        for i in jid_list_encoded:
            jid_list.append(i.decode())
    return jid_list

def update_job_status(jid: str, status: str) -> None:
    '''
    Update the status of job with ID jid

    Args:
        jid (str): a string that is the ID for the job
        status (str): the new status of the job
    Returns: none
    '''
    job_dict = get_job_by_id(jid)
    try:
        job_dict['status'] = status
        _save_job(jid, job_dict)
    except KeyError:
        raise Exception()
    return

def update_result(jid: str, result: dict) -> None:
    '''
    Update the result of a completed job to database "res"

    Args:
        jid (str): a string that is the ID for the job
        result (dict): the result returned by worker script, in JSON format
    Returns: none
    '''
    res.set(jid, json.dumps(result))
    return

def get_result(jid: str) -> dict:
    '''
    Returns the result of the job given its jid

    Args:
        jid (str): a string that is the ID for the job
    Returns:
        result_dict (dict): the result of the job
    '''

    try:
        result_dict = json.loads(res.get(jid))
    except TypeError:
        return {"Error: no job found for given ID": 0}
    return result_dict
