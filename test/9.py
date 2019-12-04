#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019-09-09 09:26
# @Author: yanmiexingkong
# @email : yanmiexingkong@gmail.com
# @File  : 9.py
import asyncio


# 定义了一个简单的协程
async def simple_async():
    print('hello')
    await asyncio.sleep(1)  # 休眠1秒
    print('python')


# 使用asynio中run方法运行一个协程
asyncio.run(simple_async())
