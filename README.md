# Hệ thống Điểm danh nhân viên — Đề 27

Chu Thế Mạnh · DTC245220021 · ATTT K23A. Giảng viên: Nguyễn Anh Chuyên.

Node.js + MySQL + phpMyAdmin; Docker Compose; Nginx reverse proxy và security headers. Quản trị viên quản lý nhân sự/ca làm; nhân viên vào ca, ra ca, xem lịch sử. Dữ liệu minh họa được tạo một lần khi chưa có nhân sự. Mật khẩu lưu bcrypt; session trong MySQL; CSRF và phân quyền phía server.

## Chạy giai đoạn ứng dụng

Yêu cầu Docker Desktop Linux containers, Git và Python 3. Tại thư mục repository:

```powershell
python scripts/setup.py
python scripts/compose.py 1 up -d --build
python scripts/compose.py 1 ps
```

Setup tự chọn cổng localhost còn trống. Xem `.env` trên máy triển khai để lấy cổng và mật khẩu; không chia sẻ file này. Admin `admin@attendance.local` dùng `ADMIN_PASSWORD`; nhân viên `nv01@attendance.local` đến `nv05@attendance.local` dùng `EMPLOYEE_PASSWORD`. phpMyAdmin đăng nhập `attendance_app` / `DB_PASSWORD` (không có quyền DDL). Root chỉ dùng trong terminal để quản trị/backup.

Ứng dụng mặc định http://127.0.0.1:8080; phpMyAdmin http://127.0.0.1:8180. Cổng thực trong `.env` được ưu tiên. Không mở cổng MySQL. HTTP localhost sử dụng security headers thay cho TLS (được đề cho phép); cookie HttpOnly/SameSite=Strict, chưa bật Secure khi dùng HTTP. Chỉ dùng dữ liệu demo, cần HTTPS trước khi đưa lên mạng.

## Bảo toàn dữ liệu

Named volume `mysql_data` lưu database và session. Dùng `stop`/`start` hoặc `restart`, không dùng `down -v`. Không chạy lại setup để đổi mật khẩu của DB đã có. Vô hiệu hóa nhân sự thay xóa vật lý để bảo toàn lịch sử. Ca có lịch sử không thể xóa; ca qua đêm chưa hỗ trợ. Giờ vào/ra lấy từ server MySQL UTC+7; số giờ chưa trừ nghỉ, chưa dùng tính lương.

## Kiểm thử

```powershell
docker compose run --rm --no-deps app npm test
```

Đây là unit tests validation; kiểm tra tích hợp thật và minh chứng được bổ sung trong `docs/evidence`.

## Monitoring (giai đoạn 2)

```powershell
python scripts/compose.py 2 up -d --build
```

Prometheus http://127.0.0.1:9090; Grafana http://127.0.0.1:3001, user `admin`, mật khẩu `GRAFANA_PASSWORD` trong `.env`. Dashboard provision sẵn trong thư mục Attendance. Prometheus scrape chính nó, cAdvisor, Nginx exporter và MySQL exporter mỗi 15 giây. Database exporter dùng tài khoản riêng với SELECT, PROCESS, REPLICATION CLIENT, giới hạn 3 kết nối.

CPU = `100 * rate(container_cpu_usage_seconds_total[2m])`, phần trăm một core (có thể vượt 100% khi dùng nhiều core), không phải phần trăm toàn máy. RAM working set tính bằng bytes, Grafana đổi đơn vị hiển thị; không phải giới hạn RAM. Network là tốc độ bytes/giây. Dashboard lọc `name=~"attendance27-.*"`; cAdvisor vẫn có quyền thấy mọi container trong Docker engine. cAdvisor privileged và mount host chỉ đọc là ngoại lệ bảo mật cần cho metrics, không dùng cấu hình này như mẫu hardening cho app.
