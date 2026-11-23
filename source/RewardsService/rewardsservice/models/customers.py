"""
Request handler for multiple customers.

GET /customers
GET /customers/{customer_email}
POST /customers
"""
import math
import pymongo

import database

from pymongo import MongoClient

CUSTOMER_COLLECTION = "customers"
REWARDS_COLLECTION = "rewards"
MINIMUM_REWARDS = 100
MAXIMUM_REWARDS = 1000

class Customer:
    """
    A model to represent a Customer document
    """

    def __init__(self):
        self._client = database.get_client()
        self._db = database.get_db()

        self._collection = self._db.get_collection(CUSTOMER_COLLECTION)
        self._collection.create_index("email", unique=True) # Faster lookups on email, email must be unique

        self._rewards = self._rewards = self._db.get_collection(REWARDS_COLLECTION)
        self._rewards.create_index("rewardPoints") # Faster lookups on rewardPoints

    def _build_customer_rewards(self, validated_data):
        """
        Gets reward data for a customer based on their order totals and existing points.

        Parameters:
            validated_data (dict): The order data to build a Customer with, validated in _validate_customers_request
            which contains two items:
                - "order_total" (int/float): The total value of the order
                - "email" (str): The user email

        Returns:
            dict: A dictionary with the customer's email and reward-based data.

        See Also:
            _validate_customers_request(<dict>) (line 18)
        """
        # Find potential existing customer
        email = validated_data["email"]
        existing_customer = self._collection.find_one({"email": email})

        # Add total to points on existing customer's account if they exist, otherwise just use the order total
        total_points = math.floor(
            validated_data["orderTotal"] + existing_customer["rewardPoints"]
            if existing_customer
            else validated_data["orderTotal"]
        )

        # Nearest reward point total will always be an integer, rounded down to the nearest hundred
        reward_points = min(int((total_points // MINIMUM_REWARDS) * 100), MAXIMUM_REWARDS)

        # If the reward points are under the first tier the user should have None.
        if reward_points < MINIMUM_REWARDS:
            current_reward, next_reward = None,  self._rewards.find_one({"points": {"$gte": reward_points}})
        else:
            # Find the relevant reward and the next reward
            rewards = list(
                self._rewards.find(
                    {"points": {"$gte": reward_points}}
                )
                .sort("points", pymongo.ASCENDING)
                .limit(2)
            )

            # If the user has reached the top tier, there will be no next reward to earn or progress to calculate.
            current_reward, next_reward = (rewards[0], rewards[1]) if len(rewards) > 1 else (rewards[0], None)

        next_tier_progress = round(1 - ((next_reward["points"] - total_points) / 100), 2) if next_reward else 0

        return {
            "email": email,
            "rewardPoints": min(total_points, MAXIMUM_REWARDS),
            "rewardTier": current_reward["tier"] if current_reward else None,
            "rewardTierName": current_reward["rewardName"] if current_reward else None,
            "nextRewardTier": next_reward["tier"] if next_reward else None,
            "nextRewardTierProgress": next_tier_progress,
        }

    def save(self, data):
        """
        Save customer info to DB. Upserts data, so if an email is in the DB, we'll update.
        Otherwise create a new customer

        Parameters:
            data (dict): The data to save

        Returns:
            rewards (dict): The data from _build_customer_rewards for the response object
        
        See Also:
            _build_customer_rewards() (line 34)
        """
        rewards = self._build_customer_rewards(data)

        self._collection.update_one(
                {"email": rewards["email"]},
                {"$set": rewards},
                upsert=True
            )

        return rewards

    def find(self, email):
        """
        Find a customer in the DB

        Parameters:
            email (string): The email we are looking for
        
        Returns:
            Any | None: The Customer document or Nothing
        """
        return self._collection.find_one({"email": email}, {"_id": 0})