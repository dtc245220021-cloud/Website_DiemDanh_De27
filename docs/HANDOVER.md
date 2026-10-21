# Bàn giao Đề 27

Project: D:\Job_2026_ICTU\Job 3\Project
Báo cáo: D:\Job_2026_ICTU\Job 3\Báo cáo\Bao_cao_De27_Chu_The_Manh_DTC245220021.docx
Repository: https://github.com/dtc245220021-cloud/Website_DiemDanh_De27

| Thành phần | URL | Tài khoản / biến mật khẩu trong .env |
|---|---|---|
| Website | http://127.0.0.1:8080 | admin@attendance.local / ADMIN_PASSWORD |
| Nhân viên | http://127.0.0.1:8080 | nv02@attendance.local đến nv05@attendance.local / EMPLOYEE_PASSWORD |
| phpMyAdmin | http://127.0.0.1:8180 | attendance_app / DB_PASSWORD |
| Prometheus | http://127.0.0.1:9090/targets | localhost, không đăng nhập |
| Grafana | http://127.0.0.1:3001/d/attendance-overview | admin / GRAFANA_PASSWORD |
| Loki readiness | http://127.0.0.1:3100/ready | localhost, không đăng nhập |

Secrets chỉ ở .env và secrets/exporter.cnf trên máy, không Git hoặc báo cáo. Không mở file secrets khi trình chiếu.

Kiểm chứng: 27 integration checks không mock; 2 unit tests; npm audit 0; 4 targets UP, 8 metrics có dữ liệu; bộ đếm tăng khi tạo tải; 3 LogQL có kết quả; quyền UID/network/ports/grants/headers; backup phục hồi schema riêng với 3 checksum khớp. Ảnh thật và JSON tại docs/evidence. Báo cáo được cập nhật TOC bằng Word và render kiểm tra từng trang.

Trước demo: Docker Desktop chạy Linux containers; chạy `python scripts/compose.py 3 up -d --build`, đợi healthy. Nhân viên nv01 đã được dùng thử cả ba ca hôm nay; dùng nv02 đến nv05 hoặc ca mới để demo, không xóa lịch sử. Tạo request404 và login sai để có log mới; chọn Last1hour trong Explore. Query trong docs/logql.md. Có thể chạy scripts/verify_runtime.py để cập nhật dữ liệu mới; bản báo cáo giữ snapshot thời điểm nghiệm thu.

Giới hạn: HTTP localhost + security headers, chưa TLS; Promtail EOL vẫn dùng theo đề; cAdvisor privileged; phpMyAdmin/Promtail có ngoại lệ root; chưa log rotation file app/Nginx, chưa tải dài/CVE toàn image, chưa HA/ca qua đêm/tính lương. Không dùng down -v, không reset DB. Backup nằm ngoài Git, restore schema riêng được giữ để đối chiếu.
