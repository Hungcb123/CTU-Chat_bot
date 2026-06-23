#!/bin/bash

# Đường dẫn tới môi trường ảo của bạn
VENV_PATH="/mnt/d/Project/Chatbot/wsl_venv"

if [ -f "$VENV_PATH/bin/activate" ]; then
    # Khởi tạo một bash session mới, nạp cấu hình mặc định, nạp file .env và kích hoạt venv
    bash --rcfile <(echo "source ~/.bashrc; source $VENV_PATH/bin/activate; set -a; [ -f /mnt/d/Project/Chatbot/.env ] && source /mnt/d/Project/Chatbot/.env; set +a; echo '🚀 Đã kích hoạt môi trường ảo wsl_venv và nạp API Key thành công!'")
else
    echo "❌ Lỗi: Không tìm thấy môi trường ảo tại $VENV_PATH"
fi
