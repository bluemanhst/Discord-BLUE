# Discord BLUE 🚀

🌐 **Đọc bằng ngôn ngữ khác / Read in other languages:**
- [🇬🇧 English](docs/README.en.md)
- [🇨🇳 中文](docs/README.zh.md)

> ⚠️ **LƯU Ý SỬ DỤNG & TUÂN THỦ ĐIỀU KHOẢN (nên đọc trước khi dùng)**
> * Dự án được phát hành cho mục đích **học tập, nghiên cứu kỹ thuật và kiểm thử tự động hóa**.
> * Chỉ sử dụng trên **tài khoản của chính bạn** và trên máy chủ/kênh mà bạn **được phép**.
> * Tự động hóa tài khoản người dùng (self-bot) và gửi tin hàng loạt có thể **vi phạm Điều khoản dịch vụ của Discord**; bạn tự chịu mọi rủi ro (khóa tài khoản, xử lý pháp lý…).
> * **Không** dùng công cụ để spam, lừa đảo, quảng cáo rác, quấy rối hoặc xâm phạm quyền của người khác.

---

**Discord BLUE** (bởi *bluemanhst*) là ứng dụng tự động hóa gửi tin nhắn đa luồng trên Discord với giao diện đồ họa (GUI) trực quan, được trang bị đầy đủ các cơ chế giả lập hành vi người dùng thật nhằm hạn chế tối đa nguy cơ bị Discord khóa tài khoản (Anti-Ban / Anti-Spam).

---

## 📥 TẢI ỨNG DỤNG (BẢN BUILD EXE)

Bạn có thể tải file `.exe` sử dụng trực tiếp mà không cần cài đặt Python:

