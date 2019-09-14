#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2019-09-09 09:22
# @Author: PythonVampire
# @email : vampire@ivamp.cn
# @File  : 8.py


def producer(c):
    n = 0
    while n < 5:
        n += 1
        print('producer {}'.format(n))
        r = c.send(n)
        print('consumer return {}'.format(r))


def consumer():
    r = ''
    while True:
        n = yield r
        if not n:
            return
        print('consumer {} '.format(n))
        r = 'ok'


if __name__ == '__main__':
    c = consumer()
    next(c)  # 启动consumer
    producer(c)
