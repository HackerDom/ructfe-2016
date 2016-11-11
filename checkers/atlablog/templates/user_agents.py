#!/usr/bin/env python3
import random


def get():
    for i in range(2):
        try:
            return __get()
        except Exception as e:
            error = e
    raise OSError(str(error))


def __get():
    with open('useragents') as fin:
        user_agents = [line.strip() for line in fin]
    return random.choice(user_agents)
