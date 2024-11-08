#(©)Tamilgram

import motor.motor_asyncio
import time
import string
import random
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN_VERIFY, TOKEN_VERIFY_TIME, DB_URL, bot_id, TUTORIAL_VIDEO, CONFIG_DICT
from helper_func import convert_short_link

def generate_token(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def format_duration(seconds):
    periods = [('Day', 86400), ('Hour', 3600), ('Minute', 60), ('Second', 1)]
    result = []
    for name, duration in periods:
        if seconds >= duration:
            count, seconds = divmod(seconds, duration)
            result.append(f"{count} {name}{'s' if count > 1 else ''}")
    return ', '.join(result)

class UserDatabase:
    def __init__(self, uri, db_name):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.collection = self.client[db_name]['tamilgram-token-verfiy-users']

    async def ensure_user(self, user_id):
        if not await self.collection.find_one({"user_id": user_id}):
            await self.collection.insert_one({"user_id": user_id, "verified_at": None, "token": None})

    async def get_user(self, user_id):
        return await self.collection.find_one({"user_id": user_id})

    async def update_user(self, user_id, updates):
        await self.collection.update_one({"user_id": user_id}, {"$set": updates})

db = UserDatabase(DB_URL, str(bot_id))

async def check_user_access(client, message):
    if not TOKEN_VERIFY:
        return True
    user_id = message.from_user.id
    command = message.command[1] if len(message.command) > 1 else None

    await db.ensure_user(user_id)
    user = await db.get_user(user_id)
    
    token = user.get('token')
    verified_at = user.get('verified_at')

    if command and "VERIFY" in command:
        command_type, token_value = command.split("-", 1)
        if token is None or token_value != token:
            new_token = generate_token()
            await db.update_user(user_id, {'token': new_token})
            verification_link = await convert_short_link(f"https://telegram.me/{client.username}?start=VERIFY-{new_token}", is_token=True)
            await message.reply_text(f"<b>Your Verify Link is Invalid or expired.\n\nVerify again👇</b>",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Verify Link", url=verification_link)], [InlineKeyboardButton("How To Verify", url=TUTORIAL_VIDEO)]]), protect_content=True)
            return False

        await db.update_user(user_id, {'verified_at': time.time(), 'token': generate_token()})
        await message.reply_text(f"Verified successfully! You can access Unlimited content for {format_duration(TOKEN_VERIFY_TIME)}.")
        return True
        
    if verified_at is None or (time.time() - verified_at > TOKEN_VERIFY_TIME):
        new_token = generate_token()
        await db.update_user(user_id, {'token': new_token})
        verification_link = await convert_short_link(f"https://telegram.me/{client.username}?start=VERIFY-{new_token}", is_token=True)
        await message.reply_text(f"<b>Your Verify Link is expired, refreshed your New Verify Link and try again.\n\nHow It's Working ?\n\nIf you Verify 1 Time, You Access Unlimited Files for Next {format_duration(TOKEN_VERIFY_TIME)}\n\nYour Verify Link is Here 👇</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Open Verify Link", url=verification_link)], [InlineKeyboardButton("How To Verify", url=TUTORIAL_VIDEO)]]), protect_content=True)
        return False

    return True
