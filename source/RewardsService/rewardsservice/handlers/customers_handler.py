"""
Request handler for multiple customers.

GET /customers
GET /customers/{customer_email}
POST /customers
"""
import json
import math
import validators
import os

import database

from pymongo import errors, DESCENDING, ASCENDING
from .base_handler import BaseHandler
from models.customers import Customer
from urllib.parse import urlencode

MINIMUM_REWARDS = 100
MAXIMUM_REWARDS = 1000

DB = database.get_db()
CUSTOMER = Customer()

def _validate_customers_request(data):
    """
    Validate request payloads for the create customer endpoint.

    Parameters:
        data (dict): The request body in a single dictionary

    Returns:
        dict: Error code dict to use for response or validated data to build customer document with.
    """
    validation_errors = {}

    # Validate email, update message + errors array if invalid
    if not validators.email(data["email"]):
        validation_errors["message"] = "Invalid email."
        validation_errors["error_code"] = "001"
        validation_errors["errors"] = {"email": ["The given email is invalid."]}

    if data['orderTotal'] < 0:
        if "message" in validation_errors.keys():
            validation_errors["message"] = f"{validation_errors['message'][:-1]} and 1 more."
        else:
            validation_errors["message"] = "Invalid monetary value."
            validation_errors["error_code"] = "002"


        error_row = {"orderTotal": ["The monetary value is invalid. Must be positive"]}
        validation_errors["errors"] = (
            validation_errors["errors"] | error_row
            if "errors" in validation_errors.keys()
            else error_row
        )
        return validation_errors

    # Format the order total to make sure it's a valid monetary value. Only 2 decimal places, round down any trailing decimals.
    total_to_format = (math.floor(data['orderTotal'] * 100) / 100)
    formatted_order_total = f"{total_to_format:.2f}"
    
    # Validate orderTotal, update message + errors array if invalid. Passed value should be same length as formatted.
    if len(str(data["orderTotal"])) > len(formatted_order_total):
        if "message" in validation_errors.keys():
            validation_errors["message"] = f"{validation_errors['message'][:-1]} and 1 more."
        else:
            validation_errors["message"] = "Invalid monetary value."
            validation_errors["error_code"] = "003"

        error_row = {"orderTotal": ["The monetary value is invalid. Round to nearest cent."]}
        validation_errors["errors"] = (
            validation_errors["errors"] | error_row
            if "errors" in validation_errors.keys()
            else error_row
        )

    # Return 422 payload
    return validation_errors if len(validation_errors) > 0 else data

def _validate_customers_post_request(data):
    """
    Validate customers request for POST Method

    Parameters:
        data (dict): The incoming payload

    Returns:
        dict: Error code dict to use for response or validated data to build customer document with.

    See Also:
        _validate_customers_request() (line 22)
    """
    # Check for 422 errors
    validated = _validate_customers_request(data)
    if "errors" in validated.keys():
        return validated

    # Check if incoming customer exists
    existing_customer = DB.customers.find_one({"email": data["email"]})

    # Return 409 payload if customer exists
    if existing_customer:
        return {
            "message": f"Cannot create Customer. Customer with email: {data['email']} already exists.",
            "meta": {
                "message": "Use the PUT method to update the Customer's rewards.",
                "method": "PUT",
                "url": f"/customers/{data['email']}" # TODO: Implement PUT method.
            }
        }

    # Return validated data
    return data

