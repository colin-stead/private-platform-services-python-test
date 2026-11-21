"""
Customers handler test files.
"""
import requests

BASE_URL = "http://localhost:7050"

def test_get_customers():
    response = requests.get(f"{BASE_URL}/customers")
    assert response.status_code == 200

def test_create_customer_with_order_total_less_than_100():
    """
    Test POST /customers endpoint

    - The status code should be 201 (Created)
    - The order total should be rounded down for the user's reward points
    - A Customer should be created
    - The Customer should not have a rewardsTier
    - The nextRewardsTier should be 'A'
    """
    payload = {
        "email": "tester@gmail.com",
        "orderTotal": 99
    }

    response = requests.post(f"{BASE_URL}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 201
    assert response_body["rewardPoints"] == payload["orderTotal"]
    assert response_body["rewardTier"] == None
    assert response_body["rewardTierName"] == None

def test_create_customer_on_existing_customer_returns_200():
    """
    Test POST /customers endpoint

    - The status code should be 200 (OK)
    - The order total should be customer's reward points + orderTotal (rounded down)
    - The Customer should be updated, not created
    """
    # TODO: Add existing customer to test DB

    payload = {
        "email": "tester@gmail.com",
        "orderTotal": 99
    }

    response = requests.post(f"{BASE_URL}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 200

def test_create_customer_with_invalid_email_fails_validation():
    """
    Test POST /customers endpoint

    - An invalid email should 422
    """
    payload = {
        "email": "tester.mail.com",
        "orderTotal": 99.99
    }

    response = requests.post(f"{BASE_URL}/customers", json=payload)
    assert response.status_code == 422

def test_create_customer_with_invalid_order_total_fails_validation():
    """
    Test POST /customers endpoint

    - An orderTotal doesn't represent a monetary value should 422
    """
    payload = {
        "email": "tester@gmail.com",
        "orderTotal": 99.997
    }

    response = requests.post(f"{BASE_URL}/customers", json=payload)
    assert response.status_code == 422

def test_create_customer_with_invalid_payload_fails_validation_with_two_errors():
    """
    Test POST /customers endpoint

    - An invalid email should 422
    - An orderTotal doesn't represent a monetary value should 422
    - response.body.errors should be equal to 2
    """
    payload = {
        "email": "tester.mail.com",
        "orderTotal": 99.997
    }

    response = requests.post(f"{BASE_URL}/customers", json=payload)
    assert response.status_code == 422

    body = response.json()

    assert len(body['errors']) == 2