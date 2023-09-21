import json
from fastapi import APIRouter

router = APIRouter()



########## circuit breaker
import circuitbreaker
import requests
import logging

logger = logging.getLogger(__name__)

class MyCircuitBreaker(circuitbreaker.CircuitBreaker):
    FAILURE_THRESHOLD = 5
    RECOVERY_TIMEOUT = 60
    EXPECTED_EXCEPTION = requests.RequestException
    

@MyCircuitBreaker()  
def call_external():
    BASE_URL = "https://jsonplaceholder.typicode.com"
    END_POINT = "posts/16"
    resp = requests.get(f"{BASE_URL}/{END_POINT}") 

    if not resp.text:
        return []  
        
    try:
        data = resp.json()
        return data
    except json.JSONDecodeError:
        
        return []  

@router.get("/",tags=['circuit breaker'])
def implement_circuit_breaker():
  try:
    data = call_external()
    return {
      "status_code": 200,
      "success": True,
      "message": "Success get starwars data", 
      "data": data
    }

  except circuitbreaker.CircuitBreakerError as e:
    logger.error(f"Circuit breaker active: {e}")
    return {
      "status_code": 503,
      "success": False,
      "message": f"Circuit breaker active: {e}"
    }

  except requests.exceptions.ConnectionError as e:
    return {
      "status_code": 500,
      "success": False,
      "message": f"Failed get starwars data: {e}"
    }
  




