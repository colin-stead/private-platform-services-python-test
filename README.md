# Objective
* Create RESTful endpoint(s) to expose Rewards Data.
* Create an algorithm to calculate a user's rewards points.
* Create a Customer Rewards Dashboard Application.

# Instructions
* [Fork this repo.](https://help.github.com/articles/fork-a-repo/)
* Install the [Dependencies](#dependencies) below.
* Follow the instructions in these 2 projects in the following order:
    1. [RewardsService](https://github.com/URBN-Interview/platform-services-python-test/tree/master/source/RewardsService)(required)
    2. [RewardsUI](https://github.com/URBN-Interview/platform-services-python-test/tree/master/source/RewardsUI) (optional)
* Follow python best practices, and ensure endpoints are RESTFul
* Make sure to read up on tornado, mongo db, RESTFul APIs if you are not familiar with the concepts or technologies
* Use incremental commits on a story branch to show how you arrived at your solutions.
* Complete [AI_USAGE.md](AI_USAGE.md) at the root of the repo. If you used AI tools, include the tools and models, your prompts (or a conversation export), and how you used them. If you didn't use AI, say so in that file.
* Push your story branch to your fork.
* [Issue a pull request](https://help.github.com/articles/using-pull-requests/) against the master branch of this repo.

# Dependencies
### Docker
* Install [Rancher Desktop](https://rancherdesktop.io/) 

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
    * Example 200 Response (with data in DB):
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
    * Example 200 Response (without data in DB):
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
    * Get a customer from the database with their email
    * Response Codes 200, 404
    * Example 200 Response:
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
    * Example 404 Response:
        ```
        {
            "error": "404 Not Found",
            "message": "Customer not found"
        }
        ```
* `PUT /customers/{customer_email}`

# Assumptions & Tradeoffs
* On the "Create Customer" endpoint `POST /customers` I assumed we wouldn't want duplicate customers with the same IDs. So I added a 409 response and another endpoint to update customer rewards `PUT /customers/{customer_email}`. This follows best practices in API design.
* I assumed "No more rewards can be earned" also meant there's a cap to reward points a customer can earn. So for this project, once a customer hits the "J Tier", they can no longer earn more points and are capped at 1000. The POST/PUT endpoints will still return 200 OK responses but the rewards data will not change.
* On the "Get Customer Details" endpoint `GET /customers/{customer_email}` I'm not a fan of passing an email directly to the URL. In a production setting I'd opt for an ID key.
