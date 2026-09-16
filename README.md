# 🎮 Legion Performance & Game FPS Monitor (v2.5 PRO)

<div align="center">

![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20x64-0078D6?style=for-the-badge&logo=windows)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20Vite%20%2B%20TailwindCSS-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Edge WebView2](https://img.shields.io/badge/Shell-Microsoft%20Edge%20WebView2-0078D7?style=for-the-badge&logo=microsoftedge)
![Hardware](https://img.shields.io/badge/Hardware-Lenovo%20Legion%20%7C%20Ryzen%207%20%7C%20RTX%203060-E2231A?style=for-the-badge&logo=lenovo)

**Ứng dụng đo FPS thời gian thực, trực quan hóa hiệu năng và giám sát phần cứng chuyên sâu đẳng cấp Modern Desktop Application** kết hợp công nghệ **Tauri-Level (React 18 + TailwindCSS + Framer Motion trên Edge WebView2)** và thiết kế **Apple Minimalist Dark Glassmorphism**.

</div>

---

## 🌟 Tính năng nổi bật (Key Features)

### 1. 🖥️ Nền tảng Giao diện Đương Đại (Modern Desktop App)
- **Kiến trúc Tauri-Level**: Giao diện ứng dụng chính được xây dựng bằng **React 18 SPA + Vite**, kết nối qua động cơ **Microsoft Edge WebView2** với khả năng tăng tốc phần cứng GPU (Hardware Accelerated).
- **Thiết kế Apple Dark Glassmorphism**: Hiệu ứng kính mờ `backdrop-blur-xl`, viền phát quang siêu mỏng `border-white/5`, chuyển động mượt mà bằng vật lý lò xo (spring physics) của Framer Motion.
- **Biểu đồ sóng Catmull-Rom Spline**:
  - Thuật toán nội suy đường cong Hermite / Catmull-Rom $C^1$ liên tục, sóng uốn lượn tự nhiên không gấp khúc thô kệch.
  - **Hỗ trợ con lăn chuột (Mouse Wheel Zoom)**: Cuộn chuột trực tiếp trên từng biểu đồ để phóng to/thu nhỏ trục thời gian (từ 1.0x đến 4.0x) để soi chi tiết từng giây biến động; click đúp để đặt lại tỉ lệ chuẩn 1.0x.
  - **Rê chuột soi tọa độ (Hover Crosshair)**: Vạch ngắm thẳng đứng đứt đoạn kèm các huy hiệu (pills) hiển thị chỉ số tức thời tại đúng thời điểm con trỏ đang chỉ.

### 2. 🌀 Trạm Giám Sát Quạt Tản Nhiệt Kép (Dual-Fan Cooling Station)
- **Đọc cảm biến vòng tua quạt phần cứng thực tế**: Truy vấn trực tiếp qua **Direct ACPI WMI Hardware Sensor** trên bo mạch Lenovo Legion mà không làm nghẽn CPU (0% overhead).
- **Cảm biến độc lập 2 quạt**:
  - **Quạt Trái (CPU Fan)**: Giám sát tốc độ vòng tua heatsink của vi xử lý AMD Ryzen 7 5800H.
  - **Quạt Phải (GPU Fan)**: Giám sát tốc độ vòng tua heatsink của card đồ họa NVIDIA GeForce RTX 3060 (TGP 130W).
- **Đồ họa động cơ quạt quay đồng bộ**: Tốc độ quay của cánh quạt trên giao diện mô phỏng chính xác theo RPM thực tế.
- **Ước tính âm học & trạng thái nhiệt**: Thể hiện mức độ ồn decibel (dB) và trạng thái tải lệch bất đối xứng khi chơi game hoặc render.

### 3. 🎯 In-Game Overlay HUD Siêu Linh Hoạt & Độc Lập
- **4 Bố cục hiển thị (Layouts)**:
  1. `Thanh ngang Apple (Horizontal)`: Thanh dài chuẩn Gaming Apple kết hợp biểu đồ dưới (Deck).
  2. `Thanh Mini Pill (Compact)`: Siêu nhỏ gọn dạng viên thuốc nổi trên game.
  3. `Khối góc OSD Card (Corner)`: Hiển thị dạng thẻ đa hàng góc màn hình.
  4. `Thanh dọc Side-Dock (Vertical)`: Dọc sát mép màn hình.
- **Cơ chế Auto-Fit 100%**: Tự động co giãn theo số lượng thông số được chọn, tọa độ neo `(x, y)` được giữ nguyên tuyệt đối khi di chuyển hoặc đổi bố cục.
- **Bộ điều chỉnh Độ trong suốt kép bằng Thanh trượt (Dual Sliders)**:
  - **Slider 1 (Độ trong suốt Nền)**: Từ `0%` (chế độ **Pure HUD** trong suốt hoàn toàn, chỉ có chữ nổi trên game) đến `100%` (nền tối nguyên khối), phản hồi tức thời 0ms.
  - **Slider 2 (Độ trong suốt Chữ & Số liệu)**: Từ `20%` đến `100%`, cho phép làm mờ số liệu để tập trung combat.
  - Tích hợp các nút chọn nhanh (Preset Pills) 1-chạm: Pure HUD, Subtle, Balanced, Deep, Solid.
- **Tùy biến hiển thị thông số 4 nhóm**: Tên trò chơi, FPS, 1% Low, Frametime, CPU (Temp/Usage/Clock), GPU (Temp/Usage/Clock/Watts), RAM, Internet $\downarrow\uparrow$, Cảm biến Quạt.

### 4. 🛡️ Kiến Trúc Hệ Thống Vững Chắc (Enterprise Robustness)
- **Win32 Kernel Named Mutex Guard**: Triệt tiêu 100% hiện tượng mở nhiều cửa sổ hoặc sinh ra icon ma (zombie icons) trong khay hệ thống.
- **Admin Elevation Takeover**: Khi chạy với quyền Administrator, tiến trình Admin tự động tiếp quản, dọn dẹp tiến trình cũ và mở giao diện ngay trong 0ms.
- **Xuyên thấu chuột (Click-Through)**: Bật cờ `WS_EX_TRANSPARENT`, chuột xuyên thẳng vào game 100% không làm gián đoạn combat.
- **Khay hệ thống Windows (System Tray)**: Thu nhỏ êm ái xuống khay icon cạnh đồng hồ, hỗ trợ menu điều khiển nhanh.

---

## ⌨️ Phím tắt toàn cục (Global Hotkeys)

| Phím | Chức năng | Mô tả |
| :---: | :--- | :--- |
| **`F8`** | **Khóa chuột / Xuyên thấu** | Chuột xuyên qua Overlay vào game 100%, không bị vướng khi lia chuột |
| **`F9`** | **Bật / Tắt Overlay HUD** | Ẩn hoặc hiện thanh Overlay tức thì khi đang chơi game |
| **`F10`** | **Đổi nhanh độ trong suốt nền** | Chuyển đổi nhanh 4 mức độ mờ (0% $\rightarrow$ 35% $\rightarrow$ 65% $\rightarrow$ 90% $\rightarrow$ 100%) |
| **Cuộn chuột** | **Thu phóng biểu đồ** | Cuộn con lăn trên biểu đồ để phóng to/thu nhỏ khoảng thời gian theo dõi |
| **Click đúp** | **Đặt lại tỉ lệ chuẩn** | Khôi phục biểu đồ về tỉ lệ 1.0x ban đầu |

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy

### Yêu cầu hệ thống:
- **Hệ điều hành**: Windows 10 / 11 (64-bit)
- **Python**: Phiên bản 3.10 trở lên
- **Phần cứng**: Tối ưu tốt nhất cho laptop Lenovo Legion (AMD Ryzen + NVIDIA GeForce RTX), tương thích với hầu hết PC Windows khác.
- **Runtime**: Microsoft Edge WebView2 Runtime (đã tích hợp sẵn trên Windows 10/11).

### Cài đặt:

1. **Clone repository**:
   ```bash
   git clone https://github.com/Zeus126/legion-fps-monitor.git
   cd legion-fps-monitor
   ```

2. **Cài đặt thư viện Python**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```

3. **Khởi chạy ứng dụng**:
   - **Chế độ Administrator (Khuyên dùng để đọc cảm biến quạt WMI)**:
     - Nhấp đúp vào file [`run_admin.bat`](run_admin.bat)
     - Hoặc chạy shortcut `Legion FPS Monitor (Admin)` trên màn hình Desktop.
   - **Chế độ Thông thường**:
     - Nhấp đúp vào file [`run.bat`](run.bat)

---

## 🛠️ Phát triển & Biên dịch Frontend (Tùy chọn)

Gói ứng dụng đã đi kèm sẵn bản build tĩnh tại `ui/dist`, do đó bạn **không cần cài đặt Node.js** nếu chỉ sử dụng. Nếu muốn tùy biến giao diện React:

```bash
cd ui
npm install
npm run dev      # Chạy live reload dev server trên trình duyệt
npm run build    # Biên dịch bundle tĩnh vào thư mục ui/dist
```

---

## 📂 Cấu trúc dự án

```
legion_fps_monitor/
│── bin/
│   └── PresentMon.exe                # Engine ETW đo FPS/Frametime thời gian thực
│── assets/
│   ├── icon.ico                      # Icon đa phân giải cho Taskbar và Desktop
│   └── icon.png                      # Icon gốc chất lượng cao
│── src/
│   ├── app_modern.py                 # Ứng dụng Desktop Shell chính (WebView2)
│   ├── web_bridge.py                 # Cầu nối IPC hai chiều Python <-> React
│   ├── overlay_window.py             # Cửa sổ In-Game Overlay HUD đa bố cục
│   ├── hw_monitor.py                 # Module đọc phần cứng (NVML, PDH, WMI Fan)
│   ├── fps_tracker.py                # Module thu thập và phân tích PresentMon ETW
│   ├── settings_manager.py           # Quản lý cấu hình JSON người dùng
│   ├── tray_manager.py               # Quản lý khay hệ thống Windows (System Tray)
│   └── hotkey.py                     # Quản lý phím tắt toàn hệ thống (F8, F9, F10)
│── ui/                               # Frontend React 18 + TailwindCSS + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── DashboardTab.jsx      # Tab Tổng quan & Trạm quạt kép
│   │   │   ├── GraphsTab.jsx         # Tab Biểu đồ Catmull-Rom Spline zoom chuột
│   │   │   └── SettingsTab.jsx       # Tab Cài đặt Glassmorphism & Bộ điều khiển
│   │   ├── App.jsx                   # Component gốc ứng dụng
│   │   └── index.css                 # Apple Glassmorphism styling & animations
│   ├── dist/                         # Bundle tĩnh đã biên dịch sẵn
│   └── package.json
│── settings.example.json             # Mẫu file cấu hình chuẩn
│── run.bat                           # File khởi động nhanh chế độ thường
│── run_admin.bat                     # File khởi động tự nâng quyền Administrator
│── run_admin_debug.bat               # File khởi động Admin kèm console debug log
│── requirements.txt                  # Danh sách dependencies Python
│── .gitignore                        # Cấu hình bỏ qua file rác khi đẩy lên Git
└── README.md                         # Tài liệu hướng dẫn sử dụng
```

---

## 📄 Bản quyền (License)

Dự án phát hành dưới giấy phép **MIT License**. Tự do sử dụng, chỉnh sửa và phân phối.
