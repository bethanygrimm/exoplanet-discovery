'''
import pytest
from jobs import add_job, get_job_by_id
from worker import exoplanets_per_method

result1 = add_job(1992, 2025)
jid = result1["id"]

def test_exoplanets_per_method():
    exoplanets_per_method(jid)
    assert(get_job_by_id(jid)["status"] == "complete")
'''
