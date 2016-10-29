#!/usr/bin/env python3

import argparse
import bisect
import json
import random
from bottle import route, run, response, request
from functools import wraps
from time import time


ROUND_TIME = 10


def team_(x): return 'team_{}'.format(x)
def service_(x): return 'service_{}'.format(x)


@route('/')
def main_page():
    return "<h1>It works!</h1>"


def tojson(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        response.content_type = 'application/json'
        return fn(*args, **kwargs)

    return wrapper



@route('/info')
@tojson
def info_page():
    return {
        'teams': {team_(i): 'TEAM%d'%i for i in range(args.teams)},
        'services': {service_(i): 'SVC_%d'%i for i in range(args.services)},
        'start': 0
    }


@route('/scoreboard')
@tojson
def scores_page():
    return {
        'table': scores,
        'status': '1',
        'round': (int(time()) - start)//ROUND_TIME
    }


def update_events():
    last_upd = events[-1][0] if events else start
    current = int(time())
    for x in range(args.frequency*(current - last_upd)):
        attacker = random.randint(1, args.teams)
        victim = attacker
        while victim == attacker:
            victim = random.randint(1, args.teams)

        events.append([
            last_upd + x//args.frequency + 1,
            service_(random.randint(1, args.services)),
            team_(attacker), team_(victim)
        ])


@route('/events')
@tojson
def events_page():
    update_events()
    rtime = int(request.params['from'])*ROUND_TIME + start

    return json.dumps(events[bisect.bisect_left(events, [rtime, '', '', '']):])


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--teams', type=int, help='teams count',
                        default=20)
    parser.add_argument('-s', '--services', type=int, help='services count',
                        default=7)
    parser.add_argument('-q', '--frequency', type=int, help='attack frequency',
                        default=2)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    start = int(time())
    events = []
    scores = {team_(i): 0 for i in range(args.teams)}

    run(host='0.0.0.0', port=8000, debug=True, reloader=True)
