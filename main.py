import os
import random
import string
import time
import names
import requests
import telebot
import threading
from flask import Flask

# --- FLASK KEEP-ALIVE SERVER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7"

def run_flask():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()

# --- INITIALIZATION ---
# Get token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN', '8386332866:AAGBMhQ5-YpbXkb-E0GRCTdAsaiwQWGEk2Y')
bot = telebot.TeleBot(BOT_TOKEN)

# ANSI Colors for Console
rd, gn, lgn, yw, lrd, be, pe = '\033[00;31m', '\033[00;32m', '\033[01;32m', '\033[01;33m', '\033[01;31m', '\033[94m', '\033[01;35m'
cn, k, g = '\033[00;36m', '\033[90m', '\033[38;5;130m'
true = f'{rd}[{lgn}+{rd}]{gn} '
false = f'{rd}[{lrd}-{rd}] '
SUCCESS = f'{rd}[{lgn}+{rd}]{gn} '
ERROR = f'{rd}[{lrd}-{rd}]{rd} '

# Dictionary to store user states (to handle concurrent users)
user_data = {}

# --- CORE LOGIC (UNCHANGED PAYLOADS/HEADERS) ---

proxies = None

def get_headers(Country, Language):
    while True:
        try:
            an_agent = (
                f'Mozilla/5.0 (Linux; Android {random.randint(9, 13)}; '
                f'{"".join(random.choices(string.ascii_uppercase, k=3))}{random.randint(111, 999)}) '
                f'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36'
            )
            r = requests.get(
                'https://www.instagram.com/api/v1/web/accounts/login/ajax/',
                headers={'user-agent': an_agent},
                proxies=proxies,
                timeout=30
            ).cookies

            response1 = requests.get(
                'https://www.instagram.com/',
                headers={'user-agent': an_agent},
                proxies=proxies,
                timeout=30
            )
            appid = response1.text.split('APP_ID":"')[1].split('"')[0]
            rollout = response1.text.split('rollout_hash":"')[1].split('"')[0]

            headers = {
                'authority': 'www.instagram.com',
                'accept': '*/*',
                'accept-language': f'{Language}-{Country},en-US;q=0.8,en;q=0.7',
                'content-type': 'application/x-www-form-urlencoded',
                'cookie': f'dpr=3; csrftoken={r["csrftoken"]}; mid={r["mid"]}; ig_did={r["ig_did"]}',
                'origin': 'https://www.instagram.com',
                'referer': 'https://www.instagram.com/accounts/signup/email/',
                'user-agent': an_agent,
                'x-csrftoken': r["csrftoken"],
                'x-ig-app-id': str(appid),
                'x-instagram-ajax': str(rollout),
                'x-web-device-id': r["ig_did"],
            }
            return headers
        except Exception as E:
            print(f"Header Error: {E}")

def Get_UserName(Headers, Name, Email):
    try:
        while True:
            data = {'email': Email, 'name': Name + str(random.randint(1, 99))}
            response = requests.post(
                'https://www.instagram.com/api/v1/web/accounts/username_suggestions/',
                headers=Headers, data=data, proxies=proxies, timeout=30
            )
            if 'status":"ok' in response.text:
                return random.choice(response.json()['suggestions'])
    except Exception as E:
        print(E)

def Send_SMS(Headers, Email):
    try:
        data = {
            'device_id': Headers['cookie'].split('mid=')[1].split(';')[0],
            'email': Email
        }
        response = requests.post(
            'https://www.instagram.com/api/v1/accounts/send_verify_email/',
            headers=Headers, data=data, proxies=proxies, timeout=30
        )
        return response.text
    except Exception as E:
        print(E)

def Validate_Code(Headers, Email, Code):
    try:
        data = {
            'code': Code,
            'device_id': Headers['cookie'].split('mid=')[1].split(';')[0],
            'email': Email
        }
        response = requests.post(
            'https://www.instagram.com/api/v1/accounts/check_confirmation_code/',
            headers=Headers, data=data, proxies=proxies, timeout=30
        )
        return response
    except Exception as E:
        print(E)

