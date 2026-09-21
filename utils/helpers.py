# utils/helpers.py
# Chứa các hàm tiện ích chung
# Author: bluemanhst

import time
import random
import re
import queue
from datetime import datetime

# ===== HÀM KIỂM TRA SCHEDULE (HẸN GIỜ) =====
def is_in_schedule(schedule_enabled, start_time, end_time):
    """
    Kiểm tra xem thời gian hiện tại có nằm trong khung giờ schedule không
    
    Args:
        schedule_enabled (bool): Bật/tắt schedule
        start_time (str): Giờ bắt đầu (format HH:MM)
        end_time (str): Giờ kết thúc (format HH:MM)
    
    Returns:
        bool: True nếu trong khung giờ, False nếu ngoài khung giờ
    """
    if not schedule_enabled:
        return True  # Nếu không bật schedule thì luôn cho phép chạy
    
    try:
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Chuyển đổi thời gian sang phút để so sánh dễ hơn
        def time_to_minutes(time_str):
            """Chuyển HH:MM sang số phút"""
            hours, minutes = map(int, time_str.split(':'))
            return hours * 60 + minutes
        
        current_minutes = time_to_minutes(current_time)
        start_minutes = time_to_minutes(start_time)
        end_minutes = time_to_minutes(end_time)
        
        # Xử lý trường hợp qua ngày (ví dụ: 22:00 - 06:00)
        if start_minutes > end_minutes:
            # Nếu start > end nghĩa là qua ngày (tối đến sáng)
            return current_minutes >= start_minutes or current_minutes <= end_minutes
        else:
            # Bình thường (sáng đến chiều)
            return start_minutes <= current_minutes <= end_minutes
    except:
        return True  # Nếu có lỗi thì mặc định cho phép chạy


# ===== HÀM CHỜ CÓ THỂ DỪNG NGAY =====
def interruptible_sleep(seconds, bot_running_ref, run_id=None, generation_ref=None):
    """
    Hàm sleep có thể dừng ngay khi bấm nút DỪNG (chia nhỏ thành từng giây).

    Args:
        seconds (int|float): Số giây cần chờ
        bot_running_ref (list): Reference đến list [bot_running] để thread-safe
        run_id (int|None): Mã lượt chạy của thread hiện tại
        generation_ref (list|None): Reference đến list [generation] của app

    Returns:
        bool: True nếu cần dừng thread ngay (bị bấm DỪNG hoặc đã có lượt chạy mới)
    """
    remaining = float(seconds)
    while remaining > 0:
        if should_stop(bot_running_ref, run_id, generation_ref):
            return True
        chunk = 1.0 if remaining >= 1.0 else remaining
        time.sleep(chunk)
        remaining -= chunk

    return should_stop(bot_running_ref, run_id, generation_ref)


def should_stop(bot_running_ref, run_id=None, generation_ref=None):
    """
    Kiểm tra thread có phải dừng lại không.

    Dùng để tránh trường hợp: người dùng bấm DỪNG rồi bấm BẮT lại, các thread cũ
    còn đang ngủ sẽ "sống dậy" và gửi tin trùng với thread mới (double send).

    Args:
        bot_running_ref (list): list [bot_running]
        run_id (int|None): Mã lượt chạy của thread
        generation_ref (list|None): list [generation] của app

    Returns:
        bool: True nếu thread phải thoát
    """
    if not bot_running_ref[0]:
        return True

    if run_id is not None and generation_ref is not None and run_id != generation_ref[0]:
        return True

    return False


# ===== HÀM XỬ LÝ SPINTAX =====
def process_spintax(text):
    """
    Xử lý format Spintax {option1|option2|option3}
    Chọn ngẫu nhiên 1 option từ danh sách
    
    Args:
        text (str): Text chứa spintax
    
    Returns:
        str: Text sau khi xử lý spintax
    
    Ví dụ:
        Input: "Xin chào {Alice|Bob|Charlie}"
        Output: "Xin chào Bob" (ngẫu nhiên)
    """
    # Pattern chỉ match spintax có dấu | bên trong
    # {Hello|Hi|Hey} sẽ match, nhưng {time} sẽ không match
    pattern = r'\{([^{}|]+(?:\|[^{}|]+)+)\}'
    
    def replace_spintax(match):
        """Thay thế spintax bằng option ngẫu nhiên"""
        content = match.group(1)
        options = [opt.strip() for opt in content.split('|')]
        selected = random.choice(options)
        return selected
    
    # Thay thế từng spintax trong text
    text = re.sub(pattern, replace_spintax, text)
    
    return text


# ===== HÀM RANDOM HÓA NỘI DUNG TIN NHẮN =====
def randomize_content(text):
    """
    Random hóa nội dung tin nhắn để tránh bị phát hiện là spam
    Bao gồm: chèn emoji, khoảng trắng, viết hoa/thường, viết tắt
    
    Args:
        text (str): Tin nhắn gốc
    
    Returns:
        str: Tin nhắn sau khi random hóa
    """
    # 1. Random chèn emoji ở các vị trí ngẫu nhiên
    text = add_random_emojis(text)
    
    # 2. Random chèn khoảng trắng thừa
    text = add_random_spaces(text)
    
    # 3. Random viết hoa/thường một số từ
    text = randomize_case(text)
    
    # 4. Random viết tắt một số từ thông dụng
    text = add_random_abbreviations(text)
    
    return text


