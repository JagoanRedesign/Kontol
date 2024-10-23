import config
import sys
import traceback
from io import StringIO, BytesIO
from datetime import datetime
import platform
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message



def get_size(bytes, suffix="B"):
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor

async def aexec(cmd, client, message):
    # Menggunakan exec dalam konteks lokal
    exec_locals = {}
    try:
        # Definisikan fungsi asinkron dalam konteks lokal
        exec(f"async def func():\n    {cmd}", exec_locals)
        # Jalankan fungsi tersebut
        await exec_locals['func']()
    except Exception as e:
        raise e  # Lemparkan kesalahan yang terjadi

@Client.on_message(filters.command("eval", config.prefix) & filters.me)
async def eval_command(client: Client, message):
    cmd = message.text.split(" ", maxsplit=1)[1] if len(message.text.split(" ")) > 1 else None
    if not cmd:
        return await message.reply("`Give me commands dude...`")
    
    ajg = await message.reply("`Processing ...`")
    reply_to_ = message.reply_to_message or message
    
    # Alihkan output
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    old_stderr = sys.stderr
    redirected_error = sys.stderr = StringIO()
    
    exc = None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()  # Tangkap kesalahan
    
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    
    # Kembalikan output ke stdout dan stderr asli
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    
    # Tentukan evaluasi akhir
    evaluation = exc if exc else stderr if stderr else stdout.strip() if stdout.strip() else "Success"
    
    final_output = "OUTPUT:\n" + evaluation.strip()
    
    if len(final_output) > 4096:
        with BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.txt"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[: 4096 // 4 - 1],
                disable_notification=True,
                quote=True,
            )
    else:
        await reply_to_.reply_text(final_output, quote=True)
    
    await ajg.delete()


@Client.on_message(filters.command("host", config.prefix) & filters.me)
async def cek_host(client: Client, message: Message):
    xx = await message.reply("Processing...")
    uname = platform.uname()
    softw = "Informasi Sistem\n"
    softw += f"Sistem   : {uname.system}\n"
    softw += f"Rilis    : {uname.release}\n"
    softw += f"Versi    : {uname.version}\n"
    softw += f"Mesin    : {uname.machine}\n"

    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    softw += f"Waktu Hidup: {bt.day}/{bt.month}/{bt.year}  {bt.hour}:{bt.minute}:{bt.second}\n"

    softw += "\nInformasi CPU\n"
    softw += "Physical cores   : " + str(psutil.cpu_count(logical=False)) + "\n"
    softw += "Total cores      : " + str(psutil.cpu_count(logical=True)) + "\n"
    cpufreq = psutil.cpu_freq()
    softw += f"Max Frequency    : {cpufreq.max:.2f}Mhz\n"
    softw += f"Min Frequency    : {cpufreq.min:.2f}Mhz\n"
    softw += f"Current Frequency: {cpufreq.current:.2f}Mhz\n\n"
    softw += "CPU Usage Per Core\n"
    for i, percentage in enumerate(psutil.cpu_percent(percpu=True)):
        softw += f"Core {i}  : {percentage}%\n"
    softw += "Total CPU Usage\n"
    softw += f"Semua Core: {psutil.cpu_percent()}%\n"

    softw += "\nBandwith Digunakan\n"
    softw += f"Unggah  : {get_size(psutil.net_io_counters().bytes_sent)}\n"
    softw += f"Download: {get_size(psutil.net_io_counters().bytes_recv)}\n"

    svmem = psutil.virtual_memory()
    softw += "\nMemori Digunakan\n"
    softw += f"Total     : {get_size(svmem.total)}\n"
    softw += f"Available : {get_size(svmem.available)}\n"
    softw += f"Used      : {get_size(svmem.used)}\n"
    softw += f"Percentage: {svmem.percent}%\n"

    await xx.edit(f"<b>{softw}</b>")
