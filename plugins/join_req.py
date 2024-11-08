#(©)Tamilgram

from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest, ChatMemberUpdated
from database.join_reqs import Join_Reqs
from config import ADMINS, CONFIG_DICT

@Client.on_chat_member_updated()
async def left_mambers(client, update):
    user_id = update.from_user.id
    chat_id = update.chat.id
    if update.old_chat_member and update.old_chat_member.status == enums.ChatMemberStatus.MEMBER:
        if chat_id in CONFIG_DICT['FSUB_CHANNELS'].keys():
            user = await Join_Reqs.get_user(user_id)
            if user:
                current_channels = user.get('channels', [])
                if chat_id in current_channels:
                    current_channels.remove(chat_id)
                    await Join_Reqs.update_user(user_id, current_channels)
            



@Client.on_chat_join_request()
async def join_reqs(client, join_req: ChatJoinRequest):
    chat_id = join_req.chat.id
    user_id = join_req.from_user.id
    first_name = join_req.from_user.first_name
    username = join_req.from_user.username or "N/A"
    date = join_req.date
    if chat_id in CONFIG_DICT['FSUB_CHANNELS'].keys():
        user = await Join_Reqs.get_user(user_id)
        
        if user:
            current_channels = user.get('channels', [])
            if chat_id not in current_channels:
                current_channels.append(chat_id)
                await Join_Reqs.update_user(user_id, current_channels)
        else:
            await Join_Reqs.add_user(
                user_id=user_id,
                first_name=first_name,
                username=username,
                date=date,
                channels=[chat_id]
            )

@Client.on_message(filters.command("totalrequests") & filters.private & filters.user(ADMINS))
async def total_requests(client, message):
    total = await Join_Reqs.get_all_users_count()
    await message.reply_text(
        text=f"Total Requests: {total}",
        parse_mode=enums.ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )

@Client.on_message(filters.command("purgerequests") & filters.private & filters.user(ADMINS))
async def purge_requests(client, message):
    await Join_Reqs.delete_all_users()
    await message.reply_text(
        text="Purged All Requests.",
        parse_mode=enums.ParseMode.MARKDOWN,
        disable_web_page_preview=True
    )
