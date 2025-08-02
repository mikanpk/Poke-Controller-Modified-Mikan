#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.Keys import Button, Direction
from .ImageProcPythonCommandAddin import ImageProcPythonCommandAddin
import time


# auto egg hatching using image recognition
# 自動卵孵化(キャプボあり)
class PkmnSwSh_SymbolShiny(ImageProcPythonCommandAddin):
    NAME = '剣盾シンボル色厳選'

    def __init__(self, cam, gui=None):
        super().__init__(cam)
        self.cam = cam
        self.gui = gui

    def do(self):
        TIMER1 = 5.5
        TIMER2 = 8.5
        sumTimer1 = 0
        sumTimer2 = 0
        minTimer1 = 9999
        minTimer2 = 9999
        maxTimer1 = 0
        maxTimer2 = 0
        count = 0 
        while True:
            # キャンプを開く
            count += 1
            self.press(Button.X, wait=1)
            self.press(Button.A, wait=2)
            while not self.isContainTemplate('pkmnSWSH_SymbolShiny_img/camp_close_yes.png', threshold=0.8):
                self.press(Button.B, wait=2)
            self.press(Button.A, wait=2)
            timerStart = time.time()
            # ○○が現れた！
            while not self.isContainTemplate('pkmnSWSH_SymbolShiny_img/encount.png', threshold=0.8):
                pass
            timerEnd1 = time.time()
            sumTimer1 += (timerEnd1 - timerStart) # いっておいで！までの時間
            minTimer1 = min(minTimer1, timerEnd1 - timerStart)
            maxTimer1 = max(maxTimer1, timerEnd1 - timerStart)
            print(f'{count}回目 遭遇 {(timerEnd1 - timerStart):.2f}秒 < {TIMER1} ')
            print(f'     ave: {sumTimer1 / count:.2f} min: {minTimer1:.2f} max: {maxTimer1:.2f}')
            self.wait(1)
            # いっておいで！
            while not self.isContainTemplate('pkmnSWSH_SymbolShiny_img/go.png', threshold=0.8):
                pass
            timerEnd2 = time.time()
            sumTimer2 += (timerEnd2 - timerStart) # 逃げるまでの時間
            minTimer2 = min(minTimer2, timerEnd2 - timerStart)
            maxTimer2 = max(maxTimer2, timerEnd2 - timerStart)
            print(f'{count}回目 逃げる {(timerEnd2 - timerStart):.2f}秒 < {TIMER2}')
            print(f'     ave: {sumTimer2 / count:.2f}秒 min: {minTimer2:.2f} max: {maxTimer2:.2f}')
            # 逃げる
            if (timerEnd1 - timerStart) < TIMER1 and (timerEnd2 - timerStart) < TIMER2:
                self.wait(4.5)
                self.press(Direction.UP, wait=0.2)
                self.press(Button.A, wait=7)
            else:
                break
