# HTTP Data Exchange for IoT — Local Python Demo

Demo học phần **IoT và ứng dụng**: một HTTP Client gửi phép đo ánh sáng lên Server bằng **POST**, Server lưu phép đo vào **CSV**, và một HTTP Client khác truy xuất các phép đo bằng **GET**.

## 1. Kiến trúc

```text
Client 1 (sensor_client.py)             Client 2 (viewer_client.py)
  POST /api/light                         GET /api/light?area=1
         |                                         |
         v                                         v
                Flask HTTP Server (server.py)
                            |
                            v
                       data.csv
                  timestamp, area, lux
```

Hai Client độc lập, cùng truy cập HTTP Server chạy **trên laptop cá nhân** tại `http://127.0.0.1:5000`. Không cần ESP32, tài khoản Cloud hay Internet trong lúc chạy.

## 2. Chuẩn bị môi trường

Yêu cầu: **Python 3.10+**, có `pip`. Tải repository về máy (Git clone hoặc **Code → Download ZIP**) rồi mở Terminal trong thư mục `iot-python-http-demo`.

### Windows (PowerShell) — không cần activate virtual environment

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Nếu máy không nhận lệnh `py`, thay bằng `python` khi tạo virtual environment. Các lệnh phía dưới sử dụng Python trong `.venv`, không cần thay đổi Execution Policy của PowerShell.

### macOS / Linux

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

> Chỉ lần đầu mới cần cài thư viện Flask và requests. Các lần chạy sau không cần cài lại.

## 3. Chạy hệ thống (3 Terminal)

**Giữ Terminal 1 mở trong suốt quá trình demo.** Tất cả Terminal đều đặt tại thư mục dự án.

### Windows (PowerShell)

**Terminal 1 — HTTP Server:**

```powershell
.\.venv\Scripts\python.exe server.py
```

**Terminal 2 — Client 1: upload dữ liệu cảm biến (POST):**

```powershell
.\.venv\Scripts\python.exe sensor_client.py
```

Kỳ vọng: Client 1 tạo `timestamp` theo đồng hồ của máy, gửi cùng `area=1`, `lux=500`; nhận `HTTP status: 201`. Server lưu nguyên timestamp từ Client vào `data.csv`.

**Terminal 3 — Client 2: truy xuất dữ liệu (GET):**

```powershell
.\.venv\Scripts\python.exe viewer_client.py
```

Kỳ vọng: `HTTP status: 200`; Terminal hiển thị phép đo vừa được lưu.

### macOS / Linux

Thực hiện theo cùng thứ tự bằng các lệnh:

```bash
./.venv/bin/python server.py
./.venv/bin/python sensor_client.py
./.venv/bin/python viewer_client.py
```

Chạy mỗi lệnh ở một Terminal riêng. Dừng Server bằng `Ctrl+C`.

## 4. Thử thay đổi dữ liệu

Trên Windows:

```powershell
.\.venv\Scripts\python.exe sensor_client.py --area 1 --lux 520
.\.venv\Scripts\python.exe sensor_client.py --area 2 --lux 300
.\.venv\Scripts\python.exe viewer_client.py --area 1
.\.venv\Scripts\python.exe viewer_client.py --area 2
```

macOS/Linux: thay ` .\.venv\Scripts\python.exe ` bằng ` ./.venv/bin/python `.

Mỗi lần chạy Sensor Client sẽ **thêm một dòng mới** vào CSV. Client 2 trả về **danh sách tất cả phép đo** thuộc khu vực được yêu cầu (không chỉ phép đo mới nhất).

Ví dụ file `data.csv` sau 2 lần POST:

```csv
timestamp,area,lux
2026-11-25 05:44:35,1,500
2026-11-25 05:44:40,1,520
```

Timestamp do **Sensor Client tạo ở thời điểm lấy phép đo**, dùng đồng hồ **giờ địa phương của máy chạy Sensor Client**, định dạng `YYYY-MM-DD HH:MM:SS` (chính xác đến giây, không kèm mili-giây).

## 5. API Contract

### POST `/api/light`

Request Body (`application/json`):

```json
{"timestamp":"2025-05-02 05:44:35","area":1,"lux":500}
```

Response: **201 Created**

```text
  "success"
```

Yêu cầu: `timestamp` là chuỗi theo đúng định dạng `YYYY-MM-DD HH:MM:SS` và là thời điểm hợp lệ; `area` là số nguyên dương; `lux` là số không âm. Ba trường đều bắt buộc.

- **400 Bad Request** nếu JSON hoặc giá trị dữ liệu không hợp lệ.
- **415 Unsupported Media Type** nếu Request không có `Content-Type: application/json`.
- **500 Internal Server Error** nếu Server không thể ghi file.

### GET `/api/light?area=1`

Response: **200 OK**

```json
{
  "count": 1,
  "data": [
    {"timestamp": "2025-05-02 05:44:35", "area": 1, "lux": 500}
  ]
}
```

Nếu chưa có phép đo phù hợp: `200 OK` với `"count": 0` và `"data": []`.
