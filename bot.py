import asyncio
import aiohttp
import json
import random
import time
import sys
import re
import os
import base64
from io import BytesIO
from PIL import Image
from fake_useragent import UserAgent
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ── CONFIG ──
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8874356199:AAGvs9dZJB-trVJLmDOWZINln3OSiNNhwtc")

TARSIERS_API = "https://api.tarsiers.bet"
TARSIERS_WEB = "https://www.tarsiers.bet"
SSPAY_URL = "https://www.sspay01.com"
PASSWORD = "qwe123"
TYPE = "phone"
AREA_CODE = "63"
OS_TYPE = "pc"
RECHARGE_AMOUNT = 1000
RECHARGE_TYPE = "GCash"
RECHARGE_CHANNEL = 1

# App markets
APP_MARKETS = [
    "TE32wBqek5m0HYE6GkxYJ",
    "UF43xC rfL6n1IZF7HlyZK",
    "VG54yDsgM7o2JAG8ImzAL",
    "WH65zEthN8p3KBH9JnaBM",
    "XI76aFuiO9q4LCI0KobCN",
]

SOURCES = ["001", "002", "003", "004", "005", "006", "007", "008", "009", "010"]

# Parse proxies from environment variable
PROXY_LIST = os.getenv("PROXIES", "").strip()
PROXIES = []

if PROXY_LIST:
    # Format: user:pass@host:port,user:pass@host:port
    for proxy_str in PROXY_LIST.split(','):
        proxy_str = proxy_str.strip()
        if not proxy_str:
            continue
        try:
            # Parse user:pass@host:port
            auth_host = proxy_str.split('@')
            auth = auth_host[0].split(':')
            host_port = auth_host[1].split(':')
            PROXIES.append({
                "username": auth[0],
                "password": auth[1],
                "host": host_port[0],
                "port": int(host_port[1]),
                "country": "ph"
            })
        except:
            pass
else:
    # Default proxies if no env variable
    PROXIES = [
        {"username": "ad65f9b0393c2aed4638__cr.ph", "password": "53c82f6ebffdc49e", "host": "gw.dataimpulse.com", "port": 823, "country": "ph"},
        {"username": "663ea6c747410f559675__cr.ph", "password": "faf33389a7a6aad9", "host": "gw.dataimpulse.com", "port": 823, "country": "ph"},
        {"username": "78ccfb89bf6dfa458094__cr.ph", "password": "1eda185143fae5d1", "host": "gw.dataimpulse.com", "port": 823, "country": "ph"},
    ]

# Track proxy usage
proxy_counter = 0
ua = UserAgent()

# ════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════
def generate_ph_mobile():
    prefixes = ["908","909","917","918","919","920","921","922","926","927","928","929","930","931","932","933","934","935","936","937","938","939","940","941","942","943","944","945","946","947","948","949","950","951","952","953","954","955","956","957","958","959","960","961","962","963","964","965","966","967","968","969","970","971","972","973","974","975","976","977","978","979","980","981","982","983","984","985","986","987","988","989","990","991","992","993","994","995","996","997","998","999"]
    return random.choice(prefixes) + str(random.randint(1000000, 9999999))

def get_next_proxy():
    """Get next proxy in round-robin fashion"""
    global proxy_counter
    if not PROXIES:
        return None
    proxy = PROXIES[proxy_counter % len(PROXIES)]
    proxy_counter += 1
    return proxy

def get_random_headers(host, origin, referer, content_type=True):
    fp = {
        "user_agent": ua.random,
        "sec_ch_ua": f'"{random.choice(["Google Chrome", "Microsoft Edge", "Chromium"])}";v="{random.randint(100, 130)}", "Not=A?Brand";v="99"',
        "sec_ch_ua_platform": random.choice(['"Windows"', '"macOS"', '"Linux"']),
        "accept_language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "en-PH,en;q=0.7"]),
    }
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": fp["accept_language"],
        "Connection": "keep-alive",
        "device": "pc",
        "Host": host,
        "Origin": origin,
        "Referer": referer,
        "sec-ch-ua": fp["sec_ch_ua"],
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": fp["sec_ch_ua_platform"],
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": fp["user_agent"],
    }
    
    if content_type:
        headers["Content-Type"] = "application/x-www-form-urlencoded;charset=UTF-8"
    
    return headers

