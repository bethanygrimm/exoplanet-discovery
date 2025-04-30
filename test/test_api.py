import pytest
import json
import os
import requests
#from api import load_exoplanet_data, return_exoplanet_data, delete_exoplanet_data, return_planets, return_planet_info, num_planets, planets_per_facility, planets_per_year, planets_per_method, avg_planets_per_system, avg_stars_per_system, post_job, get_job_id_list, get_job_info, download, help_route, debug_route

response1 = requests.post(f'http://localhost:5000/data')
response2 = requests.get(f'http://localhost:5000/data')
response3 = requests.get(f'http://localhost:5000/planets')
response5 = requests.get(f'http://localhost:5000/planets/number')
response6 = requests.get(f'http://localhost:5000/planets/facilities')
response7 = requests.get(f'http://localhost:5000/planets/years')
response8 = requests.get(f'http://localhost:5000/planets/methods')
response9 = requests.get(f'http://localhost:5000/planets/average_planets')
response10 = requests.get(f'http://localhost:5000/systems/average_stars')
response11 = requests.get(f'http://localhost:5000/jobs')
response12 = requests.get(f'http://localhost:5000/help')
response4 = requests.delete(f'http://localhost:5000/data')
'''
def test_load_exoplanet_data():
    assert(response1.status_code == 200)

def test_delete_exoplanet_data():
    assert(response4.status_code == 200)
'''
def test_return_exoplanet_data():
    assert(isinstance(response2.json(), list) == True)
    assert(isinstance(response2.json()[0], dict) == True)

def test_return_planets():
    assert(isinstance(response3.json(), list) == True)

def test_num_planets():
    assert(isinstance(response5.content.decode("utf-8"), str) == True)

def test_planets_per_facility():
    assert(isinstance(response6.json(), dict) == True)

def test_planets_per_year():
    assert(isinstance(response7.json(), dict) == True) 

def test_planets_per_method():
    assert(isinstance(response8.json(), dict) == True) 

def test_avg_planets_per_system():
    assert(isinstance(response9.content.decode("utf-8"), str) == True)

def test_avg_stars_per_system():
    assert(isinstance(response10.content.decode("utf-8"), str) == True)

def test_get_job_id_list():
    assert(isinstance(response11.json(), list) == True)

def test_help_route():
    assert(isinstance(response12.content.decode("utf-8"), str) == True)
