#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019-09-08 10:33
# @Author: yanmiexingkong
# @email : yanmiexingkong@gmail.com
# @File  : spider_selenium.py
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from secure import account, pwd


def login():
    driver = webdriver.Chrome()
    driver.get(
        'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d97ksBOi&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F')
    wait = WebDriverWait(driver, 10)
    try:
        name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#TPL_username_1')))
        password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#TPL_password_1")))
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_SubmitStatic")))
        name.send_keys(account)
        password.send_keys(pwd)

        submit.click()
        time.sleep(100)
    finally:
        driver.quit()
    pass


def search():
    driver = webdriver.Chrome()
    driver.get('https://www.taobao.com')
    wait = WebDriverWait(driver, 10)
    try:
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_TSearchForm > div.search-button > button")))
        input.send_keys('美食')
        submit.click()
        time.sleep(5)
    finally:
        driver.quit()


def main():
    login()
    # search()


if __name__ == '__main__':
    main()
