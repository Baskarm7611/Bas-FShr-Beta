#(©)Tamilgram

import os
from motor.motor_asyncio import AsyncIOMotorClient
from config import DB_URL, bot_id

class DbConfig:
    def __init__(self, mongo_uri):
        self.client = AsyncIOMotorClient(mongo_uri)
        self.db = self.client[str(bot_id)]
        self.collection = self.db['tamilgram-configs']
    
    async def update_env_var(self, var_name: str, value: str):
        await self.collection.update_one(
            {"var_name": var_name},
            {"$set": {"value": value}},
            upsert=True
        )
        os.environ[var_name] = value
        print(f"Updated {var_name} to {value}")

    async def update_env_vars(self, vars_dict: dict):
        for var_name, value in vars_dict.items():
            await self.update_env_var(var_name, value)

    async def get_env_var(self, var_name: str):
        result = await self.collection.find_one({"var_name": var_name})
        if result:
            return result['value']
        else:
            return None

    async def get_all_env_vars(self):
        env_vars = {}
        async for env in self.collection.find():
            env_vars[env['var_name']] = env['value']
        return env_vars

Db_Config = DbConfig(DB_URL)
