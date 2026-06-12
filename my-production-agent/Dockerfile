# Stage 1: Builder
FROM public.ecr.aws/docker/library/python:3.11-slim AS builder

WORKDIR /build

# Cài đặt gcc
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Tạo virtual environment và cài package
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM public.ecr.aws/docker/library/python:3.11-slim AS runtime

# Cài đặt curl cho HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Tạo non-root user
RUN useradd -m -r user

WORKDIR /app

# Copy virtual env từ stage 1
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy mã nguồn
COPY ./app ./app
COPY ./utils ./utils

# Phân quyền cho user
RUN chown -R user:user /app

USER user

# Expose port
EXPOSE 8000

# Healthcheck instruction
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://127.0.0.1:${PORT:-8000}/health || exit 1

# Chạy ứng dụng
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
