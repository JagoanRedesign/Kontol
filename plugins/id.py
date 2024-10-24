import config
import asyncio
from plugins.help.basic import edit_or_reply
from pyrogram import Client, filters, types
from pyrogram import enums

@Client.on_message(filters.command("id", config.prefix) & filters.me)
async def get_id(c: Client, m: types.Message):
    chat = m.chat
    your_id = m.from_user.id
    message_id = m.id
    reply = m.reply_to_message

    text = f"**[Message ID:]({m.link})** `{message_id}`\n"
    text += f"**[Your ID:](tg://user?id={your_id})** `{your_id}`\n"

    if len(m.command) == 2:
        try:
            split = m.text.split(None, 1)[1].strip()
            user_id = (await c.get_users(split)).id
            text += f"**[User ID:](tg://user?id={user_id})** `{user_id}`\n"
        except Exception:
            return await edit_or_reply(m, "Pengguna tidak ditemukan.")

    text += f"**[Chat ID:](https://t.me/{chat.username})** `{chat.id}`\n\n"
    
    if reply:
        id_ = reply.from_user.id if reply.from_user else reply.sender_chat.id
        text += f"**[Replied Message ID:]({reply.link})** `{reply.id}`\n"
        text += f"**[Replied User ID:](tg://user?id={id_})** `{id_}`"

    await edit_or_reply(m,
        text,
        disable_web_page_preview=True,        
    )

@Client.on_message(filters.command("gid", config.prefix) & filters.me)
async def get_id_by_username(c: Client, m: types.Message):
    if len(m.command) < 2:
        return await edit_or_reply(m,"Penggunaan: `gid <username>`\nContoh: `gid @username`")

    username = m.command[1].strip('@')
    
    try:
        user = await c.get_users(username)
        user_id = user.id
        await m.reply(f"**[User ID:](tg://user?id={user_id})** `{user_id}`")
    except Exception:
        await m.reply("Pengguna tidak ditemukan.")
