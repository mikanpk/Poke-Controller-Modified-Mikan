#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.Keys import Button, Direction
from .ImageProcPythonCommandAddin import ImageProcPythonCommandAddin
import time

# 3闘色厳選用プログラム
# キャンプを閉じると遭遇する位置でスタートすること
# 時間微調整用に、メッセージ表示までの時間出力がされる
class PkmnSwSh_SymbolShiny(ImageProcPythonCommandAddin):
    NAME = '剣盾シンボル色厳選（3闘）'
    
    def __init__(self, cam, gui=None):
        super().__init__(cam)
        self.cam = cam
        self.gui = gui

    def do(self):
        # 通常色であると判定するための閾値となる時間（秒）
        TIMER1 = 5.8    # キャンプ終了～現れた！までの時間
        TIMER2 = 2.8    # 現れた！～いっておいで！までの時間
        # 所要時間記録用
        countTimer1= 0
        countTimer2 = 0
        sumTimer1 = 0
        sumTimer2 = 0
        minTimer1 = 9999
        minTimer2 = 9999
        maxTimer1 = 0
        maxTimer2 = 0
        # ループ回数
        count = 0 

        # 実処理
        while True:
            count += 1
            print(f'{count}回目')
            # キャンプを開く
            self.press(Button.X, wait=1)
            self.press(Button.A, wait=1)
            # キャンプを閉じる
            while not self.isContainTemplate('pkmnSWSH_SymbolShiny_img/camp_close_yes.png', threshold=0.8):
                self.press(Button.B, wait=1)
            self.press(Button.A, wait=2)
            timerStart = time.time()
            # ○○が現れた！
            while not self.isContainTemplate('pkmnSWSH_SymbolShiny_img/encount.png', threshold=0.8):
                pass
            timerEnd1 = time.time()
            countTimer1 = timerEnd1 - timerStart  # 現れた！までの時間の計算
            sumTimer1 += countTimer1
            minTimer1 = min(minTimer1, countTimer1)
            maxTimer1 = max(maxTimer1, countTimer1)
            print(f'遭遇 {countTimer1:.2f} < {TIMER1}  min/max/ave:{minTimer1:.2f}/{maxTimer1:.2f}/{sumTimer1 / count:.2f}')
            self.wait(1)
            # いっておいで！
            while not self.isContainTemplate('pkmnSWSH_SymbolShiny_img/go.png', threshold=0.8):
                pass
            timerEnd2 = time.time()
            countTimer2 = timerEnd2 - timerEnd1  # いっておいで！までの時間の計算
            sumTimer2 += countTimer2
            minTimer2 = min(minTimer2, countTimer2) 
            maxTimer2 = max(maxTimer2, countTimer2)
            print(f'逃走 {countTimer2:.2f} < {TIMER2}  min/max/ave:{minTimer2:.2f}/{maxTimer2:.2f}/{sumTimer2 / count:.2f}')
            # 逃げる
            if countTimer1 < TIMER1 and countTimer2 < TIMER2:
                # たたかう表示待機
                while not self.isContainTemplate('pkmnSWSH_SymbolShiny_img/command_battle_on.png', threshold=0.8):
                    pass
                self.press(Direction.UP, wait=0.2)
                self.press(Button.A, wait=7)
            else:
                break
