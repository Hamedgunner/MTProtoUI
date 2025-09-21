#!/bin/bash

# بررسی اجرای اسکریپت با دسترسی روت
if [[ "$EUID" -ne 0 ]]; then
  echo "Please run this script as root"
  exit 1
fi

echo "Welcome to the MTProto Proxy Web UI Installer!"
echo "This script will install Python, Flask, and other dependencies to run the web interface."

# تشخیص توزیع لینوکس
distro=$(awk -F= '/^NAME/{print $2}' /etc/os-release)

# نصب نیازمندی‌های پایه
echo "Installing dependencies..."
if [[ $distro =~ "Ubuntu" ]] || [[ $distro =~ "Debian" ]]; then
  apt-get update
  apt-get install -y python3 python3-pip python3-venv lsof git
elif [[ $distro =~ "CentOS" ]]; then
  yum install -y epel-release
  yum install -y python3 python3-pip lsof git
else
  echo "Unsupported operating system."
  exit 1
fi

# ایجاد یک محیط مجازی برای پایتون
python3 -m venv /opt/mtproxy-webui
source /opt/mtproxy-webui/bin/activate

# نصب کتابخانه‌های پایتون
pip install Flask flask-login waitress

# غیرفعال کردن محیط مجازی
deactivate

# تولید پورت و رمز عبور تصادفی
WEBUI_PORT=$((RANDOM % 55535 + 10000))
while lsof -Pi :$WEBUI_PORT -sTCP:LISTEN -t >/dev/null; do
  WEBUI_PORT=$((RANDOM % 55535 + 10000))
done

WEBUI_PASSWORD=$(hexdump -vn "8" -e ' /1 "%02x"' /dev/urandom)

# ایجاد فایل سرویس systemd برای رابط کاربری
echo "Creating systemd service for the web UI..."
cat > /etc/systemd/system/mtproxy-webui.service << EOL
[Unit]
Description=MTProto Proxy Web UI
After=network.target

[Service]
User=root
WorkingDirectory=$(pwd)
ExecStart=/opt/mtproxy-webui/bin/waitress-serve --host 0.0.0.0 --port ${WEBUI_PORT} web_app:app
Restart=always
Environment="FLASK_APP=web_app.py"
Environment="MTPROXY_PASSWORD=${WEBUI_PASSWORD}"

[Install]
WantedBy=multi-user.target
EOL

# فعال‌سازی و راه‌اندازی سرویس
systemctl daemon-reload
systemctl enable mtproxy-webui.service
systemctl start mtproxy-webui.service

# نمایش اطلاعات دسترسی
clear
echo "================================================================"
echo "MTProto Proxy Web UI has been installed successfully!"
echo ""
echo "You can now access the web interface at:"
PUBLIC_IP=$(curl -s https://api.ipify.org || echo "YOUR_SERVER_IP")
echo "URL:          http://${PUBLIC_IP}:${WEBUI_PORT}"
echo "Password:     ${WEBUI_PASSWORD}"
echo ""
echo "Please save this password securely. It is required to log in."
echo "================================================================"
