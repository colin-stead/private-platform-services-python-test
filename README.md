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

Setup stays the same with `validators 0.35.0` added to the [requirements.txt](requirements.txt) file for customer email validation without a need for regex. In a real setting this could be used for initial validation but ultimately a confirmation email would need to be sent to the user to validate the email.

# Endpoints
* `POST /customers`
    * Creates a new customer in the Rewards DB under the customers collection. Updates the Customer if the Customer already exists.
    * Response Codes 200, 201, and 422
    * Example 201/200 Response body:
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

* `GET /customers`
* `GET /customers/{customer_email}`

# Assumptions & Tradeoffs
* On the "Create Customer" endpoint `POST /customers` I assumed we wouldn't want duplicate customers with the same IDs. Instead of adding another PUT/PATCH route and requiring the call to come from there I opted to simply update an existing customer when found.
* I assumed "No more rewards can be earned" also meant there's a cap to reward points a customer can earn. So for this project, once a customer hits the "J Tier", they can no longer earn more points and are capped at 1000.
* On the "Get Customer Details" endpoint `GET /customers/{customer_email}` I'm not a fan of passing an email directly to the URL. In a production setting I'd opt for an ID key.

# History Note

While working on this project I noticed the original repository was public. To keep my answers private I moved to a private repository. This was after I spun up the application and created the following endpoints:
* `POST /customers`
* `GET /customers`

Here's the corresponding branches and their PR Messages:

BRANCH: story/1-initialize ([PUBLIC PR LINK](https://github.com/colin-stead/platform-services-python-test/pull/5))
PR DESCRIPTION:
* Spin up the tornado server
* Familiarize self with codebase
* Add TODOs, Update .gitignore
* Add Pytest
* Add a BaseHandler to build off of so the headers come through as JSON instead of HTML project wide
* Add customers url pattern
* Add customer_handler for customer routes to be added

BRANCH: feature/2-post-customer-rewards ([PUBLIC PR LINK](https://github.com/colin-stead/platform-services-python-test/pull/6))
PR DESCRIPTION:
Added the POST endpoint for the Customer Rewards module.

* Adds `validators 0.35.0` to `requirements.txt` for initial email validation.
* Adds some updates to the README regarding my solution.
* Adds `_validate_customers_request` private function to `customers_handler.py` so we can validate request data, passes along validated data if it's clean. Sends errors back for 422 response if not.
*Adds `_build_customer_rewards` private function to `customers_handler.py` to apply calculations to validated request data for updating/creating new customers
* Implements `POST /customers` to create new customers or update customers that may have existed before.
