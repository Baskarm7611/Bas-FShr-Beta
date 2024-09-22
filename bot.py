#(©)Tamilgram

from aiohttp import web
from plugins import web_server
from os import path as ospath,remove as osremove
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime
from database.manage_config import Db_Config
from config import *

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={
                "root": "plugins"
            },
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        BOT_USERNAME = usr_bot_me.username
        print(BOT_USERNAME)
        CONFIG_DICT['BOT_USERNAME'] = BOT_USERNAME
        self.uptime = datetime.now()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/CodeXBotzSupport for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/CodeXBotz")
        CONFIGDICT = {
            'SUB_CHANNELS': SUB_CHANNELS,
            'AUTO_DELETE': AUTO_DELETE,
            'AUTO_DELETE_TIME': AUTO_DELETE_TIME,
            'PERMANENT_DOMAIN': PERMANENT_DOMAIN,
            'ADMINS': ADMINS,
            'CUSTOM_CAPTION': CUSTOM_CAPTION,
            "START_MSG": START_MSG,
            'FORCE_MSG': FORCE_MSG,
            'PROTECT_CONTENT': PROTECT_CONTENT,
            'SHORTENER': SHORTENER,
            'TOKEN_VERIFY': TOKEN_VERIFY,
            'TOKEN_VERIFY_TIME': TOKEN_VERIFY_TIME,
            'TUTORIAL_VIDEO': TUTORIAL_VIDEO,
            'CHANNEL_ID': CHANNEL_ID,
            'BOT_USERNAME': BOT_USERNAME
        }
        await Db_Config.update_env_vars(CONFIGDICT)
        self.LOGGER(__name__).info("Config Loaded To DB")
        self.username = usr_bot_me.username
        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        if ospath.isfile(".restartmsg"):
                    with open(".restartmsg") as f:
                        chat_id, msg_id = map(int, f)
                    msg = f"Bot Restarted Successfully❗\n"
                    await self.edit_message_text(chat_id, msg_id, msg)
                    osremove(".restartmsg")
    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
