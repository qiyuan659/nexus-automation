#!/usr/bin/env python3

import os
import subprocess
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as wire_webdriver
from web3 import Web3
import requests
from pathlib import Path
import shutil
import random
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 配置
PROJECT_NAME = "nexus_automation"
VIRTUAL_ENV_NAME = "nexus_venv"
NEXUS_LOGIN_URL = "https://app.nexus.xyz"
COUNTER_URL = "https://counter.nexus.xyz"
REMIX_URL = "https://remix.ethereum.org"
NEXUS_EXPLORER_URL = "https://explorer.nexus.xyz"
COUNTER_REPO_URL = "https://github.com/nexus-xyz/nexus-counter-app.git"

NEXUS_CHAIN_ID = 392
NEXUS_RPC_HTTP = "https://rpc.nexus.xyz/http"
NEXUS_NATIVE_TOKEN = "$NEX"

PRIVATE_KEYS = os.getenv("PRIVATE_KEYS", "").split(",")
PROXY_LIST = os.getenv("PROXY_LIST", "").split(",")

CONTRACTS_DIR = Path("contracts")
CONTRACTS_DIR.mkdir(exist_ok=True)

def random_delay(min_seconds=180, max_seconds=300):
    delay = random.uniform(min_seconds, max_seconds)
    logger.info(f"等待 {delay:.2f} 秒...")
    time.sleep(delay)

def setup_driver_with_proxy(proxy_str):
    proxy = parse_proxy(proxy_str)
    proxy_options = {
        'proxy': {
            'http': f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}",
            'https': f"http://{proxy['username']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}",
            'no_proxy': 'localhost,127.0.0.1'
        }
    }
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/google-chrome"
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = wire_webdriver.Chrome(seleniumwire_options=proxy_options, options=chrome_options)
    return driver

def parse_proxy(proxy_str):
    ip, port, username, password = proxy_str.split(":")
    return {"ip": ip, "port": port, "username": username, "password": password}

def login_with_private_key(private_key):
    w3 = Web3(Web3.HTTPProvider(NEXUS_RPC_HTTP))
    account = w3.eth.account.from_key(private_key)
    wallet_address = account.address
    logger.info(f"使用地址登录: {wallet_address}")
    random_delay()
    return wallet_address, private_key

def submit_transactions_to_counter(driver, wallet_address):
    driver.get(COUNTER_URL)
    time.sleep(random_delay())
    nex_input = driver.find_element(By.XPATH, "//input[@placeholder='Enter $NEX Amount']")
    nex_input.send_keys("0.01")
    submit_tx_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit Transaction')]")
    submit_tx_button.click()
    time.sleep(random_delay())

def deploy_contract_on_remix(driver, contract_path, private_key):
    driver.get(REMIX_URL)
    time.sleep(random_delay())
    file_input = driver.find_element(By.XPATH, "//input[@placeholder='File Name']")
    file_name = contract_path.name
    file_input.send_keys(str(file_name))
    time.sleep(random_delay())
    if contract_path.exists():
        contract_code = contract_path.read_text()
    else:
        counter_repo_path = Path("nexus-counter-app/contracts/Counter.sol")
        if counter_repo_path.exists():
            contract_code = counter_repo_path.read_text()
        else:
            contract_code = requests.get("https://raw.githubusercontent.com/nexus-xyz/nexus-counter-app/main/contracts/Counter.sol").text
    code_editor = driver.find_element(By.XPATH, "//div[@class='code-editor']")
    code_editor.send_keys(contract_code)
    time.sleep(random_delay())
    compile_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Compile')]")
    compile_button.click()
    time.sleep(random_delay(180, 300))
    deploy_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Deploy')]")
    deploy_button.click()
    time.sleep(random_delay(180, 300))
    contract_address = driver.find_element(By.XPATH, "//div[contains(text(), 'Contract Address')]").text.split(":")[1].strip()
    logger.info(f"部署合约 {file_name}，地址: {contract_address}")
    time.sleep(random_delay())
    return contract_address

