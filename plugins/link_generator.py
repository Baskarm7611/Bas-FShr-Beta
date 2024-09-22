#(©)Tamilgram



from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from config import ADMINS, SHORTENER, DISABLE_CHANNEL_BUTTON, CONFIG_DICT
from helper_func import encode, get_message_id, convert_short_link


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('batch'))
async def batch(client: Client, message: Message):
    while True:
        try:
            first_message = await client.ask(text = "Forward the First Message from DB Channel (with Quotes)..\n\nor Send the DB Channel Post Link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        f_msg_id = await get_message_id(client, first_message)
        if f_msg_id:
            break
        else:
            await first_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue

    while True:
        try:
            second_message = await client.ask(text = "Forward the Last Message from DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        s_msg_id = await get_message_id(client, second_message)
        if s_msg_id:
            break
        else:
            await second_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is taken from DB Channel", quote = True)
            continue


    string = f"get-{f_msg_id * abs(client.db_channel.id)}-{s_msg_id * abs(client.db_channel.id)}"
    base64_string = await encode(string)
    link = f"{CONFIG_DICT['PERMANENT_DOMAIN']}{base64_string}" if str(CONFIG_DICT['PERMANENT_DOMAIN']).lower() != "false" else f"https://telegram.me/{client.username}?start={base64_string}"
    if SHORTENER:
        text=f"<b>Here is your link</b>\n\n<code>{link}</code>\n\n<code>{await convert_short_link(link)}</code>"
    else:
        text=f"<b>Here is your link</b>\n\n<code>{link}</code>"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Start URL", url=f'{link}')]])
    await second_message.reply_text(text, quote=True, reply_markup=reply_markup)


@Bot.on_message(filters.private & filters.user(ADMINS) & filters.command('genlink'))
async def link_generator(client: Client, message: Message):
    while True:
        try:
            channel_message = await client.ask(text = "Forward Message from the DB Channel (with Quotes)..\nor Send the DB Channel Post link", chat_id = message.from_user.id, filters=(filters.forwarded | (filters.text & ~filters.forwarded)), timeout=60)
        except:
            return
        msg_id = await get_message_id(client, channel_message)
        if msg_id:
            break
        else:
            await channel_message.reply("❌ Error\n\nthis Forwarded Post is not from my DB Channel or this Link is not taken from DB Channel", quote = True)
            continue

    base64_string = await encode(f"get-{msg_id * abs(client.db_channel.id)}")
    link = f"{CONFIG_DICT['PERMANENT_DOMAIN']}{base64_string}" if str(CONFIG_DICT['PERMANENT_DOMAIN']).lower() != "false" else f"https://telegram.me/{client.username}?start={base64_string}"
    if SHORTENER:
        text=f"<b>Here is your link</b>\n\n<code>{link}</code>\n\n<code>{await convert_short_link(link)}</code>"
    else:
        text=f"<b>Here is your link</b>\n\n<code>{link}</code>"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Start URL", url=f'{link}')]])
    await channel_message.reply_text(text, quote=True, reply_markup=reply_markup)

@Bot.on_message(filters.private & filters.user(ADMINS) & ~filters.command(['start','users','broadcast','batch','genlink','stats','setfsub','setapi','setdb','newadmins','setcaption','startmsg','forcemsg','startmsg','protection','setreq','restart', 'settings']))
async def channel_post(client: Client, message: Message):
    reply_text = await message.reply_text("Please Wait...!", quote = True)
    try:
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.x)
        post_message = await message.copy(chat_id = client.db_channel.id, disable_notification=True)
    except Exception as e:
        print(e)
        await reply_text.edit_text("Something went Wrong..!")
        return
    converted_id = post_message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    link = f"{CONFIG_DICT['PERMANENT_DOMAIN']}{base64_string}" if str(CONFIG_DICT['PERMANENT_DOMAIN']).lower() != "false" else f"https://telegram.me/{client.username}?start={base64_string}"
    if SHORTENER:
        text=f"<b>Here is your link</b>\n\n<code>{link}</code>\n\n<code>{await convert_short_link(link)}</code>"
    else:
        text=f"<b>Here is your link</b>\n\n<code>{link}</code>"
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Start URL", url=f'{link}')]])

    await reply_text.edit(text, reply_markup=reply_markup, disable_web_page_preview = True)

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)