# ════════════════════════════════════════════════
# TARSIERS API FUNCTIONS
# ════════════════════════════════════════════════
async def register_tarsiers(proxy_cfg):
    proxy_url = None
    if proxy_cfg and proxy_cfg.get("host"):
        p = proxy_cfg
        proxy_url = f"http://{p['username']}:{p['password']}@{p['host']}:{p['port']}"

    phone = generate_ph_mobile()
    app_market = random.choice(APP_MARKETS)
    source = random.choice(SOURCES)
    
    headers = get_random_headers("api.tarsiers.bet", TARSIERS_WEB, f"{TARSIERS_WEB}/")
    
    data = {
        "app_market": app_market,
        "area_code": AREA_CODE,
        "captcha": "",
        "fbclid": "",
        "inviteCode": "",
        "os_type": OS_TYPE,
        "password": PASSWORD,
        "phone": phone,
        "repassword": PASSWORD,
        "source": source,
        "type": TYPE
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{TARSIERS_API}/user/register/phone",
                headers=headers,
                data=data,
                proxy=proxy_url,
                timeout=30
            ) as resp:
                
                if resp.status == 200:
                    json_data = await resp.json()
                    code = json_data.get("code", -1)
                    
                    if code == 0:
                        data_obj = json_data.get("data", {})
                        token = data_obj.get("access_token")
                        return {"success": True, "phone": phone, "token": token}
                return {"success": False, "phone": phone}
        except Exception as e:
            return {"success": False, "phone": phone, "error": str(e)}

async def create_recharge_order(proxy_cfg, token):
    proxy_url = None
    if proxy_cfg and proxy_cfg.get("host"):
        p = proxy_cfg
        proxy_url = f"http://{p['username']}:{p['password']}@{p['host']}:{p['port']}"

    headers = get_random_headers("api.tarsiers.bet", TARSIERS_WEB, f"{TARSIERS_WEB}/")
    headers["token"] = token
    headers["Cookie"] = f"access_token={token}"
    
    data = {
        "amount": RECHARGE_AMOUNT,
        "channel": RECHARGE_CHANNEL,
        "rechargeTag": "",
        "type": RECHARGE_TYPE
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{TARSIERS_API}/wallet/recharge/order",
                headers=headers,
                data=data,
                proxy=proxy_url,
                timeout=30
            ) as resp:
                if resp.status == 200:
                    json_data = await resp.json()
                    if json_data.get("code") == 0:
                        data_obj = json_data.get("data", {})
                        return {
                            "success": True,
                            "order_no": data_obj.get("orderNo"),
                            "cashier": data_obj.get("cashier"),
                            "qrcode": data_obj.get("qrcode"),
                            "amount": data_obj.get("amount")
                        }
                return {"success": False}
        except Exception as e:
            return {"success": False, "error": str(e)}

async def get_qr_from_sspay(qr_url, proxy_cfg):
    proxy_url = None
    if proxy_cfg and proxy_cfg.get("host"):
        p = proxy_cfg
        proxy_url = f"http://{p['username']}:{p['password']}@{p['host']}:{p['port']}"

    async with aiohttp.ClientSession() as session:
        try:
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive",
                "Host": "www.sspay01.com",
                "Referer": TARSIERS_WEB,
                "sec-ch-ua": '"Not=A?Brand";v="99", "Microsoft Edge";v="151", "Chromium";v="151"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "cross-site",
                "Sec-Fetch-User": "?1",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36 Edg/151.0.0.0"
            }
            
            async with session.get(qr_url, headers=headers, proxy=proxy_url, allow_redirects=True, timeout=30) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    qr_match = re.search(r'<img[^>]+src="(data:image/png;base64,[^"]+)"', html)
                    if qr_match:
                        qr_data = qr_match.group(1)
                        if qr_data.startswith('data:image/png;base64,'):
                            return qr_data.replace('data:image/png;base64,', '')
                    
                    # Fallback: QR server
                    qr_api_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={qr_url}"
                    async with session.get(qr_api_url, proxy=proxy_url, timeout=30) as qr_resp:
                        if qr_resp.status == 200:
                            img_data = await qr_resp.read()
                            return base64.b64encode(img_data).decode('utf-8')
                    
                    return None
        except Exception as e:
            print(f"QR Error: {e}")
            return None