🔗 **[TẢI PHIÊN BẢN DISCORD BLUE MỚI NHẤT](https://github.com/bluemanhst/Discord-BLUE/releases)**

*(Tải file `Discord BLUE.exe` ở phần Assets của phiên bản mới nhất).*

---

## ✨ TÍNH NĂNG NỔI BẬT

### 👥 1. Đa tài khoản & Đa luồng (Multi-Account)
* Chạy cùng lúc không giới hạn số lượng tài khoản Discord.
* Mỗi tài khoản hoạt động trên một **Thread độc lập**, tự động rải tin ngẫu nhiên qua danh sách các kênh (channel).
* Cơ chế dừng khẩn cấp: Nút **DỪNG TẤT CẢ** ngắt ngay lập tức mọi luồng, không bị delay.

### 🛡️ 2. Cơ chế chống phát hiện Spam (Anti-Detection)
* **Auto Typing (Giả lập gõ phím)**: Bật trạng thái *"Đang gõ..."* ngẫu nhiên trước khi gửi tin để trông giống người thật.
* **Cooldown ngẫu nhiên**: Tùy chỉnh thời gian chờ ngẫu nhiên giữa các lần gửi (ví dụ: nghỉ từ 60s đến 90s).
* **Auto Break (Nghỉ dài định kỳ)**: Cứ sau một số lượng tin nhất định (ví dụ: 15–25 tin), bot sẽ tự động cho tài khoản nghỉ dài (ví dụ: 10–30 phút) rồi mới chạy tiếp.
* **Auto Stop on Ban**: Tự động nhận diện và dừng riêng tài khoản nếu bị cấm, kick hoặc mute khỏi kênh (mã lỗi HTTP `403`, `404`), không làm ảnh hưởng các tài khoản khác.
* **Smart Templates & Spintax**:
  * Hỗ trợ cú pháp Spintax: `{Chào bạn|Hello|Hi mọi người}`.
  * Tự động biến thể tin nhắn: chèn emoji ngẫu nhiên, thêm khoảng trắng ngẫu nhiên, đổi hoa/thường, viết tắt từ thông dụng.

### 🗑️ 3. Tự động xóa tin nhắn (Auto Delete)
* Tự động xóa tin nhắn sau khi gửi với thời gian chờ tùy chỉnh (tính theo mili-giây).
* Thích hợp cho việc cày cấp độ (level/XP bot) trên các server mà không lưu lại tin nhắn rác trong kênh chat.

### ⏰ 4. Hẹn giờ hoạt động (Schedule)
* Cấu hình khung giờ chạy tự động trong ngày (ví dụ: chỉ chạy từ `09:00` đến `17:00`). Ngoài khung giờ này, bot sẽ tự động tạm nghỉ chờ đến giờ.

### 🔍 5. Kiểm tra Token (Token Validator)
* Tích hợp công cụ kiểm tra danh sách Discord Tokens trực tiếp qua API:
  * Kiểm tra token sống / hết hạn / bị khóa.
  * Xem Avatar, Username, User ID, Email, Phone, xác thực 2 bước (2FA), phân loại Token.

### 📊 6. Thống kê thời gian thực (Realtime Dashboard)
* Theo dõi: Thời gian chạy (Runtime), tổng tin đã gửi, tổng tin đã xóa, số lỗi, số tài khoản online, tốc độ gửi (tin/phút), tỷ lệ gửi thành công (%).
* Bảng thống kê chi tiết số tin nhắn/lỗi theo từng tài khoản và từng channel.
* Hỗ trợ nút **Export** xuất toàn bộ thống kê ra file `.json`.

### 🎨 7. Tùy biến giao diện & Cài đặt hệ thống
* **3 Giao diện tùy chọn**: *Dragon Ball* (mặc định), *Discord*, *Dark Professional*.
* **Đa ngôn ngữ**: Hỗ trợ đầy đủ Tiếng Việt, Tiếng Anh (English) và Tiếng Trung (中文).
* **System Tray**: Thu nhỏ ứng dụng xuống khay hệ thống góc màn hình khi bấm nút đóng (X).
* **Khởi động cùng Windows**: Tùy chọn tự động chạy tool khi bật máy tính.
* **Âm thanh thông báo**: Phát tiếng chuông khi gửi thành công, khi gặp lỗi hoặc khi dừng tool.
* **Quản lý cấu hình**: Tự động lưu `config.json`, hỗ trợ nút **Export/Import** để sao lưu hoặc chuyển cấu hình sang máy khác.

---

## 📖 HƯỚNG DẪN SỬ DỤNG DÀNH CHO NGƯỜI DÙNG

### Bước 1: Thiết lập cấu hình ban đầu
1. Mở ứng dụng **Discord BLUE**.
2. Tại tab **TRANG CHÍNH**:
   * **Danh sách Discord Tokens**: Dán danh sách token của bạn vào (mỗi tài khoản 1 dòng).
   * *(Tùy chọn)* Bấm nút **"✅ KIỂM TRA TOKEN"** để kiểm tra xem tài khoản nào còn hoạt động.
   * **Target Channel ID**: Nhập các ID kênh bạn muốn gửi tin (mỗi kênh 1 dòng). Tool sẽ tự động rải đều tin qua các kênh này.
   * **Cooldown Min / Cooldown Max**: Điền thời gian chờ ngẫu nhiên giữa 2 lần gửi (tính bằng giây, khuyến nghị: 60 - 90s).
   * **Danh sách câu chat**: Nhập danh sách nội dung tin nhắn cần gửi (mỗi câu 1 dòng).

### Bước 2: Bật các tính năng bảo vệ tài khoản
1. Chuyển sang tab **TÍNH NĂNG**:
   * Tích chọn **Auto Typing** nếu muốn giả lập đang gõ trước khi gửi.
   * Tích chọn **Auto Break** để bot tự động nghỉ dài định kỳ sau một số tin.
   * Tích chọn **Smart Templates** nếu muốn tin nhắn tự động biến đổi ngẫu nhiên tránh bị Discord đánh dấu spam.
   * Tích chọn **Auto Delete** nếu muốn xóa tin sau khi gửi.
   * Tích chọn **Schedule** nếu chỉ muốn tool chạy trong khung giờ nhất định.

### Bước 3: Khởi chạy
1. Quay lại tab **TRANG CHÍNH** và bấm nút **"BẬT DISCORD BLUE"**.
2. Quan sát nhật ký gửi tin trực tiếp ở khung **Nhật ký hoạt động** bên dưới.
3. Chuyển qua tab **DASHBOARD** và bấm **"CẬP NHẬT"** để xem số liệu thống kê chi tiết.
4. Muốn dừng tool, bấm nút **"DỪNG TẤT CẢ"**.

---

## 🛠️ CÀI ĐẶT & CHẠY TỪ SOURCE CODE (DÀNH CHO LẬP TRÌNH VIÊN)

### Yêu cầu môi trường
* Python 3.8 trở lên trên hệ điều hành Windows.

### Cài đặt thư viện
```bash
pip install requests Pillow pystray
```

### Chạy ứng dụng
```bash
python main.pyw
```

---

## 📦 ĐÓNG GÓI THÀNH FILE EXE

Dự án đã tích hợp sẵn script tự động kiểm tra thư viện và build file EXE:

1. Chạy file:
   ```cmd
   build.bat
   ```
2. Sau khi build hoàn tất, file `Discord BLUE.exe` sẽ nằm trong thư mục `dist/`.

---

## 📌 LƯU Ý QUAN TRỌNG

* **File `config.json`**: Chứa token Discord của bạn. File này luôn được tạo cùng thư mục với file `.exe` (hoặc ở thư mục gốc khi chạy source). Không bao giờ chia sẻ file `config.json` cho người khác.
* **Đổi Theme / Ngôn ngữ**: Sau khi chọn Theme mới hoặc đổi Ngôn ngữ trong tab Cài đặt, vui lòng tắt và mở lại tool để giao diện áp dụng hoàn toàn.
* **Khay hệ thống (System Tray)**: Cần có thư viện `pystray`. Khi bật tính năng này, nhấn nút `X` sẽ thu nhỏ tool xuống khay góc phải màn hình; click đúp vào icon để mở lại hoặc chuột phải chọn "Thoát".

---

---

## ⚖️ GIẤY PHÉP & BẢN QUYỀN (LICENSE)

Dự án được phân phối dưới giấy phép [MIT License](LICENSE). Bạn có toàn quyền sử dụng, sửa đổi và phân phối theo các điều khoản của giấy phép này.

---

## ⚠️ TUYÊN BỐ MIỄN TRỪ TRÁCH NHIỆM (DISCLAIMER)

* **Không liên kết với Discord Inc.**: Phần mềm này là dự án độc lập, **KHÔNG** được tài trợ, ủy quyền, duy trì hay có bất kỳ mối liên hệ chính thức nào với Discord Inc. Logo và thương hiệu Discord thuộc quyền sở hữu của Discord Inc.
* **Mục đích sử dụng**: Ứng dụng này được phát triển hoàn toàn cho mục đích **học tập, nghiên cứu kỹ thuật và kiểm thử tự động hóa (Educational & Testing Purposes)**.
* **Trách nhiệm người dùng**: Việc sử dụng các công cụ tự động hóa trên tài khoản người dùng cá nhân (Self-bot) có thể vi phạm [Điều khoản dịch vụ của Discord (Discord Terms of Service)](https://discord.com/terms). Người dùng tự chịu trách nhiệm hoàn toàn đối với mọi hành vi và rủi ro liên quan đến tài khoản của mình. Tác giả không chịu trách nhiệm cho bất kỳ tổn thất, tranh chấp hoặc thiệt hại nào phát sinh từ việc sử dụng phần mềm này.

---

## 👨‍💻 TÁC GIẢ & LIÊN HỆ

* **Tác giả**: bluemanhst
* **Discord**: [bluemanhst](https://discord.com/users/481280614956400690)
* **Facebook**: [bluemanhst](https://www.facebook.com/bluemanhstv4seo)


