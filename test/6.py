#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019-09-08 15:47
# @Author: yanmiexingkong
# @email : yanmiexingkong@gmail.com
# @File  : 6.py
import asyncio

from pyppeteer import launch

from secure import account, pwd


async def main():
    width, height = 1500, 800
    browser = await launch(headless=False, args=['--disable-infobars', f'--window-size={width},{height}'])
    page = await browser.newPage()
    await page.setViewport({'width': width, 'height': height})
    await page.goto('https://login.taobao.com/member/login.jhtml?redirectURL=https://www.taobao.com/')
    await page.evaluate('() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }')

    await page.type('#TPL_username_1', account)
    await page.type('#TPL_password_1', pwd)
    await page.click('#J_SubmitStatic')

    await asyncio.sleep(20)


asyncio.get_event_loop().run_until_complete(main())
