#(©)Tamilgram


import motor.motor_asyncio
from config import DB_URL, bot_id

class JoinReqs:
    def __init__(self, DB_URL):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(DB_URL)
        self.db = self.client[str(bot_id)]
        self.col = self.db['TAMILGRAM-SUB']

    async def add_user(self, user_id, first_name, username, date, channels=[]):
        try:
            await self.col.insert_one({"user_id": int(user_id), "first_name": first_name, "username": username, "date": date, 'channels': channels})
        except:
            pass

    async def update_user(self, user_id, channels):
        try:
            await self.col.update_one({"user_id": int(user_id), 'channels': channels}, upsert=True)
        except:
            pass

    async def get_user(self, user_id):
        return await self.col.find_one({"user_id": int(user_id)})

    async def get_all_users(self):
        return await self.col.find().to_list(None)

    async def delete_user(self, user_id):
        await self.col.delete_one({"user_id": int(user_id)})

    async def delete_all_users(self):
        await self.col.delete_many({})

    async def get_all_users_count(self):
        return await self.col.count_documents({})

Join_Reqs = JoinReqs(DB_URL)
