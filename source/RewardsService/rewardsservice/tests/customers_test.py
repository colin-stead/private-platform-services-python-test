"""
Customers handler test files.
"""
import requests

def test_get_customers(base_url):
    response = requests.get(f"{base_url}/customers")
    assert response.status_code == 200

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
        "email": "tester@gmail.com",
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

def test_create_customer_on_existing_customer_returns_409(base_url, db):
    """
    Test POST /customers endpoint

    - The status code should be 200 (OK)
    - The order total should be customer's reward points + orderTotal (rounded down)
    - The Customer should be updated, not created
    """
    # Add the existing customer to the Tests DB (removed again after the test by the clean_customers fixture)
    db.customers.insert_one({"email": "tester@gmail.com", "rewardPoints": 99, "rewardTier": None, "rewardTierName": None})

    payload = {
        "email": "tester@gmail.com",
        "orderTotal": 99
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    response_body = response.json()

    assert response.status_code == 409
    assert db.customers.count_documents({"email": payload["email"]}) == 1

def test_create_customer_with_invalid_email_fails_validation(base_url):
    """
    Test POST /customers endpoint

    - An invalid email should 422
    """
    payload = {
        "email": "tester.mail.com",
        "orderTotal": 99.99
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    assert response.status_code == 422

def test_create_customer_with_invalid_order_total_fails_validation(base_url):
    """
    Test POST /customers endpoint

    - An orderTotal doesn't represent a monetary value should 422
    """
    payload = {
        "email": "tester@gmail.com",
        "orderTotal": 99.997
    }

    response = requests.post(f"{base_url}/customers", json=payload)
    assert response.status_code == 422

def test_create_customer_with_invalid_payload_fails_validation_with_two_errors(base_url):
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

    response = requests.post(f"{base_url}/customers", json=payload)
    assert response.status_code == 422

    body = response.json()

    assert len(body['errors']) == 2