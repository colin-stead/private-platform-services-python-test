"""
customer_handler CustomerHandler:get() function test file.
"""
import requests
from models.customers import Customer

def test_get_customers(base_url):
    """
    Test GET /customers endpoint

    - Regular call works
    - Call with pagination filters work
    - Call with query params work
    """
    customers = [
        {"email": "tester1@urbn.com", "orderTotal": 134.00},
        {"email": "tester2@urbn.com", "orderTotal": 34.00},
        {"email": "tester3@urbn.com", "orderTotal": 234.99},
        {"email": "tester4@urbn.com", "orderTotal": 334.00},
        {"email": "tester5@urbn.com", "orderTotal": 400.76},
        {"email": "tester6@urbn.com", "orderTotal": 534.24},
        {"email": "tester7@urbn.com", "orderTotal": 634.00},
        {"email": "tester8@urbn.com", "orderTotal": 734.87},
        {"email": "tester9@urbn.com", "orderTotal": 834.00},
        {"email": "tester10@urbn.com", "orderTotal": 934.99},
        {"email": "tester11@urbn.com", "orderTotal": 1034.17},
        {"email": "tester12@urbn.com", "orderTotal": 108.00},
        {"email": "tester13@urbn.com", "orderTotal": 297.05},
        {"email": "tester14@urbn.com", "orderTotal": 678.24},
        {"email": "tester15@urbn.com", "orderTotal": 545.39},
        {"email": "tester16@urbn.com", "orderTotal": 499.46},
        {"email": "tester17@urbn.com", "orderTotal": 500.94},
        {"email": "tester18@urbn.com", "orderTotal": 934.00},
        {"email": "tester19@urbn.com", "orderTotal": 879.49},
        {"email": "tester20@urbn.com", "orderTotal": 999.06},
    ]
    customer = Customer()

    for data in customers:
        customer.save(data)

    # Test customers with no filter
    response = requests.get(f"{base_url}/customers")
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["meta"]["count"] == 20
    assert response_body["meta"]["page"] == 1
    assert response_body["meta"]["perPage"] == 10

    # Test page/perPage results
    response = requests.get(f"{base_url}/customers", params={"page": 2})
    response_body = response.json()
    assert response.status_code == 200
    assert response_body["meta"]["count"] == 20
    assert response_body["meta"]["page"] == 2
    assert response_body["meta"]["perPage"] == 10
    assert response_body["data"][0]["email"] == "tester10@urbn.com" # Default sort is id desc

    response = requests.get(f"{base_url}/customers", params={"perPage": 5})
    response_body = response.json()
    assert response.status_code == 200
    assert response_body["meta"]["count"] == 20
    assert response_body["meta"]["page"] == 1
    assert response_body["meta"]["perPage"] == 5

    # Test each sort and their expected first customer email
    sorts = {
        "-_id": "tester20@urbn.com",
        "_id": "tester1@urbn.com",
        "-rewardPoints": "tester11@urbn.com",
        "rewardPoints": "tester2@urbn.com",
        "-rewardTier": "tester11@urbn.com",
        "rewardTier": "tester2@urbn.com",
        "-nextRewardTierProgress": "tester16@urbn.com",
        "nextRewardTierProgress": "tester5@urbn.com" # None is less than any other number
    }
    
    for key, value in sorts.items():
        response = requests.get(f"{base_url}/customers", params={"sort": key})
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["meta"]["count"] == 20
        assert response_body["meta"]["page"] == 1
        assert response_body["meta"]["perPage"] == 10
        assert response_body["data"][0]["email"] == value

    # Test each filter and their expected count
    filters = {
        "rewardTier": {"filterVal": "A", "count": 2},
        "rewardTier": {"filterVal": "B", "count": 2},
        "rewardTier": {"filterVal": "C", "count": 1},
        "rewardTier": {"filterVal": "D", "count": 2},
        "rewardTier": {"filterVal": "E", "count": 3},
        "rewardTier": {"filterVal": "F", "count": 2},
        "rewardTier": {"filterVal": "G", "count": 2},
        "rewardTier": {"filterVal": "H", "count": 2},
        "rewardTier": {"filterVal": "I", "count": 2},
        "rewardTier": {"filterVal": "J", "count": 1},
        "rewardPoints": {"filterVal": 534, "count": 1},
        "rewardPoints[gte]": {"filterVal": 400, "count": 14},
        "rewardPoints[gt]": {"filterVal": 400, "count": 13},
        "rewardPoints[lte]": {"filterVal": 400, "count": 7},
        "rewardPoints[lt]": {"filterVal": 400, "count": 6},
    }

    for key, value in filters.items():
        response = requests.get(f"{base_url}/customers", params={key: value["filterVal"]})
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["meta"]["count"] == value["count"]

    # Test empty params result in 200 with data
    emptyFilters = {
        "rewardTier": "",
        "rewardPoints": "",
        "sort": "",
        "page": "",
        "perPage": "",
    }

    response = requests.get(f"{base_url}/customers", params={key: value for key, value in emptyFilters.items()})
    response_body = response.json()
    
    assert response.status_code == 200
    assert response_body["meta"]["count"] == 20
    assert response_body["meta"]["page"] == 1
    assert response_body["meta"]["perPage"] == 10

def test_we_can_find_customer_with_email(base_url, db):
    """
    Test GET /customers/{customer_email} endpoint

    - The status code should be 200 (OK)
    - The response should match data for the customer in the db
    """
    payload = {"email": "tester@urbn.com", "orderTotal": 234}

    # Create a B Tier customer, nextRewardTier will be C    
    customer = Customer()
    customer = customer.save({"email": "tester@urbn.com", "orderTotal": 234})

    response = requests.get(f"{base_url}/customers/{payload['email']}")
    response_body = response.json()

    # Assert the response body matches what is pulled from the DB
    assert response.status_code == 200
    assert response_body["rewardPoints"] == payload["orderTotal"]
    assert response_body["rewardTier"] == "B"
    assert response_body["rewardTierName"] == "10% off purchase"
    assert response_body["nextRewardTier"] == "C"

def test_we_404_when_email_is_not_in_the_database(base_url, db):
    """
    Test GET /customers/{customer_email} endpoint

    - The status code should be 200 (OK)
    - The response should match data for the customer in the db
    """
    response = requests.get(f"{base_url}/customers/tester@urbn.com")
    response_body = response.json()

    # Assert the response body matches what is pulled from the DB
    assert response.status_code == 404
    assert response_body["error"] == "404 Not Found"
    assert response_body["message"] == "Customer not found"