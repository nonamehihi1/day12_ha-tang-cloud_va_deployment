# Stage 1: Builder
FROM public.ecr.aws/docker/library/python:3.11-slim AS builder

WORKDIR /build

# Cài đặt gcc và các dependencies cần thiết để build (nếu có các package C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Copy requirements và cài đặt vào một thư mục riêng
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM public.ecr.aws/docker/library/python:3.11-slim AS runtime

# Cài đặt curl cho HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Khai báo biến môi trường chuẩn bị cho app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# Copy các thư viện đã được cài đặt từ Stage 1
COPY --from=builder /root/.local /root/.local

# Copy mã nguồn
COPY ./app ./app
COPY ./utils ./utils

# Expose port (sẽ bị override bằng PORT env variable trên cloud)
EXPOSE 8000

# Tạo non-root user
RUN useradd -m -r user
USER user

# Healthcheck instruction
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Chạy ứng dụng bằng uvicorn
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
