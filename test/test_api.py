import pytest
import json
import os
import requests
from api import load_exoplanet_data, return_exoplanet_data, delete_exoplanet_data, return_planets, return_planet_info, post_job, get_job_id_list, get_job_info, get_job_result, debug_route

_flask_ip = os.environ.get('FLASK_IP')

response1 = requests.post(f'http://{_flask_ip}:5000/data')
response2 = requests.get(f'http://{_flask_ip}:5000/data')
response3 = requests.get(f'http://{_flask_ip}:5000/planets')
response4 = requests.delete(f'http://{_flask_ip}:5000/data')

def test_load_exoplanet_data():
    assert(response1.status_code == 200)

def test_delete_exoplanet_data():
    assert(response4.status_code == 200)

def test_return_exoplanet_data():
    assert(isinstance(response2.json(), list) == True)
    assert(isinstance(response2.json()[0], dict) == True)

def test_return_planets():
    assert(isinstance(response3.json(), list) == True)
