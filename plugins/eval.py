import config
import sys
import traceback
from io import StringIO, BytesIO
from datetime import datetime
import platform
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message
from plugins.help.basic import edit_or_reply



def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor



async def aexec(code, client: Client, message: Message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {a}" for a in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)


@Client.on_message(filters.command("eval", config.prefix) & filters.me)
async def executor(client: Client, message: Message):
    if len(message.command) < 2:
        return await edit_or_reply(
            message, text="__Beri kode untuk di execute.__"
        )
    try:
        cmd = message.text.split(" ", maxsplit=1)[1]
    except IndexError:
        return await message.delete()
    time()
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    final_output = f"**OUTPUT**:\n```{evaluation.strip()}```"
    await edit_or_reply(message, final_output)
    
    

@Client.on_message(filters.command(["host", "cpu", "versi", "system"], config.prefix) & filters.me)
async def cek_host(client: Client, message: Message):
    xx = await edit_or_reply(message, "Processing...")
    
    uname = platform.uname()
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)

    # Format output
    softw = (
        f"➠ **Sistem**   : `{uname.system}`\n"
        f"➠ **Rilis**    : `{uname.release}`\n"
        f"➠ **Versi**    : `{uname.version}`\n"
        f"➠ **Mesin**    : `{uname.machine}`\n"
        f"➠ **Waktu Hidup**: `{bt.day}/{bt.month}/{bt.year} {bt.hour}:{bt.minute}:{bt.second}`\n\n"
        f"➠ **Informasi CPU**\n"
        f"➠ **Cores Fisik**   : `{psutil.cpu_count(logical=False)}`\n"
        f"➠ **Total Cores**    : `{psutil.cpu_count(logical=True)}`\n"
    )
    
    cpufreq = psutil.cpu_freq()
    softw += (
        f"➠ **Frekuensi Max**    : `{cpufreq.max:.2f} Mhz`\n"
        f"➠ **Frekuensi Min**    : `{cpufreq.min:.2f} Mhz`\n"
        f"➠ **Frekuensi Saat Ini**: `{cpufreq.current:.2f} Mhz`\n\n"
        f"➠ **Penggunaan CPU Per Core**\n"
    )
    
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
        softw += f"➠ **Core {i}**  : `{percentage}%`\n"
    
    softw += (
        f"➠ **Total Penggunaan CPU**\n"
        f"➠ **Semua Core**: `{psutil.cpu_percent()}%`\n\n"
        f"➠ **Bandwidth Digunakan**\n"
        f"➠ **Unggah**  : `{get_size(psutil.net_io_counters().bytes_sent)}`\n"
        f"➠ **Download**: `{get_size(psutil.net_io_counters().bytes_recv)}`\n\n"
    )

    svmem = psutil.virtual_memory()
    softw += (
        f"➠ **Memori Digunakan**\n"
        f"➠ **Total**     : `{get_size(svmem.total)}`\n"
        f"➠ **Tersedia**  : `{get_size(svmem.available)}`\n"
        f"➠ **Digunakan**  : `{get_size(svmem.used)}`\n"
        f"➠ **Persentase**: `{svmem.percent}%`\n"
    )

    await xx.edit(f"<b>{softw}</b>")