def get_random_file_from_folder(folder):
    if not os.path.exists(folder): return None
    valid_exts = ['.jpg', '.jpeg', '.png']
    files = [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in valid_exts]
    return os.path.join(folder, random.choice(files)) if files else None

def upload_profile_pic(sessionid, csrftoken, chat_id, retries=3):
    folder = 'Profile_pic'
    photo_path = get_random_file_from_folder(folder)
    if not photo_path:
        bot.send_message(chat_id, "⚠️ No profile pictures found in 'Profile_pic' folder. Skipping upload.")
        return
    url = 'https://www.instagram.com/accounts/web_change_profile_picture/'
    headers = {
        'cookie': f'sessionid={sessionid}; csrftoken={csrftoken};',
        'x-csrftoken': csrftoken,
        'referer': 'https://www.instagram.com/accounts/edit/',
        'x-requested-with': 'XMLHttpRequest',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    }
    for attempt in range(1, retries + 1):
        try:
            with open(photo_path, 'rb') as f:
                files = {'profile_pic': f}
                resp = requests.post(url, headers=headers, files=files, proxies=proxies)
            if resp.status_code == 200 and '"changed_profile":true' in resp.text:
                bot.send_message(chat_id, "✅ Profile picture uploaded!")
                return
        except:
            pass

def convert_to_professional(sessionid, csrftoken, chat_id, retries=3):
    url = "https://www.instagram.com/api/v1/business/account/convert_account/"
    headers = {
        'cookie': f'sessionid={sessionid}; csrftoken={csrftoken};',
        'x-csrftoken': csrftoken,
        'referer': 'https://www.instagram.com/accounts/convert_to_professional_account/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'content-type': 'application/x-www-form-urlencoded',
        'x-ig-app-id': '1217981644879628',
        'x-requested-with': 'XMLHttpRequest'
    }
    category_ids = ["180164648685982", "180410820992720", "180504230065143", "180213508993482", "180144472006690", "180559408665151"]
    data = {
        "category_id": random.choice(category_ids),
        "create_business_id": "true",
        "entry_point": "ig_web_settings",
        "set_public": "true",
        "should_bypass_contact_check": "true",
        "should_show_category": "0",
        "to_account_type": "3",
        "jazoest": "22663"
    }
    for attempt in range(1, retries + 1):
        try:
            resp = requests.post(url, headers=headers, data=data, proxies=proxies)
            if resp.status_code == 200 and '\"status\":\"ok\"' in resp.text:
                bot.send_message(chat_id, "✅ Converted to Professional Account!")
                return True
        except:
            pass
    return False

def Create_Acc(Headers, Email, SignUpCode, chat_id):
    try:
        firstname = names.get_first_name()
        UserName = Get_UserName(Headers, firstname, Email)
        Password = firstname.strip() + '@' + str(random.randint(111, 999))

        bot.send_message(chat_id, "⏳ Finalizing account creation...")
        data = {
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{round(time.time())}:{Password}',
            'email': Email,
            'username': UserName,
            'first_name': firstname,
            'month': random.randint(1, 12),
            'day': random.randint(1, 28),
            'year': random.randint(1990, 2001),
            'client_id': Headers['cookie'].split('mid=')[1].split(';')[0],
            'seamless_login_enabled': '1',
            'tos_version': 'row',
            'force_sign_up_code': SignUpCode,
        }

        response = requests.post(
            'https://www.instagram.com/api/v1/web/accounts/web_create_ajax/',
            headers=Headers, data=data, proxies=proxies, timeout=30
        )
        
        if '"account_created":true' in response.text:
            sessionid = response.cookies['sessionid']
            csrftoken = Headers['x-csrftoken']
            
            result_msg = (
                f"🎉 **Account Created Successfully!**\n\n"
                f"👤 **Username:** `{UserName}`\n"
                f"🔑 **Password:** `{Password}`\n"
                f"📧 **Email:** `{Email}`\n"
                f"🎫 **SessionID:** `{sessionid}`"
            )
            bot.send_message(chat_id, result_msg, parse_mode="Markdown")

            # Save to file locally (visible in Render logs or if persistent storage is used)
            with open('account_insta.txt', 'a') as f:
                f.write(f'UserName: {UserName} | Password: {Password} | Email: {Email}\n')

            upload_profile_pic(sessionid, csrftoken, chat_id)
            convert_to_professional(sessionid, csrftoken, chat_id)
            
            show_menu(chat_id, Email)
        else:
            bot.send_message(chat_id, f"❌ Account creation failed: {response.text}")
            show_menu(chat_id, Email)
    except Exception as E:
        bot.send_message(chat_id, f"❌ Error during account creation: {str(E)}")

