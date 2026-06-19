import requests
import os
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL = '@dollar_price98'
LAST_PRICE_FILE = 'last_price.txt'

def get_dollar_price():
    """دریافت قیمت دلار آزاد از tgju.org"""
    try:
        url = 'https://api.tgju.org/v1/market/indicator/summary-table-data/price_dollar_rl'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # قیمت دلار آزاد
        price = int(data['p'])
        return price
    except Exception as e:
        print(f"خطا در دریافت قیمت: {e}")
        return None

def get_last_price():
    """خواندن آخرین قیمت ذخیره شده"""
    try:
        if os.path.exists(LAST_PRICE_FILE):
            with open(LAST_PRICE_FILE, 'r') as f:
                return int(f.read().strip())
    except:
        pass
    return None

def save_price(price):
    """ذخیره قیمت جدید"""
    with open(LAST_PRICE_FILE, 'w') as f:
        f.write(str(price))

def send_telegram_message(message):
    """ارسال پیام به کانال تلگرام"""
    try:
        url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
        payload = {
            'chat_id': TELEGRAM_CHANNEL,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("پیام با موفقیت ارسال شد")
        return True
    except Exception as e:
        print(f"خطا در ارسال پیام: {e}")
        return False

def format_price(price):
    """فرمت کردن قیمت با جداکننده"""
    return f"{price:,}".replace(',', '،')

def main():
    current_price = get_dollar_price()
    
    if current_price is None:
        print("نتوانستم قیمت را دریافت کنم")
        return
    
    last_price = get_last_price()
    
    print(f"قیمت فعلی: {format_price(current_price)} تومان")
    
    if last_price is None:
        # اولین بار
        message = f"🔔 <b>قیمت دلار آزاد</b>\n\n💵 {format_price(current_price)} تومان\n\n🕐 {datetime.now().strftime('%Y/%m/%d - %H:%M:%S')}"
        send_telegram_message(message)
        save_price(current_price)
        print("قیمت اولیه ذخیره شد")
    elif current_price != last_price:
        # قیمت تغییر کرده
        diff = current_price - last_price
        diff_text = f"+{format_price(diff)}" if diff > 0 else format_price(diff)
        emoji = "📈" if diff > 0 else "📉"
        
        message = f"{emoji} <b>تغییر قیمت دلار آزاد</b>\n\n"
        message += f"💵 قیمت جدید: {format_price(current_price)} تومان\n"
        message += f"📊 قیمت قبلی: {format_price(last_price)} تومان\n"
        message += f"{'🔺' if diff > 0 else '🔻'} تغییر: {diff_text} تومان\n\n"
        message += f"🕐 {datetime.now().strftime('%Y/%m/%d - %H:%M:%S')}"
        
        send_telegram_message(message)
        save_price(current_price)
        print(f"قیمت تغییر کرده: {last_price} -> {current_price}")
    else:
        print("قیمت تغییری نداشته")

if __name__ == '__main__':
    main()
