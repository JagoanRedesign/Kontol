import config
from pyrogram import Client, filters, types
from plugins.help.basic import edit_or_reply

# Menyimpan filter untuk setiap chat
filters_dict = {}

@Client.on_message(filters.command("filter", config.prefix) & filters.me)
async def add_filter(c: Client, m: types.Message):
    if len(m.command) < 3:
        await edit_or_reply(m, "**Penggunaan:** `.filter <trigger> <reply>`\n\n**Contoh:**\n`.filter hi Hello there!`")
        return

    trigger = m.command[1]
    reply = " ".join(m.command[2:])
    chat_id = m.chat.id

    if chat_id not in filters_dict:
        filters_dict[chat_id] = {}

    filters_dict[chat_id][trigger.lower()] = reply
    await edit_or_reply(m, f"Filter ditambahkan: `{trigger}` akan membalas dengan `{reply}`.")

@Client.on_message(filters.command("filters", config.prefix) & filters.me)
async def list_filters(c: Client, m: types.Message):
    chat_id = m.chat.id
    if chat_id not in filters_dict or not filters_dict[chat_id]:
        await edit_or_reply(m, "Tidak ada filter yang aktif di chat ini.")
    else:
        response = "**Daftar Filter:**\n\n"
        for trigger, reply in filters_dict[chat_id].items():
            response += f"`{trigger}` -> `{reply}`\n"
        await edit_or_reply(m, response)

@Client.on_message(filters.command("stop", config.prefix) & filters.me)
async def stop_filter(c: Client, m: types.Message):
    if len(m.command) < 2:
        await edit_or_reply(m, "**Penggunaan:** `.stop <trigger>`\n\n**Contoh:** `.stop hi`")
        return

    trigger = m.command[1].lower()
    chat_id = m.chat.id

    if chat_id in filters_dict and trigger in filters_dict[chat_id]:
        del filters_dict[chat_id][trigger]
        await edit_or_reply(m, f"Filter `{trigger}` telah dihentikan.")
    else:
        await edit_or_reply(m, "Filter tidak ditemukan.")

@Client.on_message(filters.command("stopall", config.prefix) & filters.me)
async def stop_all_filters(c: Client, m: types.Message):
    chat_id = m.chat.id
    if chat_id in filters_dict:
        del filters_dict[chat_id]
        await edit_or_reply(m, "Semua filter telah dihentikan untuk chat ini.")
    else:
        await edit_or_reply(m, "Tidak ada filter yang aktif di chat ini.")

@Client.on_message(filters.text & filters.group)
async def handle_filter(c: Client, m: types.Message):
    chat_id = m.chat.id
    if chat_id in filters_dict:
        for trigger, reply in filters_dict[chat_id].items():
            if trigger in m.text.lower():
                await c.send_message(chat_id, reply)
                break  # Hentikan setelah menemukan filter yang cocok
