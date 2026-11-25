#!/usr/bin/env python
import database

REWARDS = [
    {"points": 100, "rewardName": "5% off purchase", "tier": "A"},
    {"points": 200, "rewardName": "10% off purchase", "tier": "B"},
    {"points": 300, "rewardName": "15% off purchase", "tier": "C"},
    {"points": 400, "rewardName": "20% off purchase", "tier": "D"},
    {"points": 500, "rewardName": "25% off purchase", "tier": "E"},
    {"points": 600, "rewardName": "30% off purchase", "tier": "F"},
    {"points": 700, "rewardName": "35% off purchase", "tier": "G"},
    {"points": 800, "rewardName": "40% off purchase", "tier": "H"},
    {"points": 900, "rewardName": "45% off purchase", "tier": "I"},
    {"points": 1000, "rewardName": "50% off purchase", "tier": "J"},
]


def load(db):
    """
    Drop and reload the rewards collection

    Parameters:
        db (Database): The database to load into (set by DB_NAME, see database.py)
    """
    db.rewards.drop()
    db.rewards.insert_many([dict(reward) for reward in REWARDS])


def main():
    db = database.get_db()

    print(f"Removing and reloading rewards in mongo ({db.name})")
    load(db)
    print("Rewards loaded in mongo")


if __name__ == "__main__":
    main()
