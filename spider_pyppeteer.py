#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019-09-08 19:04
# @Author: PythonVampire
# @email : vampire@ivamp.cn
# @File  : spider_pyppeteer.py
import asyncio
import random
import re
import time

import pyppeteer
import pymongo
from pyppeteer.errors import NetworkError
from pyquery import PyQuery as pq
from retrying import retry

from config import taobao_login_url, KEYWORD
from secure import MONGO_URL, MONGO_TABLE, account, pwd

client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_TABLE]


def input_time_random():
    return random.randint(100, 151)


def retry_if_result_none(result):
    return result is None


@retry(retry_on_result=retry_if_result_none, )
async def mouse_slide(page=None):
    await asyncio.sleep(1)
    try:
        # 鼠标移动到滑块，按下，滑动到头（然后延时处理），松开按键
        await page.hover('#nc_1_n1z')  # 不同场景的验证码模块能名字不同。
        await page.mouse.down()
        await page.mouse.move(2000, 0, {'delay': random.randint(1000, 2000)})
        await page.mouse.up()
    except Exception as e:
        print(e, ':验证失败')
        return None, page
    else:
        await asyncio.sleep(1)
        # 判断是否通过
        slider_again = await page.Jeval('.nc-lang-cnt', 'node => node.textContent')
        if slider_again != '验证通过':
            return None, page
        else:
            print('验证通过')
            return 1, page


async def get_cookie(page):
    """
    获取登录后cookie
    :param page:page
    :return:cookies
    """
    # res = await page.content()
    cookies_list = await page.cookies()
    # print(cookies_list)
    cookies = ''
    for cookie in cookies_list:
        str_cookie = '{0}={1};'.format(cookie.get('name'), cookie.get('value'))
        cookies += str_cookie
    # print(cookies)
    return cookies


async def search(page):
    try:
        await page.type('#q', KEYWORD)

        # 点击的3种方法
        await page.click('#J_TSearchForm > div.search-button > button')  # pyppeteer 原生点击
        # await page.keyboard.press('Enter')    # 按 enter 键
        # await page.evaluate('''document.querySelector("#J_TSearchForm > div.search-button > button").click()''')
        time.sleep(1)

        await page.waitForSelector('#mainsrp-pager > div > div > div > div.total')  # 等待 total 加载出来
        await page.waitForSelector('#mainsrp-pager > div > div > div > div.form > input')  # 等待输入框加载出来
        await page.waitForSelector('#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')  # 等待确定按钮加载出来

        page_source = await page.content()
        total = int(re.findall('共 (\d+) 页', page_source)[0])  # 获取总页数
        print(total, type(total))
        return total
    except NetworkError as e:
        await search(page)


async def scroll_page(page):
    cur_dist = 0
    height = await page.evaluate("() => document.body.scrollHeight")
    while True:
        if cur_dist < height:
            await page.evaluate("window.scrollBy(0, 500);")
            await asyncio.sleep(0.3)
            cur_dist += 500
        else:
            break


async def screenshot(page, page_number):
    print('开始截图')
    img_path = './image/{}.png'.format(page_number)
    await page.screenshot(path=img_path, fullPage=True, type='png')
    print('截图完成')


async def validate_current_page(page, page_number):
    print('开始验证当前页码')
    await page.waitForSelector('#mainsrp-pager > div > div > div > ul > li.item.active')  # 确保当前高亮页码已经加载
    current_page = await page.evaluate('''document.querySelector('.item.active > span').innerText''')  # 获取当前页码
    if current_page == str(page_number):
        print('当前页码验证成功。。。')
    else:
        print('当前页码错误！！！')
        raise


async def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('保存到 MONGODB 成功。。。')
        else:
            print('保存到 MONGODB 失败！！！')
            print(result)
    except Exception:
        print('保存到 MONGODB 失败！！！')
        print(result)


async def get_product(page):
    html = await page.content()
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'image': item.find('.pic .img').attr('src'),
            'price': item.find('.price').text(),
            'deal': item.find('.deal-cnt').text()[:-3],
            'title': item.find('.title').text(),
            'shop': item.find('.shop').text(),
            'location': item.find('.location').text()
        }
        await save_to_mongo(product)
        # yield product