def verify_contract_on_nexus_explorer(driver, contract_address, contract_path):
    verification_url = f"{NEXUS_EXPLORER_URL}/address/{contract_address}/contract-verification"
    driver.get(verification_url)
    logger.info(f"访问验证页面: {verification_url}")
    random_delay()
    try:
        contract_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Contract')]")
        contract_button.click()
        logger.info("已点击 'Contract' 按钮")
    except Exception as e:
        logger.warning(f"未找到 'Contract' 按钮，可能是页面已打开合约视图: {e}")
    time.sleep(random_delay())
    try:
        verify_publish_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Verify & Publish')]")
        verify_publish_button.click()
        logger.info("已点击 'Verify & Publish' 按钮")
    except Exception as e:
        logger.error(f"未找到 'Verify & Publish' 按钮: {e}")
        return
    time.sleep(random_delay())
    code_input = driver.find_element(By.XPATH, "//textarea[@name='contractSourceCode']")
    code_input.send_keys(contract_path.read_text())
    logger.info("已填写合约代码")
    time.sleep(random_delay())
    compiler_version = driver.find_element(By.XPATH, "//select[@name='compilerVersion']")
    compiler_version.send_keys("v0.8.0+commit.c7dfd78e")
    logger.info("已选择编译器版本")
    time.sleep(random_delay())
    optimization_checkbox = driver.find_element(By.XPATH, "//input[@name='optimizationUsed']")
    optimization_checkbox.click()
    runs_input = driver.find_element(By.XPATH, "//input[@name='runs']")
    runs_input.send_keys("200")
    logger.info("已配置优化设置")
    time.sleep(random_delay())
    submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Submit')]")
    submit_button.click()
    logger.info("已提交验证请求")
    time.sleep(random_delay(180, 300))
    logger.info(f"合约 {contract_address} 已验证并发布于 Nexus Explorer")

def batch_deploy_and_verify_contracts():
    for idx, private_key in enumerate(PRIVATE_KEYS):
        proxy_str = random.choice(PROXY_LIST)
        driver = setup_driver_with_proxy(proxy_str)
        try:
            wallet_address, _ = login_with_private_key(private_key)
            submit_transactions_to_counter(driver, wallet_address)
            if idx == 0:
                clone_and_setup_counter_app()
            contract_files = list(CONTRACTS_DIR.glob("*.sol"))
            if not contract_files:
                logger.warning(f"未找到合约文件，使用默认 Counter.sol")
                default_contract = CONTRACTS_DIR / "Counter.sol"
                default_contract.write_text(
                    "pragma solidity ^0.8.0;\ncontract Counter { uint public count; function increment() public { count += 1; } }"
                )
                contract_files = [default_contract]
            for contract_path in contract_files:
                contract_address = deploy_contract_on_remix(driver, contract_path, private_key)
                verify_contract_on_nexus_explorer(driver, contract_address, contract_path)
                time.sleep(random_delay())
        except Exception as e:
            logger.error(f"私钥 {private_key} 处理失败: {e}")
        finally:
            driver.quit()
            time.sleep(random_delay())

def clone_and_setup_counter_app():
    counter_dir = Path("nexus-counter-app")
    if not counter_dir.exists():
        subprocess.run(["git", "clone", COUNTER_REPO_URL, str(counter_dir)], check=True)
    os.chdir(counter_dir)
    subprocess.run(["yarn", "install"], check=True)
    subprocess.run(["yarn", "start"], check=True)
    os.chdir("..")
    time.sleep(random_delay())

def cleanup():
    if os.path.exists(VIRTUAL_ENV_NAME):
        shutil.rmtree(VIRTUAL_ENV_NAME)
    if os.path.exists("nexus-counter-app"):
        shutil.rmtree("nexus-counter-app")
    logger.info("清理完成")

def main():
    try:
        logger.info("开始执行 Nexus Automation...")
        batch_deploy_and_verify_contracts()
    except Exception as e:
        logger.error(f"主程序错误: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()
