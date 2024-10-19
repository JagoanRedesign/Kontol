import config

from pyrogram import Client, idle as idling


client = Client(
     "PyroUbot",
     api_id=config.api_id,
     api_hash=config.api_hash,
     session_string=config.session_string,
     device_model="PyroUbot",
     plugins=dict(root="plugins"),
     in_memory=False,
)

idle = idling
