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

I also upgraded `tornado` to `6.5.10` and set debug mode to false in [settings.py](rewardsservice/settings.py)

# Assumptions & Tradeoffs
* `POST /customers`
    * I assumed we wouldn't want duplicate customers with the same emails. So I added a `409` response and another endpoint to update customer rewards `PUT /customers/{customer_email}`. This follows best practices in API design.
    * I assumed "No more rewards can be earned" also meant there's a cap to reward points a customer can earn. So for this project, once a customer hits the "J Tier", they can no longer earn more points and are capped at 1000. The POST/PUT endpoints will still return 200 OK responses but the rewards data will not change.
    * I assumed rewardPoints must be >= 0.
    * I assumed ints were acceptable for the orderTotal as well. Floats are accepted as long as the decimal does not exceed the hundreths place.
* `GET /customers/{customer_email}`
    * I'm not a fan of passing an email directly to the URL. In a production setting I'd opt for an ID key.
* `GET /customers`
    * I assumed default sorting should be most recently added customer to oldest customer on `GET /customers` so the default sort is descending on the `_id` key.
    * No server side caching. Takes advantage of Tornado's built in etag handling. In a production setting I'd prefer to cache the results of heavily trafficked endpoints like server side with something like Redis.
    * Assumed filtering and pagination were desired and added it.
* Authentication
    * Nothing was in the spec on authentication. So I didn't set up any API Keys or User accounts. In a production setting these are things that would be added.