# --- TELEGRAM HANDLERS ---

@bot.message_handler(commands=['start'])
def welcome(message):
    logo = "🚀 Instagram Auto Account Creator\nOwner: @DarkFrozenOwner\nChannel: @DarkFrozenGaming"
    bot.send_message(message.chat.id, logo)
    msg = bot.send_message(message.chat.id, "📧 Enter your Email to start:")
    bot.register_next_step_handler(msg, process_email)

def process_email(message):
    email = message.text.strip()
    chat_id = message.chat.id
    bot.send_message(chat_id, f"⏳ Requesting OTP for {email}...")
    
    headers = get_headers(Country='US', Language='en')
    ss = Send_SMS(headers, email)

    if 'email_sent":true' in ss:
        user_data[chat_id] = {'email': email, 'headers': headers}
        msg = bot.send_message(chat_id, "📥 Enter the OTP sent to your email:")
        bot.register_next_step_handler(msg, process_otp)
    else:
        bot.send_message(chat_id, "❌ Failed to send OTP. Try again with /start")

def process_otp(message):
    chat_id = message.chat.id
    otp = message.text.strip()
    
    if chat_id not in user_data:
        bot.send_message(chat_id, "Session expired. Use /start")
        return

    email = user_data[chat_id]['email']
    headers = user_data[chat_id]['headers']

    bot.send_message(chat_id, "⏳ Validating OTP...")
    a = Validate_Code(headers, email, otp)
    
    if 'status":"ok' in a.text:
        bot.send_message(chat_id, "✅ OTP Verified! Starting account creation...")
        SignUpCode = a.json()['signup_code']
        Create_Acc(headers, email, SignUpCode, chat_id)
    else:
        bot.send_message(chat_id, "❌ Invalid OTP. Use /start to try again.")

def show_menu(chat_id, email):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("1. Use same email", "2. Use new email", "3. Exit")
    msg = bot.send_message(chat_id, "What would you like to do next?", reply_markup=markup)
    bot.register_next_step_handler(msg, handle_menu_choice, email)

def handle_menu_choice(message, email):
    chat_id = message.chat.id
    choice = message.text
    if "1" in choice:
        # Re-trigger with same email
        bot.send_message(chat_id, f"Using same email: {email}")
        headers = get_headers(Country='US', Language='en')
        ss = Send_SMS(headers, email)
        if 'email_sent":true' in ss:
            user_data[chat_id] = {'email': email, 'headers': headers}
            msg = bot.send_message(chat_id, "📥 Enter the NEW OTP sent to your email:")
            bot.register_next_step_handler(msg, process_otp)
    elif "2" in choice:
        msg = bot.send_message(chat_id, "📧 Enter your NEW email:")
        bot.register_next_step_handler(msg, process_email)
    else:
        bot.send_message(chat_id, "👋 Done. Type /start to begin again.", reply_markup=telebot.types.ReplyKeyboardRemove())

if __name__ == "__main__":
    print(f"{rd}Starting Bot Service...{yw}By @DarkFrozenOwner✅")
    keep_alive()  # Start the background Flask server
    bot.infinity_polling()
