import pytest
from jobs import add_job, get_job_by_id, get_job_ids, update_job_status, update_result, get_result

result1 = add_job(1992, 2025)

def test_add_job():
    assert(isinstance(result1, dict) == True)
    assert(result1["start"] == 1992)

def test_get_job_by_id():
    assert(isinstance(get_job_by_id("a"), dict) == True)
    jid = result1["id"]
    assert(get_job_by_id(jid)["start"] == 1992)

def test_get_job_ids():
    assert(isinstance(get_job_ids(), list) == True)

def test_get_result():
    assert(isinstance(get_result("a"), dict) == True)
