#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019-09-08 15:32
# @Author: yanmiexingkong
# @email : yanmiexingkong@gmail.com
# @File  : 2.png.py
import time
import asyncio

now = lambda: time.time()


async def do_some_work(x):
    print('Waiting: ', x)


start = now()

# coroutine = do_some_work(2)
# loop = asyncio.get_event_loop()
# loop.run_until_complete(coroutine)

asyncio.get_event_loop().run_until_complete(do_some_work(2))
print('TIME: ', now() - start)
