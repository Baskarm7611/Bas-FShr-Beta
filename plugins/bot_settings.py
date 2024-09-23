#(©)Tamilgram


import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.errors import FloodWait
from bot import Bot
from config import ADMINS, CONFIG_DICT
from database.manage_config import Db_Config


@Bot.on_message(filters.command('settings') & filters.private & filters.user(ADMINS))
async def bot_settings(client, message):
    buttons = []
    for var_name in CONFIG_DICT:
        buttons.append(
            [
                InlineKeyboardButton(var_name, f"var {var_name}")
            ]
        )
    await client.send_message(chat_id=message.chat.id, text="Select A Variable To edit", reply_markup=InlineKeyboardMarkup(buttons))


@Bot.on_callback_query(filters.regex('^showvars'))
async def show_vars(client, query):
    buttons = []
    for var_name in CONFIG_DICT:
        buttons.append(
            [
                InlineKeyboardButton(var_name, f"var {var_name}")
            ]
        )
    await query.message.edit(text="Select A Variable To edit", reply_markup=InlineKeyboardMarkup(buttons))


@Bot.on_callback_query(filters.regex('^var'))
async def edit_vars(client, query):
    data = query.data.split()
    var_name = data[1]
    value = await Db_Config.get_env_var(var_name)
    text = f"Var : <b>{var_name}</b>\n\nCurrent Value : <code>{value}</code>"
    await query.message.edit(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Edit', f"edit {var_name}")],
                [InlineKeyboardButton('Back', f"showvars")]
            ]
        )
    )


@Bot.on_callback_query(filters.regex('^edit'))
async def edit_var_value(client, query):
    data = query.data.split()
    var_name = data[1]
    await query.message.edit(text=f"Send value for {var_name} or /empty for Disable")
    value_msg = await client.listen(query.from_user.id)
    await value_msg.delete()

    if var_name == 'SUB_CHANNELS':
        if value_msg.text.lower() in ['no', '/empty']:
            new_value = None
            await Db_Config.update_env_var(var_name, new_value)
        else:
            lines = value_msg.text.split('\n')
            channel_ids = {}
            for line in lines:
                channel_id, mode = line.split(maxsplit=1)
                channel_ids[int(channel_id)] = mode.lower() == 'rsub'
            new_value = channel_ids
            await Db_Config.update_env_var(var_name, value_msg.text)
        CONFIG_DICT[var_name] = new_value

        if new_value:
            value_text = ""
            for channel_id, mode in new_value.items():
                mode_text = 'RSUB' if mode else 'FSUB'
                value_text += f"Channel ID: <code>{channel_id}</code>, Mode: <b>{mode_text}</b>\n"
        else:
            value_text = "No Sub Channels Configured."

        text = f"Var : <b>{var_name}</b>\n\nCurrent Value:\n{value_text}"
        
    elif value_msg.text.lower() in ['no', '/empty']:
        new_value = None
        await Db_Config.update_env_var(var_name, new_value)
        CONFIG_DICT[var_name] = new_value
    elif var_name in ['AUTO_DELETE', 'PROTECT_CONTENT', 'TOKEN_VERIFY']:
        new_value = value_msg.text.lower() == 'true'
        await Db_Config.update_env_var(var_name, value_msg.text)
        CONFIG_DICT[var_name] = new_value

    elif var_name in ['AUTO_DELETE_TIME', 'TOKEN_VERIFY_TIME']:
        new_value = int(value_msg.text)
        await Db_Config.update_env_var(var_name, new_value)
        CONFIG_DICT[var_name] = new_value
    
    elif var_name == 'ADMINS':
        admin_list = value_msg.text.split()
        new_value = [int(admin) for admin in admin_list]
        await Db_Config.update_env_var(var_name, value_msg.text)
        CONFIG_DICT[var_name] = new_value

    elif var_name in ['PERMANENT_DOMAIN', 'CUSTOM_CAPTION', 'START_MSG', 'FORCE_MSG', 'TUTORIAL_VIDEO']:
        new_value = value_msg.text
        await Db_Config.update_env_var(var_name, new_value)
        CONFIG_DICT[var_name] = new_value

    elif var_name == 'SHORTENER':
        text = value_msg.text
        site, api = text.split()
        new_value = {
            'site': site,
            'api': api
        }
        await Db_Config.update_env_var(var_name, text)
        CONFIG_DICT[var_name] = new_value
        text = f"Var : <b>{var_name}</b>\n\nCurrent Value:\n{new_value['site']} {new_value['api']}"

    value = await Db_Config.get_env_var(var_name)
    
    if var_name not in ['SUB_CHANNELS', 'SHORTENER']:
        text = f"Var : <b>{var_name}</b>\n\nCurrent Value : <code>{value}</code>"
    
    return await query.message.edit(
        text=text,
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton('Edit', f"edit {var_name}")],
                [InlineKeyboardButton('Back', f"showvars")]
            ]
        )
    )