# ════════════════════════════════════════════════
# TELEGRAM BOT HANDLERS
# ════════════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔐 Register New Account", callback_data='register')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤖 Tarsiers.bet Registration Bot\n\n"
        f"Click the button below to register a new account!\n\n"
        f"📱 Auto Recharge: ₱{RECHARGE_AMOUNT}\n"
        f"🏦 Payment: {RECHARGE_TYPE}\n"
        f"🔄 Each registration uses different IP",
        reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'register':
        await query.edit_message_text("🔄 Processing registration...\nPlease wait...")
        
        proxy = get_next_proxy()
        proxy_info = f"{proxy['host']}:{proxy['port']}" if proxy else "No proxy"
        
        reg_result = await register_tarsiers(proxy)
        
        if not reg_result["success"]:
            await query.edit_message_text(
                f"❌ Registration Failed!\n\n"
                f"Error: {reg_result.get('error', 'Unknown error')}\n\n"
                f"Please try again."
            )
            return
        
        phone = reg_result["phone"]
        token = reg_result["token"]
        
        order_result = await create_recharge_order(proxy, token)
        
        if not order_result["success"]:
            await query.edit_message_text(
                f"✅ Registered: {phone}\n"
                f"❌ Recharge Failed!\n\n"
                f"Error: {order_result.get('error', 'Unknown error')}"
            )
            return
        
        order_no = order_result.get("order_no")
        cashier = order_result.get("cashier")
        amount = order_result.get("amount", RECHARGE_AMOUNT)
        
        await query.edit_message_text(
            f"✅ Registered: {phone}\n"
            f"✅ Recharge Created!\n"
            f"💰 Amount: ₱{amount}\n"
            f"🆔 Order: {order_no}\n\n"
            f"📱 Fetching QR Code..."
        )
        
        qr_base64 = await get_qr_from_sspay(cashier, proxy)
        
        if qr_base64:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=base64.b64decode(qr_base64),
                caption=f"💵 Pay ₱{amount} via {RECHARGE_TYPE}\n\n"
                        f"📱 Phone: {phone}\n"
                        f"🆔 Order: {order_no}"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔄 Register Another", callback_data='register')],
                [InlineKeyboardButton("📱 Open Payment Link", url=cashier)]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✅ Done! Scan the QR code above or click the link below.",
                reply_markup=reply_markup
            )
        else:
            keyboard = [[InlineKeyboardButton("📱 Open Payment Link", url=cashier)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"✅ Registration Complete!\n\n"
                f"📱 Phone: {phone}\n"
                f"💰 Amount: ₱{amount}\n"
                f"🆔 Order: {order_no}\n\n"
                f"Click the button below to open payment page.",
                reply_markup=reply_markup
            )
    
    elif query.data == 'help':
        await query.edit_message_text(
            f"📖 Help Guide\n\n"
            f"🔐 Register: Creates a new account and auto-recharge ₱{RECHARGE_AMOUNT}\n"
            f"📱 QR Code: Will be sent as image after registration\n"
            f"💰 Payment: Scan QR with {RECHARGE_TYPE}\n"
            f"🔄 Each registration uses different IP/proxy\n\n"
            f"⚠️ Make sure to complete payment within 10 minutes."
        )

# ════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════
async def main():
    print("╔══════════════════════════════════════════════╗")
    print("║  TARSIERS TELEGRAM REG BOT                  ║")
    print("║  Deployed on Render                         ║")
    print("╚══════════════════════════════════════════════╝")
    print(f"\n[INFO] Proxies loaded: {len(PROXIES)}")
    print(f"[INFO] Recharge: ₱{RECHARGE_AMOUNT} via {RECHARGE_TYPE}")
    print("[INFO] Bot is running...\n")
    
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("reg", button_callback))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    # Keep running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[!] Stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()