def _build_filters(handler):
    """
    Build filters for query/pagination

    Parameters:
        handler (CustomersHandler): The handler object so we can get argument key values
    
    Returns:
        dict: The arguments fitting accepted filters, and pagination fields
    """
    # Only accepting two arguments
    accepted_arguments = [
        "rewardTier",
        "rewardPoints",
    ]

    accepted_sorts = [
        "-_id",
        "_id",
        "-rewardPoints",
        "rewardPoints",
        "-rewardTier",
        "rewardTier",
        "-nextRewardTierProgress",
        "nextRewardTierProgress"
    ]

    # Gather arguments
    arguments = handler.request.query_arguments
    page = handler.get_argument("page", default=1)
    perPage = handler.get_argument("perPage", default=10)
    sort = handler.get_argument("sort", default="-_id")


    pagination_fields = {
        'sort': sort if sort in accepted_sorts else "-_id",
        'page': int(page) if "page" in arguments.keys() and page.isdigit() else 1,
        'perPage': int(perPage) if "perPage" in arguments.keys() and perPage.isdigit() else 10
    }

    arguments = {}
    for key in handler.request.arguments.keys():
        if "[" in key:
            start = key.index("[")
            end = key.index("]")
            arg_key = key[:start]
        
            if arg_key in accepted_arguments:
                value = handler.get_argument(key, default=None)
                if (value.isdigit()): # Store with gt/gte/lt/lte args
                    arguments[arg_key] = {f"${key[(start + 1):end]}": int(value)}
        elif key in accepted_arguments:
            value = handler.get_argument(key, default=None)
            if (value.isdigit()): # Convert to int
                arguments[key] = int(value)
            elif value: # Only except args with values, ignore empty fields
                arguments[key] = value

    return {
        "arguments": arguments,
        "pagination_fields": pagination_fields
    }

class CustomersHandler(BaseHandler):

    async def get(self, email):
        """
        Get all the customers.

        Supports endpoints: GET /customers, GET /customers/{customer_email}

        Parameters:
            email (str): The email of the customer to find (OPTIONAL)

        See also:
            __build_filters(handler) (line:99)
            models.customers.get(<dict>) (models.customers:line 128)
        """
        # Send json of customers if they're in the db, otherwise empty 200 response
        try:
            if not email:
                filters = _build_filters(self)
                arguments, pagination_fields = filters["arguments"], filters["pagination_fields"]

                customers = CUSTOMER.get(arguments | pagination_fields)
                count = customers["count"]

                # Build pagination data
                prev_pagination = {}
                next_pagination = {}
                for key, value in pagination_fields.items():
                    if (key == "page"):
                        prev_pagination[key] = value - 1
                        next_pagination[key] = value + 1
                        continue

                    prev_pagination[key] = value
                    next_pagination[key] = value

                page_count = (count + pagination_fields["perPage"] - 1) // pagination_fields["perPage"]

                self.write({
                    "data": customers["data"],
                    "meta": {
                        "page": pagination_fields["page"],
                        "perPage": pagination_fields["perPage"],
                        "count": count,
                        "pages": page_count,
                        "prev": None if prev_pagination["page"] == 0 else f"{os.getenv('URI')}/customers?{urlencode(arguments | prev_pagination)}",
                        "next": None if next_pagination["page"] > page_count else f"{os.getenv('URI')}/customers?{urlencode(arguments | next_pagination)}"
                    }
                })
            else:
                # Implement email logic here, for now return first where email is email
                customer = CUSTOMER.find(email)

                # Return 404 (NOT FOUND) if customer isn't found 
                if customer == None:
                    self.set_status(404)
                    self.write({
                        "error": "404 Not Found",
                        "message": "Customer not found"
                    })
                    return

                self.write(json.dumps(customer, indent=4))
        except (errors.CollectionInvalid, TypeError):
            # Return an empty json response if nothing's been created yet
            self.write({})

    async def post(self, _):
        """
        Create a customer with customer rewards.

        Endpoint:
            POST /customers

        See Also:
            - _validate_customers_request(<dict>) (line 18)
            - models.customers.save(<dict>) (models.customers:line 92)
        """
        customer_data = json.loads(self.request.body)

        # Validate the request
        validated = _validate_customers_post_request(customer_data)

        # Return 409 CONFLICT if the customer exists
        if 'meta' in validated.keys():
            self.set_status(409)
            self.write(validated)
            return

        # Return 422 if the errors exist in the valdated data
        if 'errors' in validated.keys():
            self.set_status(422)
            self.write(validated)
            return

        # Create a new customer
        response = CUSTOMER.save(validated)

        # Set the status to 201 return data
        self.set_status(201)
        self.write(json.dumps(response, default=str))

