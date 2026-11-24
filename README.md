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

Yêu cầu: **Python 3.10+**, có `pip`. Tải repository về máy (Git clone hoặc **Code → Download ZIP**) rồi mở Terminal trong thư mục `iot-http-demo`.

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
2025-05-02 05:44:35,1,500
2025-05-02 05:44:40,1,520
```

Timestamp do **Sensor Client tạo ở thời điểm lấy phép đo**, dùng đồng hồ **giờ địa phương của máy chạy Sensor Client**, định dạng `YYYY-MM-DD HH:MM:SS` (chính xác đến giây, không kèm mili-giây). Server **không tự tạo lại timestamp** mà kiểm tra và ghi đúng giá trị nhận được. Thời gian thực tế sẽ khác ví dụ trên.

Để bài demo đơn giản và dễ quan sát, **mỗi lần chạy `sensor_client.py` chỉ gửi một phép đo**. Chưa cần vòng lặp gửi mỗi 5 giây hay tự sinh lux ngẫu nhiên; đây có thể là bài tập mở rộng.

> Định dạng minh họa không chứa múi giờ. Trong hệ thống nhiều thiết bị thực tế, nên dùng timestamp có thông tin múi giờ (ví dụ UTC theo ISO 8601) và đồng bộ đồng hồ thiết bị.

## 5. API Contract

### POST `/api/light`

Request Body (`application/json`):

```json
{"timestamp":"2025-05-02 05:44:35","area":1,"lux":500}
```

Response: **201 Created**

```json
{
  "status": "success",
  "measurement": {
    "timestamp": "2025-05-02 05:44:35",
    "area": 1,
    "lux": 500
  }
}
```

Yêu cầu: `timestamp` là chuỗi theo đúng định dạng `YYYY-MM-DD HH:MM:SS` và là thời điểm hợp lệ; `area` là số nguyên dương; `lux` là số không âm. Ba trường đều bắt buộc.

- **400 Bad Request** nếu JSON hoặc giá trị dữ liệu không hợp lệ.
- **415 Unsupported Media Type** nếu Request không có `Content-Type: application/json`.
- **500 Internal Server Error** nếu Server không thể ghi file.

### GET `/api/light?area=1`

Response: **200 OK**

```json
{
  "area": 1,
  "count": 1,
  "measurements": [
    {"timestamp": "2025-05-02 05:44:35", "area": 1, "lux": 500}
  ]
}
```

Nếu chưa có phép đo phù hợp: `200 OK` với `"count": 0` và `"measurements": []`. Nếu `area` không hợp lệ: `400 Bad Request`.

> **Lưu ý:** GET ở demo này trả về **danh sách bản ghi**, khác ví dụ minh họa tối giản `{ "area": 1, "lux": 500 }` trong slide lý thuyết. Cách thiết kế này giúp sinh viên quan sát việc Server lưu trữ nhiều phép đo.

## 6. Kiểm tra tự động (tùy chọn)

Sau khi cài dependencies, mở một Terminal và chạy:

**Windows:**

```powershell
.\.venv\Scripts\python.exe -m unittest -v test_demo
```

**macOS / Linux:**

```bash
./.venv/bin/python -m unittest -v test_demo
```

Các bài kiểm tra dùng Flask test client và một CSV tạm; **không làm thay đổi `data.csv` của demo**.

## 7. Bài tập gợi ý cho sinh viên

1. Chạy Sensor Client ba lần với các giá trị `lux` khác nhau; quan sát file CSV và kết quả GET.
2. Gửi dữ liệu cho `area=2`; kiểm tra Client 2 chỉ nhận đúng khu vực được yêu cầu. Đối chiếu `timestamp` trong Client, CSV và Response.
3. Gửi `--lux -5`: giải thích vì sao Server trả `400 Bad Request` và không ghi dữ liệu.
4. **Mở rộng:** chỉnh Sensor Client để gửi một phép đo mỗi 5 giây, có thể tạo ngẫu nhiên `lux` trong một khoảng định trước.
5. **Mở rộng thêm:** bổ sung tham số lọc các phép đo có `lux` lớn hơn một ngưỡng định trước.

## 8. Lưu ý và xử lý sự cố

- **Connection refused / ConnectionError:** Chưa chạy `server.py` hoặc Server đang ở cổng khác. Hãy giữ Terminal Server mở.
- **Port 5000 is in use:** Dừng tiến trình đang chiếm cổng 5000 trước khi chạy demo.
- **ModuleNotFoundError:** Kiểm tra đã cài `requirements.txt` và gọi đúng Python trong `.venv`.
- **CSV có dữ liệu cũ (hoặc timestamp từ phiên bản trước):** Dừng Server, xóa file `data.csv`, chạy lại Server và Client 1 để làm mới.
- **Security:** Chương trình chỉ phục vụ mục đích học tập, chạy HTTP trên `127.0.0.1` và chưa có HTTPS, xác thực người dùng, hay cơ chế lưu trữ an toàn cho nhiều Client đồng thời. Không mở trực tiếp ra Internet. `app.run()` là development server, không phải production server.

## 9. Kiến thức HTTP được minh họa

| Kiến thức | Trong code |
|---|---|
| HTTP Client–Server | `requests` → Flask Server |
| POST | `requests.post(..., json=data)` |
| GET + Query Parameters | `requests.get(..., params={"area": 1})` |
| HTTP Status Codes | `201`, `200`, `400`, `415` |
| Request/Response Body | JSON |
| Sensor-generated timestamp | `datetime.now().strftime("%Y-%m-%d %H:%M:%S")` trong Client 1 |
| Persistence | CSV file trên Server |
