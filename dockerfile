# Sử dụng hình ảnh Python chính thức làm cơ sở
FROM python:3.11-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements.txt vào container
COPY requirements.txt .

# Cài đặt các phụ thuộc
RUN pip install --no-cache-dir --default-timeout=100 --retries=10 -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Tải và lưu mô hình embedding trong quá trình build
RUN python install_embedding_model.py

# Chỉ định lệnh mặc định để chạy ứng dụng
CMD ["python", "run.py"]
