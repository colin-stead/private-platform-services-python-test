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
        validation_errors["errors"] = {"email": ["The given email is invalid."]}

    # Format the order total to make sure it's a valid monetary value. Only 2 decimal places, round down any trailing decimals.
    total_to_format = (math.floor(data['orderTotal'] * 100) / 100)
    formatted_order_total = f"{total_to_format:.2f}"
    
    # Validate orderTotal, update message + errors array if invalid. Passed value should be same length as formatted.
    if len(str(data["orderTotal"])) > len(formatted_order_total):
        if "message" in validation_errors.keys():
            validation_errors["message"] += " and 1 more."
        else:
            validation_errors["message"] = "Invalid monetary value."

        error_row = {"orders": ["The monetary value is invalid. Round to nearest cent."]}
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

class CustomersHandler(BaseHandler):

    async def get(self, email):
        """
        Get all the customers

        Supports endpoints: GET /customers, GET /customers/{customer_email}
        TODO: Add filtering, pagination, Support for single customer
        """
        # Send json of customers if they're in the db, otherwise empty 200 response
        try:
            if not email:
                accepted_arguments = [
                    "rewardTier",
                    "rewardPoints",
                ]

                arguments = self.request.query_arguments
                pagination_fields = {
                    'sort': self.get_argument("sort") if "sort" in arguments.keys() else "-_id",
                    'page': self.get_argument("page") if "page" in arguments.keys() else 1,
                    'perPage': self.get_argument("perPage") if "perPage" in arguments.keys() else 10
                }

                arguments = {}
                for key in self.request.arguments.keys():
                    if "[" in key:
                        start = key.index("[")
                        end = key.index("]")
                        arg_key = key[:start]
                    
                        if arg_key in accepted_arguments:
                            arguments[arg_key] = {f"${key[(start + 1):end]}": int(self.get_argument(key))}
                    elif key in accepted_arguments:
                        arguments[key] = self.get_argument(key, default=None)
                    
                sort_order = DESCENDING if pagination_fields["sort"][0] == '-' else ASCENDING
                sort = pagination_fields["sort"] if sort_order == ASCENDING else pagination_fields["sort"][1:]

                print(arguments)

                query = (
                    DB.customers.find(arguments, {"_id": 0})
                        .sort(sort, sort_order)
                        .skip((pagination_fields["page"] - 1) * pagination_fields["perPage"])
                        .limit(pagination_fields["perPage"])
                )

                customers = list(query)
                count = DB.customers.count_documents(arguments)

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
                    "data": customers,
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

