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