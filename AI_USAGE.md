# AI Usage Disclosure

**Did you use AI tools for this exercise?** Yes

## Tools and models
Claude Sonnet 5.5

## Prompts
### PROMPT 1:

"I need to configure a testing environment for my workspace. The testing
environment will be a separate database in MongoDB from the DB that is used
against the localhost:7050 server. The DB is on a docker container.

If you look at @source/RewardsService/rewardsservice/handlers/base_handler.py
you will see that the DB configuration is done there so customers_handler
and rewards_handler know which DB to communicate with. I'd like to move this
to variables in os.environ from database.py. This way the tests/ folder will
be able to change to the "Tests" DB from the "Rewards" DB and have the
endpoints alter data in the "Tests" DB when pytest runs.

The "Tests" DB should be populated with the same rewards data in
@source/RewardsService/load_mongo_data.py  we can leave this in the "Tests"
db, however the customers collection should be dropped at the end of each
test run so it's empty whenever the tests occur. This way we will not see
unexpected responses with the test data we hit the endpoints with.

Help me update the database setup and references and get the tests working
with the database. In test_create_customer_with_order_total_less_than_100 add
assertions against the database and run pytest to confirm it works once the
changes are in. If those fail to run against the database. Tell me the error
so I can review it and propose a solution to fix it then we will go from
there."

### PROMPT 2 (same session)

"You can add these in the readme under a new section called "Testing". Put it under Solution section. This will go in @README.md  and  @source/RewardsService/README.md

There's a warning lingering on the tests and it stems from @source/RewardsService/rewardsservice/tests/conftest.py I believe the issue lives in the serve() function in test_server(). Here's the error:
rewardsservice/tests/customers_test.py::test_get_customers
  /Users/colinstead/Projects/urbn/platform-services-python-test/.venv/lib/python3.14/site-packages/tornado/platform/asyncio.py:371: DeprecationWarning: 'asyncio.DefaultEventLoopPolicy' is deprecated and slated for removal in Python 3.16
    _BasePolicy = asyncio.DefaultEventLoopPolicy

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
First diagnose why the warning is showing and the changes required to fix it. Let me know if it is a breaking change or not and what updates we would need to make to the README files." 


## How you used them
Testing database configuration and pytest warning cleanup

## What you changed or rejected
Claude put the CLIENT config in the base_handler.py file. I changed that to be get_client() in database.py and moved client refrences in handlers/customer_handler.py to models/customer.py.
