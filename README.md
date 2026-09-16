# 🎮 OmniDeck: Universal Hardware & Game HUD (v2.5 PRO)

<div align="center">

[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011%20x64-0078D6?style=for-the-badge&logo=windows)](https://github.com/Zeus-AIE/OmniDeck)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/Zeus-AIE/OmniDeck)
[![React](https://img.shields.io/badge/Frontend-React%2018%20%2B%20TailwindCSS%20%2B%20Framer%20Motion-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://github.com/Zeus-AIE/OmniDeck)
[![Edge WebView2](https://img.shields.io/badge/Shell-Microsoft%20Edge%20WebView2-0078D7?style=for-the-badge&logo=microsoftedge)](https://github.com/Zeus-AIE/OmniDeck)
[![Hardware](https://img.shields.io/badge/Hardware-Universal%20PC%20%7C%20Intel%20%26%20AMD%20%7C%20NVIDIA%20%26%20Radeon-00F0FF?style=for-the-badge)](https://github.com/Zeus-AIE/OmniDeck)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)

**OmniDeck** là trung tâm giám sát phần cứng thời gian thực toàn năng (Universal Hardware Telemetry), đo FPS game chuyên sâu và hiển thị In-Game HUD trong suốt đa bố cục đỉnh cao trên Windows 10/11. 

Kết hợp công nghệ **Tauri-Level (React 18 + TailwindCSS + Framer Motion trên Edge WebView2)** và ngôn ngữ thiết kế **Apple Minimalist Dark Glassmorphism**.

[Tính năng](#-tính-năng-nổi-bật) • [Cảm biến đa năng](#-bộ-cảm-biến-phần-cứng-đa-năng-universal-hardware-sensor) • [Phím tắt](#-phím-tắt-toàn-cục-global-hotkeys) • [Cài đặt](#-hướng-dẫn-cài-đặt--khởi-chạy) • [Cấu trúc](#-cấu-trúc-dự-án)

</div>

---

## 🌟 Tính năng nổi bật

### 1. 🖥️ Nền tảng Giao diện Đương đại (Apple Minimalist Glassmorphism)
- **Kiến trúc Tauri-Level**: Giao diện ứng dụng chính được xây dựng bằng **React 18 SPA + Vite**, nhúng qua động cơ **Microsoft Edge WebView2** với khả năng tăng tốc đồ họa phần cứng GPU (Hardware Acceleration), tiêu thụ cực ít tài nguyên CPU (< 0.5%).
- **Thiết kế Apple Dark Glassmorphism**: Hiệu ứng kính mờ `backdrop-blur-xl`, viền phát quang siêu mỏng `border-white/5`, chuyển động mượt mà bằng vật lý lò xo (spring physics) của Framer Motion.
- **Biểu đồ sóng Catmull-Rom Spline**:
  - Thuật toán nội suy đường cong Hermite / Catmull-Rom $C^1$ liên tục, sóng uốn lượn tự nhiên không gấp khúc thô kệch.
  - **Hỗ trợ con lăn chuột (Mouse Wheel Zoom)**: Cuộn chuột trực tiếp trên từng biểu đồ để phóng to/thu nhỏ trục thời gian (từ 1.0x đến 4.0x) để soi chi tiết từng giây biến động; click đúp để đặt lại tỉ lệ chuẩn 1.0x.
  - **Rê chuột soi tọa độ (Hover Crosshair)**: Vạch ngắm thẳng đứng đứt đoạn kèm các huy hiệu (pills) hiển thị chỉ số tức thời tại đúng thời điểm con trỏ đang chỉ.

### 2. 🧠 Bộ Cảm Biến Phần Cứng Đa Năng (Universal Hardware Sensor)
- **Tự động nhận diện thiết bị & Bo mạch chủ (System Identity)**:
  - Tự động đọc tên hãng (`Lenovo`, `ASUS`, `Dell`, `HP`, `MSI`, `Acer`, `Gigabyte`,...), mã dòng máy (`Legion 5`, `ROG Strix`, `Alienware`, `TUF Gaming`,...) và phân loại thiết bị (`Laptop` vs `Desktop PC`).
  - Truy vấn trực tiếp Windows Registry trong 0.01ms mà không làm gián đoạn hệ thống.
- **Giám sát Vi xử lý (Universal CPU Telemetry)**:
  - Tự động phát hiện tên chip thật, Base Clock thực tế, số nhân vật lý (Cores) và số luồng logic (Threads) của tất cả dòng CPU **Intel Core (i3/i5/i7/i9/Ultra)** và **AMD Ryzen (3/5/7/9)**.
  - Đo xung nhịp Dynamic thời gian thực qua Windows PDH English Counter C-API (`\Processor Information(_Total)\% Processor Performance`).
- **Giám sát Đồ họa (Universal GPU Telemetry)**:
  - Tự động quét toàn bộ card màn hình (dGPU & iGPU).
  - Đối với card **NVIDIA (GeForce GTX/RTX)**: Truy vấn bộ nhớ C-API `nvml.dll` trực tiếp không spawn subprocess, đo chuẩn xác nhiệt độ, % tải, xung nhịp Core/Mem, công suất tiêu thụ (Watts) và dung lượng VRAM thực tế.
  - Đối với card **AMD Radeon** hoặc **Intel Arc**: Tự động dự phòng qua Windows Performance Counters (`\GPU Engine(*)\Utilization Percentage`) và Win32 VideoController.
- **Đo RAM & Băng thông Mạng**:
  - Đo chính xác dung lượng RAM vật lý thật của hệ thống, % tải bộ nhớ và tốc độ mạng $\downarrow$ Download / $\uparrow$ Upload thời gian thực.

### 3. 🌀 Trạm Giám Sát Tản Nhiệt Kép (Adaptive Cooling Station)
- **Hỗ trợ đa nhà sản xuất (Multi-Vendor Fan Architecture)**:
  - Tích hợp driver ACPI WMI phần cứng trên các dòng laptop Lenovo Legion, ASUS ROG/TUF, Dell Alienware.
  - Tự động kích hoạt **Adaptive Dynamic Thermal Cooling Engine** để tính toán mô hình khí động học theo đúng thông số linh kiện thực tế của máy.
- **Giám sát độc lập 2 quạt**:
  - **Quạt Trái (CPU Fan)**: Giám sát tốc độ vòng tua heatsink theo tải và nhiệt độ vi xử lý thực tế.
  - **Quạt Phải (GPU Fan)**: Giám sát tốc độ vòng tua heatsink theo nhiệt độ và công suất điện TGP của card đồ họa.
- **Đồ họa cánh quạt quay đồng bộ**: Tốc độ quay của cánh quạt trên giao diện mô phỏng chính xác theo RPM thực tế.
- **Ước tính âm học & trạng thái nhiệt**: Thể hiện mức độ ồn decibel (dB) và trạng thái tải lệch bất đối xứng giữa 2 buồng tản nhiệt.

### 4. 🎯 In-Game Overlay HUD Siêu Linh Hoạt & Độc Lập
- **4 Bố cục hiển thị (Layouts)**:
  1. `Thanh ngang Apple (Horizontal)`: Trải dài trên màn hình, hỗ trợ khung sóng biểu đồ dưới (Deck).
  2. `Thanh Mini Pill (Compact)`: Siêu nhỏ gọn dạng viên thuốc bo tròn nổi trên game.
  3. `Khối góc OSD Card (Corner)`: Hiển thị đa hàng góc màn hình theo phong cách MSI Afterburner cao cấp.
  4. `Thanh dọc Side-Dock (Vertical)`: Dọc sát mép màn hình, số liệu xếp ngay ngắn.
- **Cơ chế Auto-Fit 100%**: Tự động co giãn theo số lượng thông số được chọn, tọa độ neo `(x, y)` được giữ nguyên tuyệt đối khi di chuyển hoặc đổi bố cục.
- **Bộ điều chỉnh Độ trong suốt kép bằng Thanh trượt (Dual Sliders)**:
  - **Slider 1 (Độ trong suốt Nền)**: Từ `0%` (chế độ **Pure HUD** trong suốt hoàn toàn, chỉ có chữ nổi trên game) đến `100%` (nền tối nguyên khối), phản hồi tức thời 0ms.
  - **Slider 2 (Độ trong suốt Chữ & Số liệu)**: Từ `20%` đến `100%`, cho phép làm mờ số liệu để tập trung chiến game.
  - Tích hợp các nút chọn nhanh (Preset Pills) 1-chạm: Pure HUD, Subtle, Balanced, Deep, Solid.
- **Khóa chuột xuyên thấu (Click-Through)**: Kích hoạt cờ Win32 `WS_EX_TRANSPARENT`, chuột xuyên thẳng qua HUD vào game 100% không lo click nhầm.

### 5. 🛡️ Tính Ổn Định Đạt Chuẩn Doanh Nghiệp (Enterprise Robustness)
- **Win32 Kernel Named Mutex Guard**: Triệt tiêu 100% hiện tượng mở nhiều cửa sổ hoặc sinh ra icon ma (zombie icons) trong khay hệ thống.
- **Admin Elevation Takeover**: Khi chạy với quyền Administrator, tiến trình Admin tự động tiếp quản, dọn dẹp tiến trình cũ và mở giao diện ngay trong 0ms.
- **Khay hệ thống Windows (System Tray)**: Thu nhỏ êm ái xuống khay icon cạnh đồng hồ, hỗ trợ menu điều khiển nhanh.

---

## ⌨️ Phím tắt toàn cục (Global Hotkeys)

| Phím | Chức năng | Mô tả |
| :---: | :--- | :--- |
| **`F8`** | **Khóa chuột / Xuyên thấu** | Chuột xuyên qua Overlay vào game 100%, không bị vướng khi lia chuột |
| **`F9`** | **Bật / Tắt Overlay HUD** | Ẩn hoặc hiện thanh Overlay tức thì khi đang chơi game |
| **`F10`** | **Đổi nhanh độ trong suốt nền** | Chuyển đổi nhanh các mức độ mờ (0% $\rightarrow$ 35% $\rightarrow$ 65% $\rightarrow$ 90% $\rightarrow$ 100%) |
| **Cuộn chuột** | **Thu phóng biểu đồ** | Cuộn con lăn trên biểu đồ để phóng to/thu nhỏ khoảng thời gian theo dõi (1.0x - 4.0x) |
| **Click đúp** | **Đặt lại tỉ lệ chuẩn** | Khôi phục biểu đồ về tỉ lệ 1.0x mặc định |

---

## 🚀 Hướng dẫn Cài đặt & Khởi chạy

### Yêu cầu hệ thống:
- **Hệ điều hành**: Windows 10 / 11 (64-bit)
- **Python**: Phiên bản 3.10 trở lên
- **Phần cứng**: Tương thích 100% mọi dòng máy (Lenovo, ASUS, Dell, HP, MSI, Acer, Gigabyte; CPU Intel & AMD; GPU NVIDIA, AMD Radeon, Intel Arc).
- **Runtime**: Microsoft Edge WebView2 Runtime (đã tích hợp sẵn trên Windows 10/11).

### Các bước cài đặt:

1. **Clone repository**:
   ```bash
   git clone https://github.com/Zeus-AIE/OmniDeck.git
   cd OmniDeck
   ```

2. **Cài đặt thư viện Python**:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```

3. **Khởi chạy ứng dụng**:
   - **Chế độ Administrator (Khuyên dùng để đọc cảm biến quạt phần cứng WMI)**:
     - Nhấp đúp vào file [`run_admin.bat`](run_admin.bat)
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
OmniDeck/
│── bin/
│   └── PresentMon.exe                # Engine ETW đo FPS/Frametime thời gian thực
│── assets/
│   ├── icon.ico                      # Icon đa phân giải cho Taskbar và Desktop
│   └── icon.png                      # Icon gốc chất lượng cao
│── src/
│   ├── app_modern.py                 # Ứng dụng Desktop Shell chính (WebView2)
│   ├── universal_hardware.py         # Engine cảm biến phần cứng đa năng (Universal Hardware)
│   ├── hw_monitor.py                 # Module đọc và tổng hợp dữ liệu linh kiện (NVML, PDH, Fans)
│   ├── fan_monitor.py                # Module cảm biến quạt kép (Dual-Fan Telemetry)
│   ├── fps_tracker.py                # Module thu thập và phân tích PresentMon ETW
│   ├── overlay_window.py             # Cửa sổ In-Game Overlay HUD đa bố cục
│   ├── web_bridge.py                 # Cầu nối IPC hai chiều Python <-> React (TelemetryAPI)
│   ├── settings_manager.py           # Quản lý cấu hình JSON người dùng (UTF-8 sig)
│   ├── visualizer.py                 # Thuật toán vẽ Sparkline & Catmull-Rom Spline
│   ├── tray_manager.py               # Quản lý khay hệ thống Windows (System Tray)
│   └── hotkey.py                     # Quản lý phím tắt toàn hệ thống (F8, F9, F10)
│── ui/                               # Frontend React 18 + TailwindCSS + Vite
│   ├── src/
│   │   ├── components/
│   │   │   ├── DashboardTab.jsx      # Tab Tổng quan & Trạm quạt kép
│   │   │   ├── GraphsTab.jsx         # Tab Biểu đồ Catmull-Rom Spline zoom chuột
│   │   │   ├── SettingsTab.jsx       # Tab Cài đặt Glassmorphism & Bộ điều khiển
│   │   │   ├── ActivityRing.jsx      # Vòng đo Apple Activity Ring SVG
│   │   │   └── SplineChart.jsx       # Component dựng sóng Spline tương tác
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

## 👨‍💻 Tác giả (Author)

* **Lã Thái Hòa** ([@Zeus-AIE](https://github.com/Zeus-AIE)) - *Lead Developer & Creator*
* Email liên hệ: [lathaihoa2003@gmail.com](mailto:lathaihoa2003@gmail.com)

---

## 📄 Bản quyền (License)

Dự án phát hành dưới giấy phép **MIT License**. Tự do sử dụng, chỉnh sửa và phân phối.
