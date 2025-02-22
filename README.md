# Nexus Automation

这是一个自动化 Nexus 区块链交互的脚本，适用于 Oracle Cloud VM.Standard.A1.Flex (Ubuntu 24.04, Arm64)。

## 前提条件
- Oracle Cloud VM.Standard.A1.Flex 实例，运行 Ubuntu 24.04。
- 已配置公网访问（防火墙允许出站流量）。

## 安装和运行
1. 克隆仓库：
   ```bash
   git clone https://github.com/qiyuan659/nexus-automation.git
   cd nexus-automation

   配置环境变量：创建 .env 文件并添加：
PRIVATE_KEYS=your_private_key_1,your_private_key_2
PROXY_LIST=192.168.1.1:8080:user1:pass1,192.168.1.2:8081:user2:pass2
赋予执行权限并运行：
bash
chmod +x install_and_run.sh
./install_and_run.sh
注意事项
请替换 .env 中的私钥和代理为实际值。
确保网络连接稳定，避免超时。
许可证
MIT

---


注意事项
以上所有文件都应放置在 GitHub 仓库的根目录（/nexus-automation/）。
.env 文件是本地配置，不应上传到 GitHub（已在 .gitignore 中忽略），用户需手动创建。