async def next_page(page, page_number):
    print('执行 next_page')
    try:
        await scroll_page(page)
        await get_product(page)
        # await save_to_mongo(product)

        print('等待输入框加载出来')
        await page.waitForSelector('#mainsrp-pager > div > div > div > div.form > input')  # 等待输入框加载出来
        print('输入框已加载')

        print('等待确定按钮加载出来')
        await page.waitForSelector('#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')  # 等待确定按钮加载出来
        print('确定按钮已加载')

        print('输入' + str(page_number))
        await page.evaluate('''document.getElementsByClassName('J_Input')[0].value={}'''.format(page_number))

        time.sleep(1)
        print('点击确定')
        await page.evaluate('''document.getElementsByClassName('J_Submit')[0].click()''')
        time.sleep(1)

        await validate_current_page(page, page_number)
        await screenshot(page, page_number)

    except NetworkError as e:
        # await next_page(page, page_number)
        print('出现了异常：')
        print(e)
        time.sleep(10)


async def launch_browser():
    width, height = 1500, 1500
    browser = await pyppeteer.launch(
        {'headless': False, 'args': ['--no-sandbox', f'--window-size={width},{height}', '--disable-dev-shm-usage'], })
    page = await browser.newPage()
    # await page.setRequestInterception(True)
    await page.setViewport({'width': width, 'height': height})
    await page.setUserAgent(
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36')
    return browser, page


async def main(account, pwd, url):
    browser, page = await launch_browser()

    await page.goto(url)  # 访问登录页面
    await page.evaluate(
        '''() =>{ Object.defineProperties(navigator,{ webdriver:{ get: () => false } }) }''')
    await page.evaluate('''() =>{ window.navigator.chrome = { runtime: {},  }; }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] }); }''')
    await page.evaluate('''() =>{ Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], }); }''')
    await page.click('#J_QRCodeLogin > div.login-links > a.forget-pwd.J_Quick2Static')

    await page.type('.J_UserName', account, {'delay': input_time_random() - 50})
    await page.type('#J_StandardPwd input', pwd, {'delay': input_time_random()})

    slider = await page.Jeval('#nocaptcha', 'node => node.style')  # 检查是否有滑块

    if slider:
        print('当前页面出现滑块')
        flag, page = await mouse_slide(page=page)  # js拉动滑块过去。
        if flag:
            await page.keyboard.press('Enter')  # 确保内容输入完毕，少数页面会自动完成按钮点击
            print("print enter", flag)

            # 如果无法通过回车键完成点击，就调用js模拟点击登录按钮。
            await page.evaluate('''document.getElementById("J_SubmitStatic").click()''')

            time.sleep(1)
            # cookies_list = await page.cookies()
            # print(cookies_list)
            await get_cookie(page)  # 导出cookie 完成登陆后就可以拿着cookie玩各种各样的事情了。
            total = await search(page)
            for i in range(2, total + 1):
                print('进入' + str(i) + '页前')
                await next_page(page, i)
    else:
        print('当前页面没有滑块')
        await page.keyboard.press('Enter')
        print("print enter")
        await page.evaluate('''document.getElementById("J_SubmitStatic").click()''')
        await page.waitFor(400)  # 单位：毫秒
        await page.waitForNavigation()
        total = await search(page)
        for i in range(2, total + 1):
            print(i)
            await next_page(page, i)

        try:
            global error  # 检测是否是账号密码错误
            print("error_1:", error)
            error = await page.Jeval('.error', 'node => node.textContent')
            print("error_2:", error)
        except Exception as e:
            error = None
        finally:
            if error:
                print('确保账户安全重新入输入')
                # loop.close()  # 程序退出
            else:
                print(page.url)
                await get_cookie(page)
    await browser.close()


if __name__ == '__main__':
    my_account = account
    my_password = pwd
    my_url = taobao_login_url
    loop = asyncio.get_event_loop()  # 协程，开启个无限循环的程序流程，把一些函数注册到事件循环上。当满足事件发生的时候，调用相应的协程函数。
    loop.run_until_complete(main(my_account, my_password, my_url))
