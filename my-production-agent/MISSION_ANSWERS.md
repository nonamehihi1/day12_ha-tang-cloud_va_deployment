# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. Hardcoded secrets (ví dụ: API keys để dạng plaintext trực tiếp trong file mã nguồn).
2. Hardcoded parameters như Port cố định (thường là 8000 hoặc 5000) không lấy từ biến môi trường.
3. Chạy ứng dụng với Debug Mode được kích hoạt trên môi trường production.
4. Thiếu cơ chế Health Check để orchestration platform (Docker/Kubernetes) biết trạng thái của container.
5. Thiếu Graceful Shutdown, ứng dụng tắt đột ngột gây gián đoạn các request đang được xử lý.

### Exercise 1.3: Comparison table

| Feature | Basic (Develop) | Advanced (Production) | Tại sao quan trọng? |
|---------|-----------------|-----------------------|---------------------|
| Config | Hardcode trực tiếp trong code | Sử dụng Environment variables (`.env`) | Bảo mật secrets, dễ thay đổi cấu hình mà không cần sửa code. |
| Health check | Không có | Có endpoint `/health`, `/ready` | Giúp load balancer và orchestrator biết service có sống và sẵn sàng nhận traffic không. |
| Logging | Dùng `print()` ra console | Sử dụng Structured JSON Logging | Dễ dàng parse, tìm kiếm và monitor trên các hệ thống quản lý log tập trung (ELK, Datadog). |
| Shutdown | Đột ngột (nhấn Ctrl+C là chết ngay) | Graceful Shutdown (Bắt tín hiệu SIGTERM) | Đảm bảo các request và connection hiện tại được xử lý xong trước khi tắt ứng dụng. |

---

## Part 2: Docker Containerization

### Exercise 2.1: Dockerfile questions
1. Base image là gì?: Thường là image nhẹ như `python:3.11-slim` hoặc `python:3.11-alpine`.
2. Working directory là gì?: Thường là `/app`.
3. Tại sao COPY requirements.txt trước?: Để tận dụng Docker cache layer. Việc cài đặt dependencies (chạy `pip install`) thường tốn thời gian. Nếu chỉ thay đổi mã nguồn mà không đổi `requirements.txt`, Docker sẽ dùng lại cache của bước cài đặt.
4. CMD vs ENTRYPOINT khác nhau thế nào?: `ENTRYPOINT` định nghĩa executable mặc định sẽ chạy (thường không bị ghi đè dễ dàng), trong khi `CMD` cung cấp các tham số mặc định cho `ENTRYPOINT` (dễ dàng bị ghi đè khi chạy lệnh `docker run`).

### Exercise 2.3: Image size comparison
- Develop: ~900 MB (sử dụng base image chuẩn đầy đủ tools)
- Production: ~150 MB (sử dụng multi-stage build và `python-slim` base image)
- Difference: ~83% nhỏ hơn, giúp tiết kiệm băng thông khi pull image, giảm diện tấn công bảo mật và tăng tốc độ khởi động.

---

## Part 3: Cloud Deployment

### Exercise 3.1 & 3.2: Railway/Render deployment
- Platform: Railway / Render
- Hiểu cách inject các environment variables từ dashboard vào container. Nền tảng tự động cung cấp `PORT`, do đó mã nguồn cần lấy cổng qua `os.getenv("PORT")`.
- Cấu hình file `railway.toml` hoặc `render.yaml` tự động hóa quá trình IaC (Infrastructure as Code).

---

## Part 4: API Security

### Exercise 4.1: API Key Authentication
- API key được truyền qua HTTP Header (ví dụ: `X-API-Key`).
- Ở production, cần tạo cơ chế rotate key dễ dàng thông qua việc đổi biến môi trường và restart container mà không cần deploy lại code.

### Exercise 4.3: Rate Limiting
- Thuật toán thường dùng: Sliding window hoặc Token bucket.
- Rate limit được lưu state trên Redis (ví dụ: đếm số request trong 1 phút bằng `INCR` và `EXPIRE`).

### Exercise 4.4: Cost guard implementation
- Dựa vào User ID, lưu trữ tổng số tiền (hoặc token) đã sử dụng trong tháng trên Redis với TTL là độ dài của tháng đó (khoảng 31-32 ngày).
- Nếu Request mới khiến tổng số tiền vượt Budget thì trả về lỗi 402 Payment Required.

---

## Part 5: Scaling & Reliability

### Exercise 5.1-5.5: Implementation notes
- **Stateless Design:** Chuyển bộ nhớ cuộc hội thoại (conversation history) từ biến dictionary trong memory sang cấu trúc dữ liệu List của Redis. Đảm bảo mọi container sinh ra đều đọc/ghi vào một Redis tập trung, giúp request gửi đến bất kỳ container nào cũng xử lý được.
- **Load Balancing:** Sử dụng Nginx làm reverse proxy để chia đều lượng traffic đến N instances của ứng dụng (Round-robin). Nginx sẽ route traffic dựa vào cấu hình upstream.
- **Graceful Shutdown:** Bắt sự kiện `signal.SIGTERM` bằng thư viện signal của Python, để thực hiện các cleanup connection (đóng db connection) thay vì tắt ngang lập tức.
