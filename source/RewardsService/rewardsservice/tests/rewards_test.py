"""
Rewards handler test.
"""
import requests

def test_get_rewards(base_url):
    response = requests.get(f"{base_url}/rewards")
    assert response.status_code == 200
