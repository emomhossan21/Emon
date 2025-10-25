import requests
import telebot

# 🔹 Bot Configuration
# Use your actual bot token here
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
    processing_msg = None  # Initialize variable to hold the "processing" message
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

        # --- Send a "Processing" message to give user feedback ---
        processing_msg = bot.reply_to(message, "⏳ *Processing your request... Please wait.*")

        server = args[1]
        uid = args[2]
        api_key = "R1IsKing"

        url = f"https://r1-like.vercel.app/like?server_name={server}&uid={uid}&KEY={api_key}"
        
        # --- Make the API call with a timeout and check for HTTP errors ---
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # This will raise an exception for bad status codes (like 404, 500)

        data = response.json()

        # --- Safely extract data from the JSON response ---
        player = data.get("PlayerNickname", "Unknown")
        before = data.get("LikesbeforeCommand", 0)
        after = data.get("LikesafterCommand", 0)
        given = data.get("LikesGivenByAPI", 0)
        region = data.get("Region", "N/A")
        key_type = data.get("api_key_type", "Free")
        remain = data.get("daily_requests_remaining") # Get value, might be None or "N/A"
        used = data.get("daily_requests_used")       # Get value, might be None or "N/A"
        status = data.get("status", 0)

        sender_name = message.from_user.first_name or "User"

        # --- Build the final message based on the API response status ---
        if status == 2:
            # --- Safely handle usage stats to prevent crashing ---
            used_str = str(used) if used is not None else "N/A"
            remain_str = str(remain) if remain is not None else "N/A"
            total_requests_str = "N/A"
            
            # Only calculate the total if both 'used' and 'remain' are integers
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
            # Get a more specific error message from the API if available
            error_message = data.get("message", "Invalid UID or Server Name.")
            msg = f"❌ *Failed to send like!* \n`{error_message}`"

        # --- Edit the "Processing" message with the final result ---
        bot.edit_message_text(msg, chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)

    except requests.exceptions.RequestException as e:
        # --- Handle network/API errors (e.g., timeout, server down) ---
        error_text = f"❌ *API Error!* The server failed to respond. Please try again later.\n`{e}`"
        if processing_msg:
            bot.edit_message_text(error_text, chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)
        else:
            bot.reply_to(message, error_text)
            
    except Exception as e:
        # --- Handle any other unexpected errors in the code ---
        error_text = f"⚠️ *An unexpected error occurred:*\n`{e}`"
        if processing_msg:
            bot.edit_message_text(error_text, chat_id=processing_msg.chat.id, message_id=processing_msg.message_id)
        else:
            bot.reply_to(message, error_text)


print("🚀 LikeBot is running...")
bot.infinity_polling()