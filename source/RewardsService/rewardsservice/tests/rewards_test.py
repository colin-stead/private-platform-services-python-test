"""
Rewards handler test files.
"""
import requests

BASE_URL = "http://localhost:7050"

def test_get_rewards():
    response = requests.get(f"{BASE_URL}/rewards")
    assert response.status_code == 200
