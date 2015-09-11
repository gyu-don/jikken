# coding: utf-8

from __future__ import print_function
from __future__ import division

import sys
import random
from collections import Counter
import matplotlib.pyplot as plt

import weather2014

def rain(p):
    '''「真の」降水確率pを引数として与える。
    雨ならばTrue, 晴れならばFalseを返す。'''
    return random.random() < p

class Evaluator:
    def __init__(self, bin_func=None):
        def default_bin_func(dat):
            '10%刻みに振り分ける。'
            return int(dat * 10 + 0.5) / 10

        self.rain = Counter()
        self.count = Counter()
        if bin_func:
            self.bin_func = bin_func
        else:
            self.bin_func = default_bin_func

    def add(self, estimate, result):
        idx = self.bin_func(estimate)
        if result:
            self.rain[idx] += 1
        self.count[idx] += 1

    def dump_as_csv(self, f=None):
        if not f:
            f = sys.stdout
        keys = sorted(self.count.keys())
        for k in keys:
            print('{},{},{}'.format(k, self.rain[k], self.count[k]), file=f)

    def get_r2(self):
        '''決定係数。いろいろ定義があるらしいが、
        Wikipediaで「一般的」とかかれているものを今回は利用した。
        1以下の値を返し、1に近いほど、確率がうまく予想できていることを示す。
        また、この定義では、値はマイナスになりうる。'''
        a = 0
        b = 0
        rain_ave = sum(self.rain.values()) / sum(self.count.values())
        for k in self.count:
            p = self.rain[k] / self.count[k]
            a += (p - k) ** 2
            b += (p - rain_ave) ** 2
        try:
            return 1 - a/b
        except ZeroDivisionError:
            return 0.0

    def plot(self):
        x = sorted(self.count.keys())
        y = [self.rain[k] / self.count[k] for k in x]
        plt.plot(x, y)
        plt.xlim((0, 1))
        plt.ylim((0, 1))
        plt.show()

if __name__ == '__main__':
    print('Case 1: 真の降水確率は20%, 40%を交互, 予想降水確率は的中。')
    a = Evaluator()
    for _ in range(1500):
        a.add(0.2, rain(0.2))
        a.add(0.4, rain(0.4))
    a.dump_as_csv()
    print(a.get_r2())
    a.plot()

    print('Case 2: 真の降水確率はμ=30%, σ=20%のガウシアン、'
          '予想降水確率はμ=真の降水確率, σ=15%のガウシアン')
    a = Evaluator()
    for _ in range(3000):
        p = random.gauss(0.3, 0.2)
        a.add(p, rain(random.gauss(p, 0.15)))
    a.dump_as_csv()
    print(a.get_r2())
    a.plot()

    print('Case 3: 東京の2014年の天気予報(2日前発表)と、実際の天気')
    # データは下記を使用。
    # http://homepage3.nifty.com/i_sawaki/WeatherForecast/
    # http://www.data.jma.go.jp/obd/stats/etrn/index.php
    # 降水確率の定義上、1 mm以上の降雨を雨とした。
    a = Evaluator()
    for r,p in weather2014.data:
        a.add(p / 100, r>=1.0)
    a.dump_as_csv()
    print(a.get_r2())
    a.plot()