* [Documentation](#endpoint-documentation)
    * I only included docs in the README files. In a production setting I'd use something like Swagger for documentation. FastAPI supports this out of the box, unsure if there's a good tornado plugin or not.
* UI
    * I opted not to make a UI for this project. I had too much fun with the backend REST API and opted to improve it instead.

# Testing
Tests run with `pytest` on your machine (not inside docker) against a separate **`Tests`** MongoDB database, so the `Rewards` database used by the service on `http://localhost:7050` is never touched. `conftest.py` starts its own copy of the service on **port 7051** that is pointed at the `Tests` database.

### Prerequisites
* The MongoDB container is running with port `27017` published: `cd source/RewardsService && docker-compose up -d`. The service on port 7050 does not need to be running for the tests.
* From the root directory (directory just one step above source) run the following commands to create a Python virtual environment with the pinned dependencies (an older tornado raises a `DeprecationWarning` on Python 3.14):
    * For MacOS
        ```
        python -m venv .venv
        source .venv/bin/activate
        pip install -r source/RewardsService/requirements.txt
        ```
    * For Windows
        ```
        python -m venv .venv
        ./venv/Scripts/Activate.ps1
        pip install -r source/RewardsService/requirements.txt
        ```
* Port `7051` is free.

### Run the tests from inside the virtual environment
```
cd source/RewardsService
pytest
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

# DB Cleanup
* When the rewardsservice container stops running the `customers` collection persists. So restarting the container doesn't wipe data. To get a clean slate run `docker-compose down -v` Then run `docker-compose build && docker-compose up -d`

# Endpoint Documentation
* `POST /customers`
    * Creates a new customer in the Rewards DB under the `customers` collection. 409s if the customer exists
    * Request Body accepts:
        * `email` - a string, the customer's email
        * `orderTotal` - a number with no more than 2 digits after the decimal. A monetary value. No negatives.
    * Request Body Example:
        {
            "email": "colin@urbn.com",
            "orderTotal": 200.98
        }
    * Response Codes `201`, `409`, and `422`
    * `422` reasons:
        * Invalid email (`error_code: 001`)
        * Invalid orderTotal (`error_code: 002`)
        * Negative orderTotal (`error_code: 003`)
    * Example `201` Response:
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
    * Example `409` Response:
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
     * Example `422` Response:
        ```
        {
            "message": "Invalid email and 1 more.",
            "error_code": "001",
            "errors": {
                "email": [
                    "The given email is invalid."
                ],
                "orderTotal": [
                    "The monetary value is invalid. Round to nearest cent."
                ]
            }
        }
        ```

* `GET /customers`
    * Gets a list of all the customers that are in the database.
    * Accepts Following Filters:
        * `sort` - The key to sort on. ACCEPTED VALUES: [`-_id`, `_id`, `-rewardPoints`, `rewardPoints`, `-rewardTier`, `rewardTier`, `-nextRewardTierProgress`, `nextRewardTierProgress`]
        * `rewardTier` - char ranging from A - J. Must be uppercase. Anything else will return nothing.
        * `rewardPoints` - The rewardPoint value. This can also be passed as `rewardPoints[lt]` (for less than a value), `rewardPoints[gt]` (for greater than a value), `rewardPoints[lte]` (for less than or equal to a value), `rewardPoints[gte]` (for greater than or equal to a value) or whatever other comparison you'd like to make between the braces.
    * Uses Tornado's default etag handling and passes an etag in the response header.
    * Response Codes `200`, `304`
    * Example `200` Response Body (with data in DB):
        ```
        {
            "data": [
                {
                    "email": "dawn@urbn.com",
                    "nextRewardTier": "I",
                    "nextRewardTierProgress": 0.49,
                    "rewardPoints": 849,
                    "rewardTier": "H",
                    "rewardTierName": "40% off purchase"
                },
                {
                    "email": "sam@urbn.com",
                    "nextRewardTier": "I",
                    "nextRewardTierProgress": 0.45,
                    "rewardPoints": 845,
                    "rewardTier": "H",
                    "rewardTierName": "40% off purchase"
                }
            ],
            "meta": {
                "page": 2,
                "perPage": 2,
                "count": 11,
                "pages": 6,
                "prev": "http://localhost:7050/customers?sort=-_id&page=1&perPage=2",
                "next": "http://localhost:7050/customers?sort=-_id&page=3&perPage=2"
            }
        }
        ```
    * Example `200` Response Body (without data in DB):
        ```
        {
            "data": [],
            "meta": {
                "page": 1,
                "perPage": 10,
                "count": 0,
                "pages": 0,
                "prev": null,
                "next": null
            }
        }
        ```
* `GET /customers/{customer_email}`
    * Get a customer from the database by their email
    * Uses Tornado's default etag handling and passes an etag in the response header.
    * Response Codes `200`, `304`, `404`
    * Example `200` Response:
        ```
        {
            "email": "colin@gmail.com",
            "nextRewardTier": "B",
            "nextRewardTierProgress": 0.13,
            "rewardPoints": 113,
            "rewardTier": "A",
            "rewardTierName": "5% off purchase"
        }
        ```
    * Example `404` Response:
        ```
        {
            "error": "404 Not Found",
            "message": "Customer not found"
        }
        ```
* `PUT /customers/{customer_email}`
    * Update a customer in the database given their email
    * Request Body accepts:
        * `email` - a string, the customers email
        * `orderTotal` - a number with no more than 2 digits after the decimal. A monetary value. Negatives are allowed
    * Request Body Example:
        ```
        {
            "email": "colin@urbn.com",
            "orderTotal": 200.98
        }
        ```
    * Response codes `200`, `404`, `422`
    * Example `200` Response:
        ```
        {
            "email": "colin@gmail.com",
            "nextRewardTier": "B",
            "nextRewardTierProgress": 0.13,
            "rewardPoints": 313,
            "rewardTier": "C",
            "rewardTierName": "15% off purchase"
        }
        ```
    * Example `404` Response:
        ```
        {
            "error": "404 Not Found",
            "message": "Customer not found"
        }
        ```
    * Example `422` Response:
        ```
        {
            "message": "Invalid monetary value.",
            "error_code": "002",
            "errors": {
                "orderTotal": [
                    "The monetary value is invalid. Round to nearest cent."
                ]
            }
        }
        ```

## Manual Usage of API
* I included json file called [Urbn-openapi.json](Urbn-openapi.json) in the root directory. You can import this file to [hoppscotch.io](https://hoppscotch.io/) via Import > "Import from OpenAPI" or another REST Client that accepts the JSON file and test for yourself. Otherwise you can curl endpoints as you'd like.

### curl GET /rewards
```
curl "http://localhost:7050/rewards"
```

### curl GET /customers
For the generic /customers endpoint run
```
curl "http://localhost:7050/customers"
```

To filter/paginate pass the params in place of {key} replace the key you want to filer on and in place of value replace the value you want for the filter
```
curl "http://localhost:7050/customers" \
    --url-query "{key}={value}"
```
Example:
```
curl "http://localhost:7050/customers" \
    --url-query "rewardPoints[gt]=400" \
    --url-query "sort=-rewardPoints"
```

### curl GET /customers/{customer_email}
For the generic /customers endpoint replace the {customer_email} with the email you'd like to search and run
```
curl "http://localhost:7050/customers/{customer_email}"
```
Example:
```
curl "http://localhost:7050/customers/colin@urbn.com"
```

### curl POST /customers
```
curl -X POST http://localhost:7050/customers \
    -d '{"email": "colin@urbn.com", "orderTotal": 849.06}'
```

### curl PUT /customers
```
curl -X PUT http://localhost:7050/customers \
    -d '{"email": "colin@urbn.com", "orderTotal": 849.06}'
```
