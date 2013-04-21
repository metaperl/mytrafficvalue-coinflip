#!/usr/bin/python
from __future__ import print_function
import os
import sys
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# system
from collections import defaultdict

import datetime
from functools import wraps
import pdb
import pprint
import re
import sys
import time
import traceback

# pypi
from blargs   import Parser
from splinter import Browser

# local
import user


pp = pprint.PrettyPrinter(indent=4)

base_url = 'http://www.mytrafficvalue.com'

action_path = dict(
    login = "",
    coin_flip = "games/coin_flip.html"
)

one_minute  = 60
ten_minutes = 10 * one_minute
one_hour    = 3600

def martingale_sequence():
    l = [0.25,2, 4, 8, 16, 32,66]
    return iter(l)

def url_for_action(action):
    return "{0}/{1}".format(base_url,action_path[action])

def loop_forever():
    while True: pass

def current_time():
    now = datetime.datetime.now()
    return now.strftime("%I:%M%p")


def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


class Entry(object):

    def __init__(self, user, browser, url):
        self.user=user
        self.browser=browser
        self.url=url

    def login(self):
        print("Logging in...")
        self.browser.visit(url_for_action('login'))
        self.browser.fill('user[email]', self.user['username'])
        self.browser.fill('user[password]', self.user['password'])
        button = self.browser.find_by_name('submit').first
        button.click()

    def input_bet(self,bet):
        print("Inputting bet of", bet)
        bet = str(bet)
        self.browser.fill('bet', bet)

    def guess_coin_toss(self, flip):
        lookup = '//a[@data-value="{0}"]'.format(flip)
        print("Guessing", flip)
        print("Clicking it now...", flip)
        button = self.browser.find_by_xpath(lookup).first
        button.click()

    def click_payment_method_pulldown(self):
        time.sleep(1)
        button = self.browser.find_by_xpath('//*[@class="selectedBalance"]')
        button.click()


    def click_payment_method(self, method):
        lookup = '//li[@data-code="{0}"]'.format(method)
        li = self.browser.find_by_xpath(lookup).first
        button = li.find_by_tag('a').first
        button.click()

    def win(self):
        result = self.browser.find_by_id('result').first.value
        print("Result", result)
        return "right" in result


    def poll_for_login(self):
        print("\tPolling for successful login.")
        at = self.browser.find_by_id('logout')
        if at:
            print("Logged in")
            return True
        else:
            time.sleep(5)
            return self.poll_for_login()

    def trade(self, seq):

        self.poll_for_login()
        self.browser.visit(url_for_action('coin_flip'))
        print("Clicking Payment Method Pulldown")
        self.click_payment_method_pulldown()
        time.sleep(1)
        print("Clicking Payment Method")
        #self.click_payment_method('st') # solid trust pay
        self.click_payment_method('ap')  # egopay
        self.input_bet(seq.next())
        time.sleep(4)
        self.guess_coin_toss('heads')
        time.sleep(20)

        if self.win():
            print("I win")
            return
        else:
            print("lost")



def main(bid_url=None):
    args = dict()
    with Parser(args) as p:
        p.flag('live')

    with Browser() as browser:

        _u = user.User()
        key = 'live' if args['live'] else 'demo'
        u = getattr(_u, key)
        e = Entry(u, browser, bid_url)
        e.browser.visit(base_url)

        while True:
            s = martingale_sequence()
            e.trade(s)


if __name__ == '__main__':
    main(base_url)
