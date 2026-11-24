"""
customer_handler CustomerHandler:create() function test file.
"""
import requests
from models.customers import Customer

MAXIMUM_POINTS = 1000

def test_create_customer_with_order_total_less_than_100(base_url, db):
    """
    Test POST /customers endpoint

    - The status code should be 201 (Created)
    - The order total should be rounded down for the user's reward points
    - A Customer should be created
    - The Customer should not have a rewardsTier
    - The nextRewardsTier should be 'A'
    - The Customer should be saved in the Tests DB customers collection
    """
    payload = {
        "email": "tester@urbn.com",
        "orderTotal": 99
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 201
    assert response_body["rewardPoints"] == payload["orderTotal"]
    assert response_body["rewardTier"] == None
    assert response_body["rewardTierName"] == None

    # The Customer should have been saved to the database
    assert db.customers.count_documents({"email": payload["email"]}) == 1

    customer = db.customers.find_one({"email": payload["email"]}, {"_id": 0})
    assert customer["rewardPoints"] == 99
    assert customer["rewardTier"] is None
    assert customer["rewardTierName"] is None
    assert customer["nextRewardTier"] == "A"
    assert customer == response_body

def test_create_customer_with_order_total_more_than_1000(base_url, db):
    """
    Test POST /customers endpoint

    - The status code should be 201 (Created)
    - The order total should be rounded down for the user's reward points
    - A Customer should be created
    - The Customer should not have a rewardsTier
    - The nextRewardsTier should be 'A'
    - The Customer should be saved in the Tests DB customers collection
    """
    payload = {
        "email": "tester@urbn.com",
        "orderTotal": 1200
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 201
    assert response_body["rewardPoints"] == MAXIMUM_POINTS
    assert response_body["rewardTier"] == "J"
    assert response_body["rewardTierName"] == "50% off purchase"

    # The Customer should have been saved to the database
    assert db.customers.count_documents({"email": payload["email"]}) == 1

    customer = db.customers.find_one({"email": payload["email"]}, {"_id": 0})
    assert customer["rewardPoints"] == MAXIMUM_POINTS
    assert customer["rewardTier"] == "J"
    assert customer["rewardTierName"] == "50% off purchase"
    assert customer == response_body

def test_create_customer_has_next_reward_data(base_url, db):
    """
    Test POST /customers endpoint

    - The status code should be 201 (Created)
    - The order total should be rounded down for the user's reward points
    - A Customer should be created
    - The Customer should not have a rewardsTier
    - The nextRewardsTier should be 'A'
    - The Customer should be saved in the Tests DB customers collection
    """
    payload = {
        "email": "tester@urbn.com",
        "orderTotal": 450
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 201
    assert response_body["rewardPoints"] == payload["orderTotal"]
    assert response_body["rewardTier"] == "D"
    assert response_body["rewardTierName"] == "20% off purchase"
    assert response_body["nextRewardTier"] == "E"
    assert response_body["nextRewardTierProgress"] == 0.5


    # The Customer should have been saved to the database
    assert db.customers.count_documents({"email": payload["email"]}) == 1

    customer = db.customers.find_one({"email": payload["email"]}, {"_id": 0})
    assert customer["rewardPoints"] == payload["orderTotal"]
    assert customer["rewardTier"] == "D"
    assert customer["rewardTierName"] == "20% off purchase"
    assert customer["nextRewardTier"] == "E"
    assert customer["nextRewardTierProgress"] == 0.5
    
    assert customer == response_body

def test_create_customer_on_existing_customer_returns_409(base_url, db):
    """
    Test POST /customers endpoint

    - The status code should be 409 (CONFLICT)
    - The response should include a route to the PUT method in the meta
    """
    # Add the existing customer to the Tests DB (removed again after the test by the clean_customers fixture)
    db.customers.insert_one({"email": "tester@urbn.com", "rewardPoints": 99, "rewardTier": None, "rewardTierName": None})

    payload = {
        "email": "tester@urbn.com",
        "orderTotal": 99
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response_body["meta"]["url"] == f"/customers/{payload['email']}"

    assert response.status_code == 409
    assert db.customers.count_documents({"email": payload["email"]}) == 1

def test_create_customer_with_invalid_email_fails_validation(base_url):
    """
    Test POST /customers endpoint

    - An invalid email should 422
    - error_code should be 001
    """
    payload = {
        "email": "tester.urbn.com",
        "orderTotal": 99.99
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 422
    assert response_body["error_code"] == "001"

def test_create_customer_with_invalid_order_total_fails_validation(base_url):
    """
    Test POST /customers endpoint

    - An orderTotal doesn't represent a monetary value should 422
    - error_code should be 002
    """
    payload = {
        "email": "tester@urbn.com",
        "orderTotal": 99.997
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    response_body = response.json()
    
    assert response.status_code == 422
    assert response_body["error_code"] == "002"

def test_create_customer_with_negative_number_fails_validation(base_url):
    """
    Test POST /customers endpoint

    - An negative number should 422
    - error_code should be 003
    """
    payload = {
        "email": "tester@urbn.com",
        "orderTotal": -1.00
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    response_body = response.json()
    
    assert response.status_code == 422
    assert response_body["error_code"] == "003"

def test_create_customer_with_invalid_payload_fails_validation_with_two_errors(base_url):
    """
    Test POST /customers endpoint

    - An invalid email should 422
    - An orderTotal doesn't represent a monetary value should 422
    - response.body.errors should be equal to 2
    """
    payload = {
        "email": "tester.urbn.com",
        "orderTotal": 99.997
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    assert response.status_code == 422

    body = response.json()

    assert len(body['errors']) == 2