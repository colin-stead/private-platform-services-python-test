"""
Request handler for multiple customers.

GET /customers
GET /customers/{customer_email}
POST /customers
"""
import json
import math
import validators

import database

from pymongo import errors
from .base_handler import BaseHandler
from models.customers import Customer

MINIMUM_REWARDS = 100
MAXIMUM_REWARDS = 1000

DB = database.get_db()

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
                customers = list(DB.customers.find({}, {"_id": 0}))
                self.write(json.dumps(customers, indent=4))
            else:
                # Implement email logic here, for now return first where email is email
                self.write({})
        except (errors.CollectionInvalid, TypeError):
            # Return an empty json response if nothing's been created yet
            self.write({})

    async def post(self, _):
        """
        Create or update a customer with customer rewards. Upsert the data into the db.

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
        customer = Customer()
        response = Customer.save(customer, validated)

        # Set the status to 201 return data
        self.set_status(201)
        self.write(json.dumps(response, default=str))

