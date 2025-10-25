import requests
import telebot

# 🔹 Bot Configuration
# আপনার আসল টোকেন এখানে ব্যবহার করুন
BOT_TOKEN = "8405694741:AAHeD2D8J032w-9TqMR36n7Zdv0K49lVYm4"
OWNER_ID = "123456789"
OWNER_NAME = "SHAZZ"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(
        msg,
        "🤖 *Welcome to LikeBot!*\n\n"
        "Use `/like <server> <uid>` to send likes!\n\n"
        "*Example:*\n`/like bd 8431020681`"
    )

@bot.message_handler(commands=['like'])
def like_cmd(message):
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(
                message,
                "⚠️ *Invalid Format!*\n"
                "*Usage:* `/like <server_name> <uid>`\n"
                "*Example:* `/like bd 8431020681`",
            )
            return

        # ব্যবহারকারীকে জানানো হচ্ছে যে অনুরোধটি প্রক্রিয়া করা হচ্ছে
        processing_msg = bot.reply_to(message, "⏳ *Processing your request... Please wait.*")

        server = args[1]
        uid = args[2]
        api_key = "R1IsKing"

        url = f"https://r1-like.vercel.app/like?server_name={server}&uid={uid}&KEY={api_key}"
        
        # নেটওয়ার্ক এবং অন্যান্য অনুরোধ-সম্পর্কিত ত্রুটি পরিচালনা
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # HTTP ত্রুটি থাকলে Exception তুলবে

        data = response.json()

        # --- নিরাপদে ডেটা বের করা ---
        player = data.get("PlayerNickname", "Unknown")
        before = data.get("LikesbeforeCommand", 0)
        after = data.get("LikesafterCommand", 0)
        given = data.get("LikesGivenByAPI", 0)
        region = data.get("Region", "N/A")
        key_type = data.get("api_key_type", "Free")
        remain = data.get("daily_requests_remaining") # ডিফল্ট মান নেই
        used = data.get("daily_requests_used") # ডিফল্ট মান নেই
        status = data.get("status", 0)

        sender_name = message.from_user.first_name or "User"

        # --- বার্তা তৈরি করা ---
        if status == 2:
            # ব্যবহৃত এবং অবশিষ্ট অনুরোধের সংখ্যা নিরাপদে পরিচালনা করা
            used_str = str(used) if used is not None else "N/A"
            remain_str = str(remain) if remain is not None else "N/A"
            total_requests_str = "N/A"
            
            if isinstance(used, int) and isinstance(remain, int):
                total_requests_str = str(used + remain)

            msg = (
                f"👤 *Requested by:* {sender_name}\n"
                f"✅ *LIKE SENT SUCCESSFULLY!*\n\n"
                f"🧑‍🎮 *Player:* `{player}`\n"
                f"🆔 *UID:* `{uid}`\n"
                f"🌍 *Region:* `{region}`\n\n"
                f"💖 *Likes Before:* `{before}`\n"
                f"💞 *Likes After:* `{after}`\n"
                f"⚡ *Likes Given:* `{given}`\n\n"
                f"🔑 *Key Type:* `{key_type}`\n"
                f"📊 *Used Today:* `{used_str}` / `{total_requests_str}`\n"
                f"♻️ *Remaining:* `{remain_str}`\n\n"
                f"👑 *Owner:* {OWNER_NAME} (`{OWNER_ID}`)"
            )
        else:
            error_message = data.get("message", "Invalid UID or Server Name.")
            msg = f"❌ *Failed to send like!* \n`{error_message}`"

        # "Processing" বার্তাটি চূড়ান্ত ফলাফল দিয়ে এডিট করা হয়
        bot.edit_message_text(msg, chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)

    except requests.exceptions.RequestException as e:
        # নেটওয়ার্ক বা API এরর হলে এই বার্তাটি দেখানো হবে
        bot.edit_message_text(
            f"❌ *API Error!* The server might be down. Please try again later.\n`{e}`",
            chat_id=processing_msg.chat.id,
            message_id=processing_msg.message_id
        )
    except Exception as e:
        # অন্য কোনো অপ্রত্যাশিত ত্রুটি ঘটলে এটি দেখানো হবে
        bot.edit_message_text(f"⚠️ *An unexpected error occurred:*\n`{e}`", chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)


print("🚀 LikeBot is running...")
bot.infinity_polling()