# LogQL chạy trên dữ liệu thật

Trong Grafana Explore, chọn datasource Loki, khoảng thời gian Last 1 hour.

1. Truy cập web: `{project="attendance27",job="nginx"} | json`
2. HTTP lỗi: `{project="attendance27",job="nginx"} | json | status >= 400`
3. Đăng nhập và nghiệp vụ: `{project="attendance27",job="app"} | json | event =~ "login_.*|check_in|check_out"`

Tạo sự kiện bằng đăng nhập sai một lần, truy cập `/demo-missing`, đăng nhập đúng và vào/ra ca. Log JSON chỉ lưu path không có query, không ghi mật khẩu, cookie, token. Labels chỉ có project/job/file, không gắn user ID làm label.

Promtail hết hỗ trợ từ 02/03/2026. Giữ đúng công cụ bắt buộc của đề; chỉ demo localhost, cần chuyển Alloy khi vận hành lâu dài. Promtail có UID 0 và capability DAC_READ_SEARCH để đọc hai log volumes, không mount Docker socket. Chỉ log app/Nginx; không tuyên bố đã thu log mọi container. Loki dùng single tenant không xác thực, cổng chỉ bind localhost.
