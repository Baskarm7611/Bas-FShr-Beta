#(©)Tamilgram

import base64
import re
import asyncio
from cache import AsyncLRU
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CONFIG_DICT
from database.join_reqs import Join_Reqs
from shortzy import Shortzy

global_invite_links = {}


async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.x)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

async def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
        else:
            return 0
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern,message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    else:
        return 0


def get_readable_time(seconds: int) -> str:
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += f"{time_list.pop()}, "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time


#@AsyncLRU(maxsize=200)
async def check_rsub_status(client, message, user_id, channel_id):
    user = await Join_Reqs.get_user(user_id)
    if not user:
        await Join_Reqs.add_user(user_id, message.from_user.first_name, message.from_user.username, message.date)
        user = await Join_Reqs.get_user(user_id)
    if chats := user['channels']:
        return channel_id in chats
    return False

async def check_fsub_status(client, user_id, channel_id):
    try:
        user = await client.get_chat_member(channel_id, user_id)
        return user.status != ChatMemberStatus.BANNED
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Error checking follow subscription status: {e}")
        return False

async def update_invite_links(client, channel_id, mode):
    invite = await client.create_chat_invite_link(channel_id, creates_join_request=mode)
    global_invite_links[channel_id] = invite.invite_link
    return invite.invite_link

async def check_user_sub_status(client, message):
    CHANNELS = CONFIG_DICT['FSUB_CHANNELS']
    if not CHANNELS:
        return True
    user_id = message.from_user.id
    invite_links = []

    for channel_id, mode in CHANNELS.items():
        if mode:
            if await check_fsub_status(client, user_id, channel_id):
                continue
            if not await check_rsub_status(client, message, user_id, channel_id):
                try:
                    link = global_invite_links[channel_id]
                except KeyError:
                    link = await update_invite_links(client, channel_id, mode)
                invite_links.append((link, mode))
        else:
            if not await check_fsub_status(client, user_id, channel_id):
                try:
                    link = global_invite_links[channel_id]
                except KeyError:
                    link = await update_invite_links(client, channel_id, mode)
                invite_links.append((link, mode))

    if not invite_links:
        return True

    buttons = [
        [InlineKeyboardButton(f"{'Request' if mode else 'Join'} Channel {index + 1}", url=invite_link)]
        for index, (invite_link, mode) in enumerate(invite_links)
    ]
    if len(message.command) > 1:
        buttons.append(
            [InlineKeyboardButton("Try Again", url=f"https://telegram.me/{client.username}?start={message.command[1]}")]
        )

    await message.reply_text(
        text=CONFIG_DICT['FORCE_MSG'].format(mention=message.from_user.mention),
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    return False


async def convert_short_link(url, is_token=False):
    if is_token:
        auth = Shortzy(CONFIG_DICT['TOKEN_SHORTENER']['api'], CONFIG_DICT['TOKEN_SHORTENER']['site'])
    else:
        auth = Shortzy(CONFIG_DICT['SHORTENER']['api'], CONFIG_DICT['SHORTENER']['site'])
    return await auth.convert(url, silently_fail=True)


async def deleteMessage(message, time=None, use_default=True):
    if time and not use_default:
        await asyncio.sleep(time)
    elif use_default:
        await asyncio.sleep(CONFIG_DICT['AUTO_DELETE_TIME'])
    try:
        await message.delete()
    except Exception as e:
        print(e)
