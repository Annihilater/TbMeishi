#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019-09-08 15:36
# @Author: yanmiexingkong
# @email : yanmiexingkong@gmail.com
# @File  : 3.py
import asyncio
import time

now = lambda: time.time()


async def do_some_work(x):
    print('Waiting: ', x)


start = now()

coroutine = do_some_work(2)
loop = asyncio.get_event_loop()
# task = asyncio.ensure_future(coroutine)
task = loop.create_task(coroutine)
print(task)
loop.run_until_complete(task)
print(task)
print('TIME: ', now() - start)
