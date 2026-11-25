"""
customer_handler CustomerHandler:put() function test file.
"""
import requests

def test_add_to_reward_points_on_existing_customer(base_url, db):
    """
    Test PUT /customers endpoint

    - The status code should be 200 (OK)
    - The response should show updated data
    - The customer should be updated in the DB

    """
    # Add the existing customer to the Tests DB (removed again after the test by the clean_customers fixture)
    db.customers.insert_one({"email": "tester@urbn.com", "rewardPoints": 99, "rewardTier": None, "rewardTierName": None})

    payload = {
        "email": "tester@urbn.com",
        "orderTotal": 100
    }

    response = requests.put(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["rewardPoints"] == 199
    assert response_body["rewardTier"] == "A"

    customer = db.customers.find_one({"email": payload["email"]}, {"_id": 0})
    assert customer["rewardPoints"] == 199
    assert customer["rewardTier"] == "A"

def test_subtract_from_reward_points_on_existing_customer(base_url, db):
    """
    Test PUT /customers endpoint

    - The status code should be 200 (OK)
    - The response should show updated data
    - The customer should be updated in the DB
    """
    # Add the existing customer to the Tests DB (removed again after the test by the clean_customers fixture)
    db.customers.insert_one({"email": "tester@urbn.com", "rewardPoints": 99, "rewardTier": None, "rewardTierName": None})

    payload = {
        "email": "tester@urbn.com",
        "orderTotal": -98
    }

    response = requests.put(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["rewardPoints"] == 1
    assert response_body["rewardTier"] == None

    customer = db.customers.find_one({"email": payload["email"]}, {"_id": 0})
    assert customer["rewardPoints"] == 1
    assert customer["rewardTier"] == None

def test_subtract_from_reward_points_on_existing_customer_stops_at_zero(base_url, db):
    """
    Test PUT /customers endpoint

    - The status code should be 200 (OK)
    - The response should show updated data
    - The customer should be updated in the DB
    """
    # Add the existing customer to the Tests DB (removed again after the test by the clean_customers fixture)
    db.customers.insert_one({"email": "tester@urbn.com", "rewardPoints": 99, "rewardTier": None, "rewardTierName": None})

    payload = {
        "email": "tester@urbn.com",
        "orderTotal": -200
    }

    response = requests.put(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["rewardPoints"] == 0
    assert response_body["rewardTier"] == None

    customer = db.customers.find_one({"email": payload["email"]}, {"_id": 0})
    assert customer["rewardPoints"] == 0
    assert customer["rewardTier"] == None

def test_add_to_reward_points_on_existing_customer_stops_at_1000(base_url, db):
    """
    Test PUT /customers endpoint

    - The status code should be 200 (OK)
    - The response should show updated data
    - The customer should be updated in the DB
    """
    # Add the existing customer to the Tests DB (removed again after the test by the clean_customers fixture)
    db.customers.insert_one({"email": "tester@urbn.com", "rewardPoints": 99, "rewardTier": None, "rewardTierName": None})

    payload = {
        "email": "tester@urbn.com",
        "orderTotal": 1400
    }

    response = requests.put(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["rewardPoints"] == 1000
    assert response_body["rewardTier"] == "J"

    customer = db.customers.find_one({"email": payload["email"]}, {"_id": 0})
    assert customer["rewardPoints"] == 1000
    assert customer["rewardTier"] == "J"

def test_we_404_unknown_emails(base_url, db):
    """
    Test PUT /customers endpoint

    - The status code should be 404 (NOT FOUND)
    """
    # Add the existing customer to the Tests DB (removed again after the test by the clean_customers fixture)
    db.customers.insert_one({"email": "tester@urbn.com", "rewardPoints": 99, "rewardTier": None, "rewardTierName": None})

    payload = {
        "email": "tester6@urbn.com",
        "orderTotal": 1400
    }

    response = requests.put(f"{base_url}/customers", json=payload)

    assert response.status_code == 404

def test_we_422_invalid_emails(base_url, db):
    """
    Test PUT /customers endpoint

    - The status code should be 422 (UNPROCESSABLE ENTITY)
    - error_code should be 001
    """
    payload = {
        "email": "tester6urbn.com",
        "orderTotal": 1400
    }

    response = requests.put(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 422
    assert response_body["error_code"] == "001"

def test_we_422_invalid_order_totals(base_url, db):
    """
    Test PUT /customers endpoint

    - The status code should be 422 (UNPROCESSABLE ENTITY)
    """
    payload = {
        "email": "tester@urbn.com",
        "orderTotal": 1400.6789
    }

    response = requests.put(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 422
    assert response_body["error_code"] == "002"
