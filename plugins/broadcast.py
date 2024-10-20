import asyncio
import typing
import contextlib

import config
from pyrogram import (
  Client,
  filters,
  types,
  enums,
  errors,
)


def get_msg(m: types.Message) -> types.Message:
    msg: typing.Union[str, types.Message] = None
    if rep := m.reply_to_message:
        msg = rep

    elif len(m.command) > 1:
        msg = (m.text or m.caption).split(None, 1)[1]
    else:
        return None

    return msg


@Client.on_message(filters.command(["broadcast", "gcast"], config.prefix) & filters.me)
async def broadcast_group(c: Client, m: types.Message):
    msg = get_msg(m)
    if not msg:
        with contextlib.suppress(errors.SlowmodeWait):
            return await m.reply("Give me a message or reply to a message!")
    load = None
    with contextlib.suppress(errors.SlowmodeWait):
        load = await m.reply("Broadcast Group processing....")
    done = error = 0
    chat_ids = []

    async for dialog in c.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            chat_ids.append(dialog.chat.id)

    async def send_broadcast(chat_id):
        nonlocal done, error
        try:
            await msg.copy(chat_id) if m.reply_to_message else await c.send_message(chat_id, msg)
            done += 1
            if done % 4 == 0:
                await asyncio.sleep(1.5)
        except errors.FloodWait as f:
            await asyncio.sleep(f.value + 1)
            await msg.copy(chat_id) if m.reply_to_message else await c.send_message(chat_id, msg)
        except Exception: # type: ignore
            error += 1

    for chat_id in chat_ids: # loop
        if chat_id in config.group_blacklist:
            continue
        await send_broadcast(chat_id)
    if done:
        return await load.edit(f"<i>Broadcast was sent to {done} groups, failed to send to {error} groups(s)</i>")


@Client.on_message(filters.command("ucast", config.prefix) & filters.me)
async def broadcast_users(c: Client, m: types.Message):
    msg = get_msg(m)
    if not msg:
        with contextlib.suppress(errors.SlowmodeWait):
            return await m.reply("Give me a message or reply to a message!")
    load = None
    with contextlib.suppress(errors.SlowmodeWait):
        load = await m.reply("Broadcast users processing.....")
    done = error = 0
    chat_ids = []

    async for dialog in c.get_dialogs():
        if dialog.chat.type in enums.ChatType.PRIVATE:
            chat_ids.append(dialog.chat.id)

    async def send_broadcast(chat_id):
        nonlocal done, error
        try:
            await msg.copy(chat_id) if m.reply_to_message else await c.send_message(chat_id, msg)
            done += 1
            if done % 4 == 0:
                await asyncio.sleep(1.5)
        except errors.FloodWait as f:
            await asyncio.sleep(f.value + 1)
            await msg.copy(chat_id) if m.reply_to_message else await c.send_message(chat_id, msg)
        except Exception: # type: ignore
            error += 1

    for chat_id in chat_ids: # loop
        await send_broadcast(chat_id)
    if done:
        return await load.edit(f"<i>Broadcast was send to {done} users, failed to send to {error} users(s)</i>")


@Client.on_message(filters.command("fwdcast", config.prefix) & filters.me)
async def broadcast_forward(c: Client, m: types.Message):
    if not (reply := m.reply_to_message):
        with contextlib.suppress(errors.SlowmodeWait):
            return await m.reply("Reply to messages you want to continue posting")
    load = None
    with contextlib.suppress(errors.SlowmodeWait):
        load = await m.reply("Broadcast forward processing....")
    done = error = 0
    chat_ids = []

    async for dialog in c.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            chat_ids.append(dialog.chat.id)

    async def send_broadcast(chat_id):
        nonlocal done, error
        try:
            await reply.forward(chat_id)
            done += 1
            if done % 4 == 0:
                await asyncio.sleep(0.5)
        except errors.FloodWait as f:
            await asyncio.sleep(f.value + 1)
            await reply.forward(chat_id)
        except Exception: # type: ignore
            error += 1

    for chat_id in chat_ids: # loop
        if chat_id in config.group_blacklist:
            continue
        await send_broadcast(chat_id)
    if load:
        return await load.edit(f"<i>Broadcast was send to {done} forward, failed to send to {error} forward(s)")
