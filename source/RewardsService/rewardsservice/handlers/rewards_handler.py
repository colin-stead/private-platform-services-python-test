import json

import database

from .base_handler import BaseHandler

DB = database.get_db()

class RewardsHandler(BaseHandler):

    async def get(self):
        rewards = list(DB.rewards.find({}, {"_id": 0}))
        self.write(json.dumps(rewards, indent=4))
