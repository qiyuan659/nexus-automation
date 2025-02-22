#!/bin/bash
set -e
echo "开始设置环境..."
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git curl npm unzip
sudo npm install -g yarn
yarn --version
echo "安装 Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_arm64.deb
sudo apt install -y ./google-chrome-stable_current_arm64.deb
rm google-chrome-stable_current_arm64.deb
google-chrome --version
echo "安装 ChromeDriver..."
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1)
DRIVER_URL="https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}"
LATEST_DRIVER=$(curl -s $DRIVER_URL)
wget -q "https://chromedriver.storage.googleapis.com/${LATEST_DRIVER}/chromedriver_linux64.zip"
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
rm chromedriver_linux64.zip
chromedriver --version
echo "配置 Python 虚拟环境..."
python3 -m venv nexus_venv
source nexus_venv/bin/activate
pip install -r requirements.txt
echo "运行 Nexus Automation 脚本..."
python3 nexus_automation.py
deactivate
echo "脚本执行完成！"