def add_random_emojis(text):
    """Chèn emoji ngẫu nhiên vào tin nhắn (30% cơ hội)"""
    emojis = ["😀", "😂", "🎉", "🔥", "💯", "⭐", "🚀", "💪", "👍", "❤️", "🌟", "✨", "😊", "🙌", "👋", "💫"]
    
    # 30% cơ hội chèn emoji
    if random.random() < 0.3:
        words = text.split()
        if len(words) > 2:
            # Chọn vị trí ngẫu nhiên để chèn (tránh đầu và cuối câu)
            insert_pos = random.randint(1, len(words) - 2)
            emoji = random.choice(emojis)
            words.insert(insert_pos, emoji)
            text = " ".join(words)
    
    return text


def add_random_spaces(text):
    """Chèn khoảng trắng thừa ngẫu nhiên (20% cơ hội mỗi từ)"""
    words = text.split()
    result = []
    
    for word in words:
        result.append(word)
        # 20% cơ hội thêm khoảng trắng thừa sau từ
        if random.random() < 0.2 and word not in ["😀", "😂", "🎉", "🔥", "💯", "⭐", "🚀", "💪", "👍", "❤️", "🌟", "✨", "😊", "🙌", "👋", "💫"]:
            # Thêm 1-2 khoảng trắng
            result.append(" " * random.randint(1, 2))
    
    return " ".join(result)


def randomize_case(text):
    """Random viết hoa/thường một số từ (30% cơ hội mỗi từ)"""
    words = text.split()
    result = []
    
    # Các từ có thể random hoa/thường (tránh emoji)
    common_words = ["xin", "chao", "hello", "hi", "moi", "nguoi", "everyone", "ban", "friend", 
                   "co", "ai", "khong", "no", "yes", "ok", "duoc", "roi"]
    
    for word in words:
        # Chỉ random các từ thông dụng, không phải emoji
        if word.lower() in common_words and len(word) > 2:
            # 30% cơ hội viết hoa, 30% viết thường, 40% giữ nguyên
            rand = random.random()
            if rand < 0.3:
                word = word.upper()
            elif rand < 0.6:
                word = word.lower()
        result.append(word)
    
    return " ".join(result)


def add_random_abbreviations(text):
    """Random viết tắt một số từ thông dụng (40% cơ hội)"""
    abbreviations = {
        "xin chao": ["chao", "hello", "hi", "helo", "xin chao"],
        "moi nguoi": ["m.n", "moi ng", "every1", "everyone", "ae"],
        "ban": ["b", "bn", "friend", "frend"],
        "duoc": ["dc", "ok", "oke", "duoc"],
        "roi": ["r", "ok", "yess", "duoc"],
        "khong": ["ko", "k", "no", "nop", "khong"],
        "co": ["co", "yes", "yep", "co"],
        "biet": ["bit", "know", "no", "biet"],
        "thoi": ["thui", "thi", "nvm", "thoi"]
    }

    result = text
    for full_form, abbrevs in abbreviations.items():
        # 40% cơ hội thay thế bằng viết tắt
        if random.random() >= 0.4:
            continue

        # Giữ nguyên chữ cái đầu viết hoa/thường giống từ gốc trong câu
        def _replace(match):
            original = match.group(0)
            chosen = random.choice(abbrevs)
            if original[:1].isupper():
                chosen = chosen.capitalize()
            return chosen

        result = re.sub(re.escape(full_form), _replace, result, count=1, flags=re.IGNORECASE)

    return result


# ===== HÀM XỬ LÝ SMART TEMPLATE =====
def process_smart_template(template):
    """
    Xử lý template tin nhắn thông minh
    Kết hợp spintax và random hóa nội dung
    
    Args:
        template (str): Template tin nhắn
    
    Returns:
        str: Tin nhắn sau khi xử lý
    """
    # Xử lý spintax trước
    template = process_spintax(template)
    
    # Random hóa nội dung
    template = randomize_content(template)
    
    return template


# ===== CẦU NỐI GHI LOG AN TOÀN TỪ THREAD PHỤ =====
class ThreadSafeLog:
    """
    Thay thế cho widget log khi truyền vào các thread gửi tin.

    Tkinter không thread-safe: ghi trực tiếp vào widget Text từ nhiều thread
    có thể làm treo/crash app. Class này chỉ đẩy dữ liệu vào hàng đợi, luồng
    chính (Tkinter) sẽ gọi drain() để thực sự ghi vào widget.

    Cách dùng:
        log_proxy = ThreadSafeLog()
        thread(...)                     # trong thread: log_proxy.insert("end", text, "tag")
        root.after(100, pump)           # luồng chính: log_proxy.drain(log_area)
    """

    def __init__(self):
        self.queue = queue.Queue()

    def insert(self, index, text, tag=None):
        """Giống Text.insert nhưng chỉ xếp vào hàng đợi (an toàn từ thread khác)"""
        self.queue.put((str(text), tag))

    def see(self, index=None):
        """Không cần làm gì - việc cuộn log do luồng chính xử lý"""
        return None

    def drain(self, widget):
        """
        Ghi toàn bộ log đang chờ vào widget (CHỈ gọi từ luồng chính).

        Args:
            widget (tk.Text): Widget log thật

        Returns:
            int: Số dòng log đã ghi
        """
        count = 0
        while True:
            try:
                text, tag = self.queue.get_nowait()
            except queue.Empty:
                break

            if tag:
                widget.insert("end", text, tag)
            else:
                widget.insert("end", text)
            count += 1

        if count:
            widget.see("end")

        return count

