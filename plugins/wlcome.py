import config
from pyrogram import Client, filters, types
from plugins.help.basic import edit_or_reply

# Struktur data untuk menyimpan pengaturan sambutan per grup
group_settings = {}

@Client.on_message(filters.command("wlc", config.prefix) & filters.me & filters.group)
async def toggle_welcome(c: Client, m: types.Message):
    chat_id = m.chat.id

    if chat_id not in group_settings:
        group_settings[chat_id] = {
            "welcome_enabled": False,
            "welcome_message": "Selamat datang, {name}! Semoga betah di grup ini!"
        }

    if len(m.command) < 2:
        await edit_or_reply(m, "**Penggunaan:**\n`.wlc on` untuk menghidupkan sambutan\n`.wlc off` untuk mematikan sambutan\n`.wlc list` untuk melihat semua welcome yang aktif")
        return

    command = m.command[1].lower()
    if command == "on":
        group_settings[chat_id]["welcome_enabled"] = True
        await edit_or_reply(m, "Fitur sambutan telah dihidupkan.")
    elif command == "off":
        group_settings[chat_id]["welcome_enabled"] = False
        await edit_or_reply(m, "Fitur sambutan telah dimatikan.")
    elif command == "list":
        active_welcomes = [f"- {group_settings[gid]['welcome_message']} (Grup: {gid})" for gid in group_settings if group_settings[gid]['welcome_enabled']]
        if active_welcomes:
            welcome_list = "\n".join(active_welcomes)
            await edit_or_reply(m, f"**Welcome yang saat ini aktif:**\n{welcome_list}")
        else:
            await edit_or_reply(m, "Tidak ada welcome yang saat ini aktif.")
    else:
        await edit_or_reply(m, "Perintah tidak dikenali. Gunakan `.wlc on`, `.wlc off`, atau `.wlc list`.")

@Client.on_message(filters.command("set_welcome", config.prefix) & filters.me & filters.group)
async def set_welcome(c: Client, m: types.Message):
    chat_id = m.chat.id

    if chat_id not in group_settings:
        group_settings[chat_id] = {
            "welcome_enabled": False,
            "welcome_message": "Selamat datang, **{name}**! Semoga betah di grup ini!"
        }

    # Mengambil kalimat sambutan dari perintah
    new_welcome_message = " ".join(m.command[1:])
    
    if not new_welcome_message:
        await edit_or_reply(m, "**Penggunaan:** `.set_welcome <kalimat_sambutan>`")
        return
    
    group_settings[chat_id]["welcome_message"] = new_welcome_message
    await edit_or_reply(m, f"Kalimat sambutan telah diubah menjadi: `{new_welcome_message}`")

@Client.on_chat_member_updated(filters.group)
async def welcome_new_member(c: Client, m: types.ChatMemberUpdated):
    chat_id = m.chat.id

    if chat_id in group_settings and group_settings[chat_id]["welcome_enabled"] and m.new_chat_member.status == "member":
        user_name = m.new_chat_member.user.first_name if m.new_chat_member.user.first_name else "Sahabat"
        personalized_welcome = group_settings[chat_id]["welcome_message"].format(name=user_name)
        
        await c.send_message(chat_id, personalized_welcome)
