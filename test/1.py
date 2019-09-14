#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019-09-08 15:24
# @Author: PythonVampire
# @email : vampire@ivamp.cn
# @File  : 1.py
import asyncio
from pyppeteer import launch
from pyquery import PyQuery as Pq


async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('http://quotes.toscrape.com/js/')
    doc = Pq(await page.content())
    print('Quotes:', doc('.quote').length)
    await browser.close()


asyncio.get_event_loop().run_until_complete(main())
