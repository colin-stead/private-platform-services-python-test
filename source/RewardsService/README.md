# Objective
Create RESTful endpoint(s) to calculate, store, and retrieve customer rewards data from MongoDB.

# Background
* You will be using the [Tornado](http://www.tornadoweb.org) Python web framework and a MongoDB docker image.
* When starting up the 'rewardsservice' docker container in the [Setup](#setup) below, a mongo 'Rewards' database will be created for you with a "rewards" collection containing each reward a user can earn and how many points are needed to reach each reward.
    ```
    [
        { "tier": "A", "rewardName": "5% off purchase", "points": 100 },
        { "tier": "B", "rewardName": "10% off purchase", "points": 200 },
        { "tier": "C", "rewardName": "15% off purchase", "points": 300 },
        { "tier": "D", "rewardName": "20% off purchase", "points": 400 },
        { "tier": "E", "rewardName": "25% off purchase", "points": 500 },
        { "tier": "F", "rewardName": "30% off purchase", "points": 600 },
        { "tier": "G", "rewardName": "35% off purchase", "points": 700 },
        { "tier": "H", "rewardName": "40% off purchase", "points": 800 },
        { "tier": "I", "rewardName": "45% off purchase", "points": 900 },
        { "tier": "J", "rewardName": "50% off purchase", "points": 1000 }
    ]
    ```

# Instructions:
* Design and implement the following endpoints.
    * **Endpoint 1:**
        * Accept a customer's order data: **email adress**  (ex. "customer01@gmail.com") and **order total** (ex. 100.80).
        * Calculate and store the following customer rewards data into MongoDB. For each dollar a customer spends, the customer will earn 1 reward point. For example, an order of $100.80 earns 100 points. Once a customer has reached the top rewards tier, there are no more rewards the customer can earn.
            * **Email Address:** the customer's email address (ex. "customer01@gmail.com")
            * **Reward Points:** the customer's rewards points (ex. 100)
            * **Reward Tier:** the rewards tier the customer has reached (ex. "A")
            * **Reward Tier Name:** the name of the rewards tier (ex. "5% off purchase")
            * **Next Reward Tier:** the next rewards tier the customer can reach (ex. "B")
            * **Next Reward Tier Name:** the name of next rewards tier (ex. "10% off purchase")
            * **Next Reward Tier Progress:** the percentage the customer is away from reaching the next rewards tier (ex. 0.5)
    * **Endpoint 2:** Accept a customer's email address, and return the customer's rewards data that was stored in Endpoint 1.
    * **Endpoint 3:** Return the same rewards data as Endpoint 2 but for all customers.
* Add error handling and unit tests.

# Setup
* Install docker and docker-compose dependencies.
* $ cd APP_PATH/platform-services-python-test/source/RewardsService
* $ docker-compose build
* $ docker-compose up -d
* Services are accessible at http://localhost:7050/

# Solution

Setup stays the same with the following packages added to [requirements.txt](requirements.txt)
* `validators 0.35.0` for customer email validation without a need for regex. In a real setting this could be used for initial validation but ultimately a confirmation email would need to be sent to the user to validate the email.
* `pytest 9.2.0` for unit testing.
* `requests 2.34.2` for hitting endpoints in pytest.

I also upgraded tornado to 6.5.10.

# Testing
Tests run with `pytest` on your machine (not inside docker) against a separate **`Tests`** MongoDB database, so the `Rewards` database used by the service on `http://localhost:7050` is never touched. `conftest.py` starts its own copy of the service on **port 7051** that is pointed at the `Tests` database.

### Prerequisites
* The MongoDB container is running with port `27017` published: `cd source/RewardsService && docker-compose up -d`. The service on port 7050 does not need to be running for the tests.
* A Python virtual environment with the pinned dependencies (an older tornado raises a `DeprecationWarning` on Python 3.14):
    ```
    python -m venv .venv
    source .venv/bin/activate
    pip install -r source/RewardsService/requirements.txt
    ```
* Port `7051` is free.

### Run the tests
```
cd source/RewardsService
pytest rewardsservice/tests -v
```

### What the tests do
* The `rewards` collection in the `Tests` database is reloaded with the same data as `load_mongo_data.py` at the start of each run.
* The `customers` collection is emptied before and after every test, and dropped when the run finishes, so tests never see data from other tests or earlier runs. The `rewards` collection stays in the `Tests` database.

### Configuration
Database settings are environment variables read in `source/RewardsService/database.py`:

| Variable | Default | Under pytest |
| --- | --- | --- |
| `MONGO_HOST` | `mongodb` (docker compose service name) | `localhost` (override if Mongo is elsewhere) |
| `MONGO_PORT` | `27017` | `27017` |
| `DB_NAME` | `Rewards` | `Tests` (always) |

If you have more than one container engine installed (for example Rancher Desktop and Docker Desktop), make sure the MongoDB that owns host port `27017` is the one you expect.

# Endpoints
* `POST /customers`
    * Creates a new customer in the Rewards DB under the customers collection. Updates the Customer if the Customer already exists.
    * Response Codes 201, 409, and 422
    * Example 201 Response:
        ```
        {
            "email": "test.customer@urbn.com",
            "orderTotal": 103.78,
            "rewardPoints": 103,
            "rewardTier": "A",
            "rewardTierName": "5% off purchase",
            "nextRewardTier": "B",
            "nextRewardTierProgress": 0.97
        }
        ```
    * Example 409 Response:
        ```
        {
            "message": "Cannot create Customer. Customer with email: colin@urbn.com already exists.",
            "meta": {
                "message": "Use the PUT method to update the Customer's rewards.",
                "method": "PUT",
                "url": "/customers/colin@urbn.com"
            }
        }
        ```
     * Example 422 Response:
        ```
        {
            "message": "Invalid email. and 1 more.",
            "errors": {
                "email": [
                    "The given email is invalid."
                ],
                "orders": [
                    "The monetary value is invalid. Round to nearest cent."
                ]
            }
        }
        ```

* `GET /customers`
    * Gets a list of all the customers that are in the database.
    * Response Codes 200
    * Example 200 Response:
        ```
        [
            {
                "email": "jackie@urbn.com",
                "nextRewardTier": null,
                "nextRewardTierProgress": 0.99,
                "rewardPoints": 1000,
                "rewardTier": "J",
                "rewardTierName": "50% off purchase"
            },
            {
                "email": "colin@urbn.com",
                "nextRewardTier": "B",
                "nextRewardTierProgress": 0.13,
                "rewardPoints": 113,
                "rewardTier": "A",
                "rewardTierName": "5% off purchase"
            }
        ]
        ```
* `GET /customers/{customer_email}`
* `PUT /customers/{customer_email}`

# Assumptions & Tradeoffs
* On the "Create Customer" endpoint `POST /customers` I assumed we wouldn't want duplicate customers with the same IDs. So I added a 409 response and another endpoint to update customer rewards `PUT /customers/{customer_email}`. This follows best practices in API design.
* I assumed "No more rewards can be earned" also meant there's a cap to reward points a customer can earn. So for this project, once a customer hits the "J Tier", they can no longer earn more points and are capped at 1000. The POST/PUT endpoints will still return 200 OK responses but the rewards data will not change.
* On the "Get Customer Details" endpoint `GET /customers/{customer_email}` I'm not a fan of passing an email directly to the URL. In a production setting I'd opt for an ID key.
