#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
色タマゴ孵化(SV)_v4.0 Release.2025/5/XX by mikan
# おもな改修内容
  - コードの整理、Extension版での動作確認
  - 画像認識処理の変更（位置や数を取得できるように拡張）
  - LINE Notice廃止に伴う機能の削除
"""
import datetime
from .ImageProcPythonCommandAddin import ImageProcPythonCommandAddin
from Commands.Keys import Button, Direction, Stick

class SV_HatchingShiny(ImageProcPythonCommandAddin):

    NAME = "SVタマゴ孵化"

    # 画面トリミング範囲の定義 [左上x,左上y,右下x,右下y]
    # 画像認識の際に、特定のUI要素だけを切り出して判定するための座標です。
    CROPAREA_MINIMAP      = [1060, 485, 1280, 650]    # ミニマップの範囲
    CROPAREA_MASSAGE        = [325, 525, 955, 650]      # メッセージの範囲
    CROPAREA_XMENU_PARTY    = [50, 105, 375, 720]       # Xメニューで手持ちポケモンが表示される範囲
    CROPAERA_BOX_BUTTON     = [0, 0, 80, 50]            # ボックスを開いているかを確認するためのXマークの位置
    CROPAREA_BOX_LV         = [830, 1, 1279, 100]       # ボックス内でレベル表示がある範囲
    CROPAREA_BOX_INBOX      = [280, 125, 810, 560]      # ボックス内のセル部分
    CROPAREA_BOX_STATUS     = [830, 1, 1279, 720]       # ボックス右側の詳細情報表示範囲
    CROPAREA_BOX_PARTYPKMN  = [0, 50, 280, 720]         # 手持ち表示の範囲
    CROPAREA_BOX_UNDERCOMMANDMENU = [0, 650, 1280, 720] # ボックス下部のコマンドメニュー範囲

    ###############################################
    # 調整してほしいエリア
    ###############################################
    # 使用画像一覧
    # 使用している画像は以下のみです
    # 差し替える場合は個々の値を確認
    PATH_BOX_BUTTON_X           = "pkmnSV_AutoHatching_img/box_button_x.png"
    PATH_BOX_COMMAND_YES        = "pkmnSV_AutoHatching_img/box_command_yes.png"
    PATH_BOX_CURSOR_BG          = "pkmnSV_AutoHatching_img/box_cursor_bg.png"
    PATH_BOX_EGG                = "pkmnSV_AutoHatching_img/box_egg.png"
    PATH_BOX_MENU_NIGASU        = "pkmnSV_AutoHatching_img/box_menu_nigasu.png"
    PATH_BOX_NAME_BASE          = "pkmnSV_AutoHatching_img/box_name_base.png"
    PATH_BOX_NAME_EGG           = "pkmnSV_AutoHatching_img/box_name_egg.png"
    PATH_BOX_NULL_CELL          = "pkmnSV_AutoHatching_img/box_null_cell.png"
    PATH_BOX_NULL_COLUMN        = "pkmnSV_AutoHatching_img/box_null_column.png"
    PATH_BOX_NULL_PARTYCELL     = "pkmnSV_AutoHatching_img/box_null_partycell.png"
    PATH_BOX_STATUS_0           = "pkmnSV_AutoHatching_img/box_status_0.png"
    PATH_BOX_STATUS_31          = "pkmnSV_AutoHatching_img/box_status_31.png"
    PATH_BOX_STATUS_LEVEL       = "pkmnSV_AutoHatching_img/box_status_lv.png"
    PATH_BOX_STATUS_SHINY       = "pkmnSV_AutoHatching_img/box_status_shiny.png"
    PATH_BOX_UNDERCOMANDMENU_CATCHINGPKMN   = "pkmnSV_AutoHatching_img/box_undercommandmenu_catchingpkmn.png"
    PATH_BOX_UNDERCOMANDMENU_JUDGEMODE      = "pkmnSV_AutoHatching_img/box_undercommandmenu_judgemode.png"
    PATH_FIELD_MINIMAP          = "pkmnSV_AutoHatching_img/field_minimap.png"
    PATH_MESSAGE_HATCHING       = "pkmnSV_AutoHatching_img/message_hatching.png"
    PATH_MESSAGE_WINDOW         = "pkmnSV_AutoHatching_img/message_window.png"
    PATH_PICNIC_BUTTON_YPUSH                     = "pkmnSV_AutoHatching_img/picnic_command_y.png"
    PATH_PICNIC_COMMAND_YES                 = "pkmnSV_AutoHatching_img/picnic_command_yes.png"
    PATH_PICNIC_MESSAGE_BASKET_CHECK        = "pkmnSV_AutoHatching_img/picnic_message_basket_check.png"
    PATH_PICNIC_MESSAGE_BASKET_EGG_GET      = "pkmnSV_AutoHatching_img/picnic_message_basket_egg_get.png.png"
    PATH_PICNIC_MESSAGE_BASKET_EGG_SEND     = "pkmnSV_AutoHatching_img/picnic_message_basket_egg_send.png"
    PATH_PICNIC_MESSAGE_CLOSE               = "pkmnSV_AutoHatching_img/picnic_message_close.png"
    PATH_PICNIC_SANDWITCH_COOKING_HAND  = "pkmnSV_AutoHatching_img/picnic_sandwitch_cooking_hand.png"
    PATH_PICNIC_SANDWITCH_COOKING_TIMER = "pkmnSV_AutoHatching_img/picnic_sandwitch_cooking_timer.png"
    PATH_PICNIC_SANDWITCH_NAME          = "pkmnSV_AutoHatching_img/picnic_sandwitch_menu_name.png"
    PATH_PICNIC_SANDWITCH_MENU_TITLE    = "pkmnSV_AutoHatching_img/picnic_sandwitch_menu_title.png"
    PATH_SV_LOADING             = "pkmnSV_AutoHatching_img/sv_loading.png"
    PATH_XMENU_EGG              = "pkmnSV_AutoHatching_img/xmenu_egg.png"
    PATH_XMENU_FOUCUS_BOX       = "pkmnSV_AutoHatching_img/xmenu_focus_box.png"
    PATH_XMENU_FOUCUS_PICNINC   = "pkmnSV_AutoHatching_img/xmenu_focus_picnic.png"
    PATH_XMENU_TITLE            = "pkmnSV_AutoHatching_img/xmenu_title.png"
    PATH_YMENU_MAP              = "pkmnSV_AutoHatching_img/ymenu_map.png"
    PATH_YMENU_SORAWOTOBU       = "pkmnSV_AutoHatching_img/ymenu_sorawotobu.png"

    def __init__(self, cam, gui=None):
        super().__init__(cam)
        self.cam = cam
        self.gui = gui

        # カウンタ（編集不要）
        self.total_hatched = 0  # 孵化数合計の合計
        self.total_shiny = 0    # 色違い取得数の合計
        self.total_status = 0   # 個体値一致取得数の合計

        ###############################################
        # 調整してほしいエリア
        ###############################################
        # 実行用パラメータ （要件に合わせて変更してください）
        self.max_egg = 30                   # タマゴ取得数（最大1BOX=30）
        self.max_shiny = 10                 # 色違いが何回出たら停止するか
        self.statuscheck_flag = False       # ステータスの確認実施をするか
        self.status = [                     # ステータスの確認実施をするときに、残しておきたい個体値
            # [H,A,B,C,D,S]（0、31、-1=任意）
            [31, 31, 31, 31, 31, 31],       # 6Vの例
            [31, 0, 31, 31, 31, 31],        # 5V（A抜）の例
            [-1, 0, -1, -1, -1, -1]         # A抜の例
        ]

    def do(self):
        # 案内
        print("========================================")
        print("タマゴ孵化(SV)_v4.0")
        print("トラブル事例はこちらをご確認下さい")
        print("https://note.com/mikan_tabetaine/n/n031a1808072d")
        print("========================================")

        # 実行状態を保持するカウンタを初期化
        progress_status = 0


        # total_shiny数分取得するまで繰り返す
        while True:

            dt_now = datetime.datetime.now()
            print(f"--- {dt_now.strftime('%Y/%m/%d %H:%M:%S')} ---")
            print(f"- 色違い{self.total_shiny}/{self.max_shiny}")

            match progress_status:

                case 99:
                    print(f"## {progress_status} ソフトを再起動")
                    self.reboot_soft()
                    progress_status = 0

                case 0:
                    print(f"## {progress_status} 手持ちのタマゴ有無を確認")
                    partyEggs = self.xmenu_eggs_count()
                    if partyEggs == 0:
                        progress_status = 1
                    else:
                        progress_status = 3

                case 1:
                    print(f"## {progress_status} 手持ちを親に変更し、ピクニック 色違い{self.total_shiny}/{self.max_shiny}")
                    if self.changeparty_parent_pull()  \
                            and self.reset_position_zerogate()\
                            and self.eggs_lay(self.max_egg) \
                            and self.changeparty_parent_put():
                        progress_status = 2
                    else:
                        self.camera.saveCapture()
                        progress_status = 99

                case 2:
                    print(f"## {progress_status}> ボックス内のタマゴを手持ちに移動 色違い{self.total_shiny}/{self.max_shiny}")
                    partyEggs = self.changeparty_egg_pull()
                    if partyEggs > 0:
                       progress_status = 3
                    else:
                       progress_status = 4

                case 3:
                    print(f"<{progress_status}>手持ち・ボックス内タマゴの孵化 色違い{self.total_shiny}/{self.max_shiny}")
                    if self.reset_position_zerogate() \
                            and self.hatching_party(partyEggs):
                        self.changeparty_hatchedeggs_put()
                        progress_status = 2
                    else:
                        self.camera.saveCapture()
                        progress_status = 99

                case 4:
                    print(f"<{progress_status}>孵化結果の確認 色違い{self.total_shiny}/{self.max_shiny}")
                    # いったん逃がさない状態で確認する
                    shiny_count, statusmatch_count = self.box_hatched_check(release_flag=False, statuscheck_flag=self.statuscheck_flag)
                    self.total_shiny += shiny_count
                    self.total_status += statusmatch_count
                    # 逃がし処理の実施
                    if shiny_count+statusmatch_count > 0:
                        _, _ = self.box_hatched_check(release_flag=True, statuscheck_flag=False)
                        # <6>レポートを書く
                        print("◆レポートを書いて次のループを開始 色違い{self.total_shiny}/{self.max_shiny}")
                        self.report_write()
                        # 色違い数が指定数以上であれば終了
                        if self.total_shiny >= self.max_shiny:
                            print("◆色違い数が指定数に達したためプログラムを終了 色違い{self.total_shiny}/{self.max_shiny}")
                            self.finish()
                        progress_status = 0
                    else:
                        progress_status = 99

    def reboot_soft(self):
        """
        ソフト再起動（ソフトウェアの起動確認メッセージ対応）
        """
        # ソフトを終了
        self.press(Button.HOME, 0.1, wait=1.8)
        self.press(Button.X, 0.1, wait=1)
        self.press(Button.A, 0.1, wait=4)
        self.press(Button.A, 0.1, wait=4)
        self.press(Button.A, 0.1, wait=20)  # ソフトの状況確認
        # ポケモンSVのローディング画面までA連打
        for _ in range(0, 60):
            if self.isContainTemplate(self.PATH_SV_LOADING, threshold=0.9):
                break
            else:
                self.press(Button.A, wait=0.5)
        else:
            self.finish()

    def report_write(self):
        """
        レポートを書く

        returns
        -------
        None
        """
        self.xmenu_open()
        self.press(Button.R, wait=1)
        self.pressRep(Button.A, repeat=2, interval=0.5)
        self.wait(3)
        self.pressRep(Button.B, repeat=5, interval=0.5)

    def fiield_minimap_check(self) -> bool:
        """
        フィールド画面になっているかどうかの判定

        ミニマップの表示で確認する

        returns
        -------
        bool : True ミニマップ（プレーヤーマーカー）あり
               False 表示なし
        """
        return self.isContainTemplate(self.PATH_FIELD_MINIMAP, crop=self.CROPAREA_MINIMAP)

    def field_return(self) -> bool:
        """
        フィールド表示になるまでB押下を繰り返す

        returns
        -------
        bool
            True:成功
            False:エラーあり
        """
        print("[field_return]フィールド表示になるまでB押下")
        for _ in range(0, 10):
            if self.fiield_minimap_check():
                break
            else:
                self.press(Button.B, wait=1)
        else:
            print("[field_return]ERROR：フィールド画面に戻れませんでした")
            return False
        # 正常終了
        return True

    def xmenu_eggs_count(self) -> int:
        """ 手持ちのタマゴ数の確認

        何も開いていない状態から、Xメニューを開いて手持ちのタマゴの数を確認する

        Returns
        -------
        int
            手持ちのタマゴ数
        """
        partyEggs = 0
        self.xmenu_open()
        partyEggs, _ = self.isContainTemplateCount(self.PATH_XMENU_EGG, crop=self.CROPAREA_XMENU_PARTY)
        # 手持ちのタマゴ数を返す
        print("[xmenu_eggs_count]手持ちタマゴ数：", partyEggs)
        return partyEggs

    def xmenu_open(self) -> bool:
        """
        Xメニューを開く

        returns
        -------
        bool
            True:成功
            False:エラーあり
        """
        for _ in range(0, 30):
            if self.isContainTemplate(self.PATH_XMENU_TITLE):
                break
            elif self.fiield_minimap_check():
                self.press(Button.X, wait=1)
            else:
                self.press(Button.B, wait=0.5)
        else:
            print("[xmenu_open]ERROR：Xメニューの表示画像検出失敗")
            return False
        # カーソル位置を右にそろえる
        self.press(Direction.RIGHT, wait=1)
        # 正常終了
        return True

    def box_open(self) -> bool:
        """
        ボックスを開く・ジャッジモードであることを確認する

        returns
        -------
        bool : True 操作成功
               False 操作失敗
        """
        # リトライ用
        for _ in range(0, 2):
            # ボックスが開いている場合終了
            if self.isContainTemplate(self.PATH_BOX_BUTTON_X, crop=self.CROPAERA_BOX_BUTTON, threshold=0.9):
                break
            # ボックスが開いていない場合は、ボックスを開くためXメニューを開く
            self.xmenu_open()
            # ボックスにカーソルを移動
            for _ in range(0, 10):
                if self.isContainTemplate(self.PATH_XMENU_FOUCUS_BOX):
                    break
                self.press(Direction.DOWN, wait=0.5)
            else:
                return False
            self.press(Button.A, wait=3)
        else:
            return False

        # 正常終了
        self.box_cursor_move(row=1, column=0)
        return True

    def picnic_open(self) -> bool:
        """
        Xメニューを開いてピクニックを選択する

        returns
        -------
            bool : 処理成功か
        """
        # プレイヤーの向きを手前に向ける
        self.press(Direction.DOWN, duration=0.2, wait=0.5)
        # Xmenuを開く
        self.xmenu_open()
        # リトライ上限
        for _ in range(0, 10):
            if not self.isContainTemplate(self.PATH_XMENU_FOUCUS_PICNINC):
                self.press(Direction.DOWN, wait=0.5)
            else:
                self.press(Button.A, wait=7)
                break
        else:
            print("[picnic_open]ERROR：ピクニックメニュー画像認識失敗")
            return False
        self.wait(3)
        self.press(Button.PLUS)  # コライドン/ミライドンをしまう
        self.press(Direction.DOWN, duration=3, wait=0.5)  # プレイヤーの向きを手前に向ける
        return True

    def picnic_close(self) -> bool:
        """
        ピクニックを終了する
        ※ピクニック終了時のレベルアップ挙動終了の確認のためXメニューを開く

        returns
        -------
            bool : 処理成功か
        """

        print("[picnic_close]START")

        # リトライ上限
        for _ in range(0, 20):
            # 「ピクニックを やめようか？」の「はい」が表示されていたら
            if self.isContainTemplate(self.PATH_PICNIC_COMMAND_YES):
                self.press(Button.A, wait=1)
            # 「Y ピクニックをやめる」の表示がなくなったら
            elif not self.isContainTemplate(self.PATH_PICNIC_COMMAND_YPUSH):
                break
            else:
                self.press(Button.B, wait=0.5)  # 何か開いていた時用
                self.press(Button.Y, wait=1.5)  # 「Y ピクニックをやめる」
        else:
            print("[picnic_close]ERROR：ピクニックコマンド画像の認識失敗")
            return False
        self.wait(3)
        # レベルアップメッセージの表示が終了するのを確認する、メニューが開けるかどうかで終了を確認する
        # リトライ上限
        for _ in range(0, 15):
            if not self.isContainTemplate(self.PATH_XMENU_TITLE):
                self.press(Button.B, wait=0.5)
                self.press(Button.X, wait=1)
            else:
                break
        else:
            print("[picnic_close]ERROR：レベルアップメッセージ送り中にエラーが発生")
            return False
        # ボックスにカーソルを移動する
        self.press(Direction.UP)
        # 上記で開いたxメニューを終了する
        self.field_return()
        return True

    def eggs_lay(self, egg=30) -> bool :
        """
        ピクニックを開いてタマゴを取得する（サンドイッチを作る）

        Parameters
        ----------
        egg : int
            取得したいタマゴ数を設定すると、その数分バスケットからタマゴを取得する

        Returns
        -------
        bool
            成否
        """
        print("[eggs_lay]START")
        # ピクニックを開始
        self.picnic_open()
        # 料理開始（引数:作りたいサンドイッチ名）
        if not self.picnic_sandwich_make(recipe_path=self.PATH_PICNIC_SANDWITCH_NAME):
            return False
        # バスケットに向かう（うまく到達できない場合があるので、環境によっては要調整）
        self.press(Button.B)
        self.press(Direction.RIGHT, duration=0.5, wait=0.5)
        self.press(Direction.DOWN, duration=1, wait=0.5)
        self.press(Direction.LEFT, duration=0.1, wait=0.5)
        # 指定タマゴ数分、バスケットを確認する
        if not self.picnic_basket_check(egg):
            print("[eggs_lay]ERROR：バスケットからのタマゴ取得失敗")
            return False
        # ピクニック終了
        if not self.picnic_close():
            print("[eggs_lay]ERROR：ピクニックのクローズ失敗")
            return False
        print("[eggs_lay]END")
        return True

    def hatching_party(self, eggs=5):
        """
        タマゴ孵化処理

        Parameters
        ----------
        partyEggs  : int
            手持ちのタマゴの数を引数に設定すると、その数分孵化処理を行う

        Returns
        -------
        bool
            成否
        """
        print("[hatching]START")
        self.field_return()
        # ポケモンに乗る
        self.press(Button.PLUS, wait=0.5)
        # 手持ちのタマゴ数分繰り返す
        print(f"[hatching]孵化メッセージを{eggs}回確認するまで繰り返す")
        for hatched_count in range(0, eggs):
            # 走り始める
            self.hold([Direction(Stick.LEFT, 85), Direction(Stick.RIGHT, 180)])
            # 孵化アニメーションが始まるまで繰り返す
            for _ in range(0, 500):
                self.press(Button.LCLICK)   # Lスティック押し込み
                if self.isContainTemplate(self.PATH_MESSAGE_HATCHING, crop=self.CROPAREA_MASSAGE):
                    # メッセージ送り
                    self.press(Button.A)
                    # 走行をやめる
                    self.holdEnd([Direction(Stick.LEFT, 85),
                                 Direction(Stick.RIGHT, 180)])
                    # 孵化数をカウントする
                    self.total_hatched += 1
                    print(f"[hatching]孵化メッセージ認識成功{str(hatched_count + 1)}/{eggs} 計:{str(self.total_hatched)}")
                    break
            else:
                # 一定数以上繰り返しても繰り返しを抜けない場合、孵化失敗と判断しFalseを返す
                print("[hatching]ERROR：一定時間走行してもタマゴ孵化しませんでした")
                self.holdEnd(
                    [Direction(Stick.LEFT, 85), Direction(Stick.RIGHT, 180)]
                )
                return False
            # 孵化アニメーション終了（ミニマップが表示される）までA連打
            self.wait(10)
            print("[hatching]孵化アニメーション終了までA連打（ミニマップ画像確認）")
            for _ in range(0, 50):
                if self.fiield_minimap_check():
                    break
                # メッセージ送り
                self.press(Button.A, wait=0.5)
            else:
                print("[hatching]ERROR：孵化アニメーション終了確認失敗")
                self.finish()
            # プレイヤーの向きを修正
            self.wait(2)
            self.press(Button.L, wait=0.5)
            self.wait(0.3)
        # 手持ちのタマゴ分繰り返したら終了
        return True

    def box_box_move_target(self, boxtitle_path,left_flag=True) -> bool:
        """
        指定のボックスまで移動する

        Parameters
        ----------
        boxtitle_path : str
            開きたいボックス名の画像パスを渡す

        returns
        -------
            bool : 成否

        """

        # 失敗したらリトライするための繰り返し
        for _ in range(0, 2):
            # 最大32回ボックスを移動する
            for i in range(0, 32):
                # 引数の画像（ボックス名画像）と一致したか
                if self.isContainTemplate(boxtitle_path):
                    print("[box_box_move_target]指定ボックスを認識")
                    return True
                # 見つからなかった場合、LRボタンで移動
                if left_flag:
                    print(f"[box_box_move_target]L方向に移動:{i}回")
                    self.press(Button.L, wait=0.3)
                else:
                    print(f"[box_box_move_target]R方向に移動:{i}回")
                    self.press(Button.R, wait=0.3)
            else:
                # リトライ
                self.field_return()
                self.box_open()
        else:
            print("[box_box_move_target]ERROR：指定画像のボックスが見つかりませんでした")
            print("※頻発する場合は画像の差し替え、閾値調整を行ってください")
            self.finish()
            return False



    def box_pressbutton_minus(self):
        """
        マイナスボタンでポケモンを掴むモードにする
        【前提】ボックスを開いた状態

        Returns
        -------
        bool
            成否
        """
        print("[box_pressbutton_minus]マイナスボタンでポケモンをつかむ")
        # リトライ上限
        for _ in range(0, 5):
            if self.isContainTemplate(
                    self.PATH_BOX_UNDERCOMANDMENU_CATCHINGPKMN,
                    crop=self.CROPAREA_BOX_UNDERCOMMANDMENU):
                return True
            else:
                self.press(Button.MINUS, wait=0.8)
        else:
            print("[box_pressbutton_minus]FAILD:掴んでいる状態のコマンド画像認識失敗")
        return False


    def box_cursor_move(self, row, column) -> bool:
        """
        ボックスのカーソルを、指定の行列の位置に移動する
        【前提】ボックスを開いた状態

        returns
        -------
            bool
                True:成功
                False:エラーあり

        Parameters
        ----------
        row : int
            移動したいボックスの行を渡す
        column  : int
            移動したいボックスの列を渡す
        """

        # 十字キー押下調整
        DURATION = 0.04
        WAIT = 0.3
        # タイトル位置は0-4で統一
        if row==0:
            column=4
        self.wait(0.5)

        # カーソルを移動（最大試行回数5回）
        for _ in range(0, 5):

            # カーソル背景色の座標を取得（黄色背景位置）
            # 戻り値 res：[x, y, w, h, mx, my]
            res = self.isContainTemplateHSV(self.PATH_BOX_CURSOR_BG, crop=[0, 50, 810, 650])
            # ボックスの行列に変換
            focus_row, focus_column = self.box_cell_convert_position(top=res[5], left=res[4])

            # カーソル位置が目的位置の場合繰り返しを終了
            if focus_column == column and focus_row == row:
                return True

            # 座標が取得できたか確認
            if focus_row is None:
                # ポケモン選択後すぐB押下したときに背景色が消えるバグの対応
                # とりあえず下ボタンを押してみる
                self.press(Direction.DOWN, duration=DURATION)
                self.press(Direction.UP, duration=DURATION)
                continue
            # ボックス名の位置だった場合下を押下してもう一度位置を確認
            if focus_row == 0 and row!=0:
                self.press(Direction.DOWN, duration=DURATION)
                continue
            # 「いちらん」「けんさく」の位置だった場合下を押下してもう一度位置を確認
            if focus_row == 6 and focus_column != 0:
                self.press(Direction.UP, duration=DURATION)
                continue

            print(f"[box_cursor_move]カーソル移動 {focus_row},{focus_column} -> {row},{column}")
            # ボタン押下数の計算
            push_left = focus_column - column
            push_right = column - focus_column
            if focus_row == 0:
                push_left = 0
                push_right = 0
            push_up = focus_row - row
            push_down = row - focus_row
            # 回数分押下
            if push_left > 0:
                for _ in range(0, push_left):
                    self.press(Direction.LEFT, duration=DURATION)
                    self.wait(WAIT)
            if push_right > 0:
                for _ in range(0, push_right):
                    self.press(Direction.RIGHT, duration=DURATION)
                    self.wait(WAIT)
            if push_up > 0:
                for _ in range(0, push_up):
                    self.press(Direction.UP, duration=DURATION)
                    self.wait(WAIT)
            if push_down > 0:
                for _ in range(0, push_down):
                    self.press(Direction.DOWN, duration=DURATION)
                    self.wait(WAIT)
        else:
            print("[box_cursor_move]ERROR：カーソル移動上限到達 ", row, "行", column, "列")
            print("※頻発する場合は待機時間や閾値を調整して下さい")
            return False

    def box_cell_convert_position(self, top=None, left=None):
        """
        座標位置 => ボックスの行列に変換して返す
        列0 : パーティ列
        列1~6 : ボックスの列

        Parameters
        ----------
        top : int
            上からの座標を渡すと、座標位置がボックスの何行目かを返す
        left : int
            左からの座標を渡すと、座標位置がボックスの何列目かを返す

        Retirn
        ----------
        result_row: int
            変換後の行の値
        result_column: int
            変換後の列の値
        """
        # 初期化
        CELL_WIDTH = 84          # 1列の幅
        CELL_HEIGHT = 84         # 1列の高さ
        POINT_TOP = 130     # 1列目の上端
        POINT_LEFT = 300    # 1列目の左端

        result_row = None
        result_column = None

        if top != None:
            if top < POINT_TOP:
                result_row = 0
            else:
                result_row, _ = divmod(top-POINT_TOP+CELL_HEIGHT, CELL_HEIGHT)
        if left != None:
            if left < POINT_LEFT:
                result_column = 0
            else:
                result_column, _ = divmod(left-POINT_LEFT+CELL_WIDTH, CELL_HEIGHT)

        return result_row, result_column

    def box_cell_find_posirion(self, path, threshold=0.9):
        """
        ボックス画面で、引数画像と同じセルの行列を返す

        Returns
        -------
        [int（行）,int（列）]
            セルがある場合
        [None,None]
            セルがない場合
        """
        print("[box_cell_find_posirion]指定画像と同じ状態のセルを見つける")
        result_row=None
        result_column=None
        cellcount, result_boxes = self.isContainTemplateCount(
            template_path=path,
            use_gray=True,
            use_edge=True,
            threshold=threshold,
            crop=self.CROPAREA_BOX_INBOX)

        if cellcount==0:
            return None,None

        x1 = result_boxes[0][0]
        y1 = result_boxes[0][1]
        x2 = result_boxes[0][2]
        y2 = result_boxes[0][3]
        result_row, result_column = self.box_cell_convert_position(top=(y1+y2)/2, left=(x1+x2)/2)
        result_row=int(result_row)
        result_column=int(result_column)
        print(f"[box_cell_find_posirion]{result_row}行{result_column}列")
        return result_row, result_column

    def box_party_count(self) -> int:
        """
        ボックス画面で、手持ちの数を確認して返却する
        【前提】BOXを開いた状態から実行、カーソル（黄色背景）が手持ち以外にある状態

        Returns
        -------
        int
            手持ち数
        """
        # エッジ比較で空き画像数を検出・カウント
        cellcount, _ = self.isContainTemplateCount(
            self.PATH_BOX_NULL_PARTYCELL,
            crop=self.CROPAREA_BOX_PARTYPKMN,
            use_edge=True)
        # 最大手持ち数-空き画像数で手持ちの数を計算
        return 6-cellcount

    def box_pkmn_release(self) -> bool:
        """
        逃がす処理
        【前提】対象のポケモンにカーソルをあてた状態から

        Returns
        -------
        bool
            成否
        """
        # print("[box_pkmn_release]レベル画像を確認、タマゴでないか？")

        # カーソル対象がポケモン（＝レベル表示がある）
        if self.isContainTemplate(self.PATH_BOX_STATUS_LEVEL, crop=self.CROPAREA_BOX_LV):
            # 逃がすコマンド
            self.press(Button.A, wait=0.5)
            self.press(Direction.UP, wait=0.5)
            self.press(Direction.UP, wait=0.5)
            # （念のため）逃がすが選べているか
            if not self.isContainTemplate(self.PATH_BOX_MENU_NIGASU):
                self.press(Button.B, wait=0.8)
                print("[box_pkmn_release]ERROR：にがすの選択に失敗")
                return False
            self.press(Button.A, wait=0.8)
            self.press(Direction.UP, wait=0.3)
            # （念のため）はいが選べているか
            if not self.isContainTemplate(self.PATH_BOX_COMMAND_YES):
                self.press(Button.B, wait=0.8)
                print("[box_pkmn_release]ERROR：はいの選択に失敗")
                return False
            # リトライ上限・メッセージ送り
            for _ in range(0, 5):
                if not self.isContainTemplate(self.PATH_BOX_STATUS_LEVEL, crop=self.CROPAREA_BOX_LV):
                    break
                self.press(Button.A, wait=0.5)
            else:
                print("[box_pkmn_release]ERROR：メッセージ送りに失敗")
                return False
            self.press(Button.A, wait=0.5)
            return True
        else:
            print("[box_pkmn_release]SKIP：ポケモンがいないためスキップ")
            return True

    def box_pkmn_put_next(self) -> bool:
        """
        次以降のボックスの空きセルにポケモンを移動する
        【前提】動かしたいポケモンにカーソルがある状態から

        Returns
        -------
        bool
            成否
        """
        print("[box_pkmn_put_next]ポケモンを掴む")
        # initialize
        count_move_box = 0
        # リトライ上限
        for _ in range(0, 3):
            # ポケモンをつかむ
            self.press(Button.Y, wait=0.5)
            # （念のため）つかんでいる状態か
            if self.isContainTemplate(
                    self.PATH_BOX_UNDERCOMANDMENU_CATCHINGPKMN,
                    crop=self.CROPAREA_BOX_UNDERCOMMANDMENU,
                    threshold=0.8):
                break
        # 空きセルを探しやすいよう位置を仮移動
        self.box_cursor_move(row=1, column=0)
        # 最大31ボックス分確認
        for _ in range(0, 31):
            # 次のボックスへ
            self.press(Button.R, wait=1.8)
            count_move_box += 1
            # 空いているセルを探す
            row, column = self.box_cell_find_posirion(path=self.PATH_BOX_NULL_CELL)
            if row is None:
                print("[box_pkmn_put_next]ボックスに空き無し")
                continue
            # 空いているセルへポケモンを移動
            print("[box_pkmn_put_next]ポケモンを移動")
            self.box_cursor_move(row, column)
            self.wait(1)
            self.press(Button.Y, wait=0.5)
            break
        else:
            print("[box_pkmn_put_next]ERROR：ポケモンの移動に失敗しました")
            self.press(Button.B, wait=0.5)
            return False
        # ボックスをもとの位置に戻す
        self.pressRep(Button.L, count_move_box, interval=0.1)
        return True

    def box_hatched_check(self, release_flag=False, statuscheck_flag=False) :
        """
        色違い・良個体値のポケモンをチェック
        【前提】BOXを開いた状態から

        Parameters
        ----------
        release_flag : bool, optional
            Releaseフラグを立てるかどうか（デフォルトはFalse）
        statuscheck_flag : bool, optional
            ステータスチェックを行うかどうか（デフォルトはFalse）
            Trueの場合、色違いのポケモンはReleaseしない

        Returns
        -------
        int
            色違い数
        int
            ステータス一致数
        """
        print("[box_hatched_check]たまごボックス内の色/良個体を確認")
        print(f"逃がし処理:{release_flag} / 個体値チェック: {statuscheck_flag}")
        BOXNUM = [[1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6], [6, 5, 4, 3, 2, 1], [1, 2, 3, 4, 5, 6]]

        while True:
            # ボックスを開く
            self.box_open()
            # 「たまご」ボックスへ移動
            self.box_box_move_target(self.PATH_BOX_NAME_EGG, left_flag=False)
            # initialize
            shiny_count = 0
            statusmatch_count = 0

            # 1行目から順に処理
            for row in range(len(BOXNUM)):

                # 1列目から順に処理
                for column in range(len(BOXNUM[row])):
                    # (試行回数5回)
                    for _ in range(0,5):
                        if not self.box_cursor_move(row=row+1, column=BOXNUM[row][column]):
                            # retry
                            print("[box_hatched_check]ERROR：カーソル移動に失敗")
                            self.field_return()
                            self.box_open()
                            self.box_cursor_move(row=row+1, column=BOXNUM[row][column])
                            continue
                        # ポケモンがいるセルの場合
                        if self.isContainTemplate(self.PATH_BOX_STATUS_LEVEL, crop=self.CROPAREA_BOX_LV):
                            # 色違いか
                            if self.isContainTemplate(self.PATH_BOX_STATUS_SHINY, crop=self.CROPAREA_BOX_STATUS):
                                shiny_count += 1
                                print(f"★ 色違いが生まれました！ {shiny_count}/{self.max_shiny}")
                                self.box_pkmn_put_next()  # 次のボックスにポケモンを移動する
                            # ステータスチェックをする場合
                            elif statuscheck_flag and self.box_hatched_status_check(status=self.status):
                                # statusmatch
                                statusmatch_count += 1
                                print(f"★ 指定個体値が生まれました！ {statusmatch_count}")
                                self.box_pkmn_put_next()  # 次のボックスにポケモンを移動する
                            # 逃がし処理Trueの時
                            elif release_flag:
                                if not self.box_pkmn_release():
                                    # retry
                                    print("[box_hatched_check]ERROR：逃がし失敗")
                                    self.field_return()
                                    self.box_open()
                                    continue
                        if column < len(BOXNUM[row])-1:
                            if row%2==0:
                                self.press(Direction.RIGHT, duration=0.04)
                            else:
                                self.press(Direction.LEFT, duration=0.04)
                        break
                    else:
                        print("[box_hatched_check]ERROR：試行回数上限")
                        self.finish()
                self.press(Direction.DOWN, duration=0.04)

            # ボックスを閉じる
            self.field_return()
            # 色違い数を返す
            return shiny_count, statusmatch_count

    def box_hatched_status_check(self, status=[[31, 31, 31, 31, 31, 31]]) -> bool:
        """
        セルにいるポケモンが色違い/任意ステータスか確認する
        【前提】対象のポケモンにカーソルをあてた状態から

        Returns
        -------
        bool
            ステータス一致有無
        """

        status_flag = False
        result_status = [-1,-1,-1,-1,-1,-1]

        # モード変更
        while not self.isContainTemplate(self.PATH_BOX_UNDERCOMANDMENU_JUDGEMODE,crop=self.CROPAREA_BOX_UNDERCOMMANDMENU):
            self.press(Button.PLUS, wait=0.5)

        # 「さいこう」の検索
        _,result_boxes=self.isContainTemplateCount(self.PATH_BOX_STATUS_31, crop=self.CROPAREA_BOX_STATUS)
        if result_boxes != []:
            for box in result_boxes:
                x1, y1, x2, y2 = box  # 各ボックスの座標を取得
                if x1 < 950 :
                    if y1 < 250 :
                        result_status[3] = 31
                        # print("C")
                    else:
                        result_status[4] = 31
                        # print("D")
                elif x1 < 1100:
                    if y1 < 250:
                        result_status[0] = 31
                        # print("H")
                    else:
                        result_status[5] = 31
                        # print("S")
                else:
                    if y1 < 250:
                        result_status[1] = 31
                        # print("A")
                    else:
                        result_status[2] = 31
                        # print("B")
        # 「ダメかも」の検索
        _, result_boxes = self.isContainTemplateCount(self.PATH_BOX_STATUS_0, crop=self.CROPAREA_BOX_STATUS)
        if result_boxes != []:
            for box in result_boxes:
                x1, y1, x2, y2 = box  # 各ボックスの座標を取得
                if x1 < 950:
                    if y1 < 250:
                        result_status[3] = 0
                        # print("C")
                    else:
                        result_status[4] = 0
                        # print("D")
                elif x1 < 1100:
                    if y1 < 250:
                        result_status[0] = 0
                        # print("H")
                    else:
                        result_status[5] = 0
                        # print("S")
                else:
                    if y1 < 250:
                        result_status[1] = 0
                        # print("A")
                    else:
                        result_status[2] = 0
                        # print("B")

        # 引数個体値との一致数の確認
        for target_status in status:
            count = 0
            for i in range(0, 6):
                if target_status[i] < 0 or target_status[i] == result_status[i]:
                    count = count+1
            if count >= 6:
                print(f"ステータス一致:{result_status}")
                return True

        return False


    def picnic_sandwich_make(self, recipe_path, repeatcount_max=30) -> bool:
        """
        サンドイッチを作って食べる
        【前提】テーブルに向かった状態で、レシピが具材1つだけのもの
        【戻り値】bool
            True:指定レシピで作成・パワーの発動ができた時
            False:エラーがあった時

        Parameters
        ----------
        recipe_path : str
            使用したいレシピ名画像のパスを渡す
        repeatcount_max : int
            レシピの検索上限を渡す（レシピを行き過ぎてしまったときに早めにやり直すための上限）

        Returns
        -------
        bool
            成否
        """

        print("[picnic_sandwich_make]START")
        save_debug_img = False
        GUZAI_AREA_TOP_LOWER = 70
        GUZAI_AREA_TOP_UPPER = 100
        GUZAI_AREA_LEFT_LOWER = 560
        GUZAI_AREA_LEFT_UPPER = 630
        PAN_AREA_TOP_LOWER = 295
        PAN_AREA_TOP_UPPER = 320

        # レシピを見つけるまで繰り返す
        # リトライ上限
        for _ in range(0, 3):
            # 料理開始
            self.press(Button.A, wait=1)
            self.press(Button.A, wait=6)
            count, result_boxes = self.isContainTemplateCount(self.PATH_PICNIC_SANDWITCH_MENU_TITLE, use_gray=False, use_edge=True)
            if count > 0:
                break
        else:
            print("[picnic_sandwich_make]ERROR：レシピ画面が認識できませんでした")
            return False
        # リトライ上限
        for _ in range(0, repeatcount_max):
            self.press(Direction.RIGHT, wait=0.4)
            if self.isContainTemplate(recipe_path, threshold=0.8):  # 違う名前のものを選択してしまいやすいので注意
                break
        else:
            print("[picnic_sandwich_make]ERROR：レシピ名の画像が認識できませんでした")
            print("[picnic_sandwich_make]ERROR：レシピの材料が不足している可能性があります")
            return False

        # レシピを決定
        print("[picnic_sandwich_make]レシピ決定")
        self.pressRep(Button.A, repeat=2, interval=0.3)

        # 調理画面に移動できたか確認
        # リトライ上限
        for _ in range(0, 20):
            self.wait(1)
            if self.isContainTemplate(self.PATH_PICNIC_SANDWITCH_COOKING_TIMER):
                break
        else:
            print("[picnic_sandwich_make]ERROR：調理開始後の画面の画像認識失敗")
            print("[picnic_sandwich_make]ERROR：レシピの材料が不足している可能性があります")
            return False

        # 3回具材を置く
        for put_count in range(0, 3):
            # 具材まで移動
            print("[picnic_sandwich_make]具材移動開始")
            self.press(Direction.UP, duration=1)
            self.press(Direction(Stick.LEFT, -90, 0.4), duration=0.5, wait=0.2)  # 下方向
            # リトライ上限30回
            for _ in range(0, 30):
                # カーソル位置微調整
                _, result_boxes = self.isContainTemplateCount(self.PATH_PICNIC_SANDWITCH_COOKING_HAND, use_edge=True, save_debug_img=save_debug_img)
                if result_boxes == []:
                    print("[picnic_sandwich_make]ERROR：カーソル画像の認識失敗")
                    self.press(Direction(Stick.LEFT, -90, 0.2), duration=0.2, wait=0.2)
                    save_debug_img = True
                if result_boxes == []:
                    continue
                left= result_boxes[0][0]
                top = result_boxes[0][1]
                if top < GUZAI_AREA_TOP_LOWER:
                    self.press(Direction(Stick.LEFT, -90, 0.2), duration=0.2, wait=0.2)
                elif top > GUZAI_AREA_TOP_UPPER:
                    self.press(Direction(Stick.LEFT, 90, 0.2), duration=0.2, wait=0.2)
                elif left < GUZAI_AREA_LEFT_LOWER:
                    self.press(Direction(Stick.LEFT, 0, 0.2), duration=0.2, wait=0.2)
                elif left > GUZAI_AREA_LEFT_UPPER:
                    self.press(Direction(Stick.LEFT, 180, 0.2), duration=0.2, wait=0.2)
                else:
                    break
                self.wait(0.3)
            else:
                print("[picnic_sandwich_make]ERROR：リトライ上限に達しました")
                print("[picnic_sandwich_make]ERROR：具材までのカーソル移動に失敗しました")
            # 具材を掴む
            self.hold(Button.A)
            # パンまで移動
            self.press(Direction.DOWN, duration=1)
            self.press(Direction(Stick.LEFT, 90, 0.4), duration=0.6, wait=0.2)  # 上方向
            # リトライ上限30回
            for _ in range(0, 30):
                # カーソル位置微調整
                _, result_boxes = self.isContainTemplateCount(self.PATH_PICNIC_SANDWITCH_COOKING_HAND, use_edge=True, save_debug_img=save_debug_img)
                if result_boxes == []:
                    print("[picnic_sandwich_make]ERROR：カーソル画像の認識失敗")
                    self.press(Direction(Stick.LEFT, -90, 0.2), duration=0.2, wait=0.2)
                    save_debug_img = True
                    continue
                top = result_boxes[0][1]
                if top > PAN_AREA_TOP_UPPER:
                    self.press(Direction(Stick.LEFT, 90, 0.2), duration=0.2, wait=0.2)
                elif top < PAN_AREA_TOP_LOWER:
                    self.press(Direction(Stick.LEFT, -90, 0.2), duration=0.2, wait=0.2)
                else:
                    break
                self.wait(0.3)
            else:
                print("[picnic_sandwich_make]ERROR：リトライ上限に達しました")
                print("[picnic_sandwich_make]ERROR：パンまでのカーソル移動に失敗しました")
            # カーソルを左右に移動
            if put_count == 1:
                self.press(Direction.LEFT, duration=0.25, wait=0.3)
            elif put_count == 2:
                self.press(Direction.RIGHT, duration=0.25, wait=0.3)
            # 具材を離す
            self.holdEnd(Button.A)
            # カーソルを左右に移動
            if put_count == 1:
                self.press(Direction.RIGHT, duration=0.25, wait=0.3)
            elif put_count == 2:
                self.press(Direction.LEFT, duration=0.25, wait=0.3)

        # サンドイッチ作成画面が終了するまでA連打（上限60回）
        print("[picnic_sandwich_make]料理終了までA連打")
        for _ in range(0, 60):
            self.press(Button.A, wait=2)
            if self.isContainTemplate(self.PATH_PICNIC_COMMAND_YPUSH):
                print("[picnic_sandwich_make]サンドイッチ作成画面認識終了")
                break
        else:
            print("[picnic_sandwich_make]ERROR：サンドイッチ作成画面終了待ちタイムアウト")
            return False

        print("[picnic_sandwich_make]料理を終了")
        return True


    def picnic_basket_check(self, egg=30) -> bool:
        """
        バスケット内のタマゴをチェック
        【前提】バスケットに向いた状態
        【戻り値】bool
            True:指定数タマゴを取得できた時 ※たまに指定数以下になる時があります
            False:タマゴが見つからなかった時

        Parameters
        ----------
        egg : int
            取得したいタマゴ数を設定すると、その数分バスケットからタマゴを取得する
        """
        print(f"[picnic_basket_check]START 取得予定タマゴ数{egg}")

        egg_count = 0
        timeout_count = 0

        # バスケットをチェック
        self.press(Button.A, wait=1)
        if not self.isContainTemplate(self.PATH_PICNIC_MESSAGE_BASKET_CHECK, crop=self.CROPAREA_MASSAGE):
            print("[picnic_basket_check]ERROR：バスケットメッセージ画像の確認に失敗")
            print("バスケットへの移動に失敗した可能性があります")
            return False

        # 指定数取得するまで繰り返す
        while True:
            # タイムアウト
            if timeout_count > 10:
                print("[picnic_basket_check]ERROR：タマゴの確認失敗")
                print("親が不適切な可能性があります")
                return False
            # ウィンドウ表示があればBでメッセージ送り
            if self.isContainTemplate(self.PATH_MESSAGE_WINDOW, crop=self.CROPAREA_MASSAGE):
                self.press(Button.B, wait=1)
            # タマゴ寄贈メッセージがあれば「はい」
            elif self.isContainTemplate(self.PATH_PICNIC_MESSAGE_BASKET_EGG_SEND, crop=self.CROPAREA_MASSAGE):
                self.press(Button.A, wait=1)
                print(f"[picnic_basket_check]タマゴ取得をキャンセル")
            # タマゴ取得メッセージがあれば「はい」
            elif self.isContainTemplate(self.PATH_PICNIC_MESSAGE_BASKET_EGG_GET, crop=self.CROPAREA_MASSAGE):
                if egg_count < egg:
                    self.press(Button.A, wait=1)
                    egg_count += 1
                    timeout_count = 0
                    print(f"[picnic_basket_check]タマゴ取得数 {egg_count}/{egg}")
                else:
                    self.press(Button.B, wait=1)
            # ウィンドウ表示もメッセージ表示もない場合
            elif egg_count >= egg:
                return True
            else:
                print("[picnic_basket_check]WAIT：30秒待機")
                timeout_count += 1
                self.wait(30)
                self.press(Button.A, wait=1)


    def changeparty_parent_pull(self) ->  bool:
        """
        手持ちを親ポケモンに変更する

        BOXを開いた状態から実行、"きじゅん"box内に親ポケモンを配置しておくこと
        隣のたまごボックスを表示したあとフィールドに戻る

        Returns
        -------
        bool
            成否
        """

        print(f"[changeparty_parent_pull]手持ちを親ポケモンに変更する")

        # ボックスを開く
        self.box_open()

        # 手持ちが1匹か確認
        if 1 == self.box_party_count():
            pass
        else:
            # プログラム終了
            print(f"[changeparty_parent_pull]ERROR：開始時の手持ちが孵化要員1体でないため継続不可")
            self.finish()
        # "きじゅん"ボックスを開く
        self.box_box_move_target(self.PATH_BOX_NAME_BASE,left_flag=True)
        # 手持ちの移動
        print(f"[changeparty_parent_pull]手持ちの1番目にカーソルを移動")
        self.box_cursor_move(row=1, column=0)
        print(f"[changeparty_parent_pull]手持ちの先頭を、ボックス左上のポケモンと交換")
        self.press(Button.Y, wait=0.3)  # pull
        self.box_cursor_move(row=1, column=1)
        self.press(Button.Y, wait=0.3)  # put
        self.box_cursor_move(row=1, column=2)
        print(f"[changeparty_parent_pull]ボックス2列目1~5行目をまとめて移動")
        self.box_pressbutton_minus()
        self.press(Direction.DOWN, duration=0.6, wait=0.3)
        self.press(Button.A, wait=0.5)  # pull
        self.box_cursor_move(row=2, column=0)
        self.press(Button.A, wait=0.5)  # put
        # 移動終了、ボックス位置を戻す
        print(f"[changeparty_parent_pull]Rでたまごボックスへ移動")
        self.press(Button.R, wait=0.3)
        # 念のため「たまご」ボックスを確認
        self.box_box_move_target(self.PATH_BOX_NAME_EGG,left_flag=False)

        print(f"[changeparty_parent_pull]手持ちが1匹でないか確認")
        if 1 == self.box_party_count():
            # 手持ちが1匹の場合Falseを返す
            print(f"[changeparty_parent_pull]ERROR：親を手持ちに移動できませんでした")
            print("※頻発する場合は画像の差し替え、閾値調整を行ってください")
            return False
        else:
            # ボックスを閉じる
            self.field_return()
            return True

    def changeparty_parent_put(self) -> bool:
        """
        手持ちをタマゴ孵化用ポケモンに変更し、隣のタマゴ用ボックスを表示して終了する
        【前提】BOXを開いた状態から実行、"きじゅん"box内に孵化用ポケモンを配置しておく

        Returns
        -------
        bool
            成否
        """
        print("[changeparty_parent_put]手持ちを孵化要員に変更")
        # ボックスを開く
        self.box_open()
        # 「きじゅん」ボックスまで移動する
        self.box_box_move_target(self.PATH_BOX_NAME_BASE,left_flag=True)

        # 手持ちを孵化要員に変更
        self.box_cursor_move(row=1, column=1)
        self.press(Button.Y, wait=0.3)  # pull
        self.box_cursor_move(row=1, column=0)
        self.press(Button.Y, wait=0.3)  # put
        self.box_cursor_move(row=2, column=0)
        # 手持ちの2体目以降をまとめて交換
        self.box_pressbutton_minus()
        self.press(Direction.DOWN, duration=0.6, wait=0.3)
        self.press(Button.A, wait=0.5)
        self.box_cursor_move(row=1, column=2)
        self.press(Button.A, wait=0.5)
        # Rを押下して隣の「たまご」ボックスへ移動
        self.press(Button.R, wait=0.3)
        # 念のため「たまご」ボックスの名称を確認
        self.box_box_move_target(self.PATH_BOX_NAME_EGG,left_flag=False)
        # 手持ちが1匹か確認
        # ボックス操作は失敗しやすいので念のため実施
        if 1 == self.box_party_count():
            return True
        # 手持ちが1匹でない場合Falseを返す
        print("[changeparty_parent_put]ERROR：孵化要員の手持ち移動失敗")
        print("[changeparty_parent_put]END")
        return False

    def changeparty_egg_pull(self) -> int:
        """
        タマゴを手持ちに移動
        【前提】ボックスを開いた状態から実行、"たまご"box内にタマゴを配置しておく

        Returns
        -------
        int
            手持ち内タマゴ数
        """
        print("[changeparty_egg_pull]START")
        # 手持ちのタマゴ数
        partyEggs = 0

        # リトライ上限
        for _ in range(0,10):
            # ボックスを開いた状態であることを確認
            self.box_open()
            # 手持ちにタマゴがあるか確認する
            partyEggs, _ = self.isContainTemplateCount(
                template_path=self.PATH_BOX_EGG,
                use_gray=False,
                use_edge=True,
                threshold=0.7,
                crop=self.CROPAREA_BOX_PARTYPKMN)
            if partyEggs > 0:
                print(f"[changeparty_egg_pull]END:手持ちにタマゴがあるため終了 {partyEggs}")
                return partyEggs
            # 「たまご」ボックスへ移動
            self.box_box_move_target(self.PATH_BOX_NAME_EGG,left_flag=False)
            # エッジ比較で空き数を検出・カウント
            row, column = self.box_cell_find_posirion(path=self.PATH_BOX_EGG,threshold=0.65)
            if row is None:
                print("[changeparty_egg_pull]SKIP:ボックスにタマゴがないため終了")
                print("[changeparty_egg_pull]END")
                return 0
            # タマゴの列までカーソルを移動し列を選択
            print("[changeparty_egg_pull]タマゴがあるため移動処理開始")
            if not (self.box_cursor_move(row=1, column=column) and self.box_pressbutton_minus()):
                # リトライ
                print("[changeparty_egg_pull]RETRY:ボックスを開きなおす")
                self.field_return()
                continue
            # 列を選択・手持ち列まで移動・手持ちに置く
            self.press(Direction.DOWN, duration=1, wait=0.3)
            self.press(Button.A, wait=0.5)
            self.box_cursor_move(row=2, column=0)
            self.press(Button.A, wait=0.6)
            self.press(Direction.UP, duration=1, wait=0.5)
        else:
            print("[changeparty_egg_pull]ERROR：リトライ上限に達しました")
            self.camera.saveCapture()
            self.finish()


    def changeparty_hatchedeggs_put(self) -> bool:
        """
        孵化したポケモンをBOXに移動

        Returns
        -------
        bool
            成否
        """
        print("[changeparty_hatchedeggs_put]START")

        # 次のボックスに移動したかを確認するカウンタ
        count_move_box = 0

        # リトライ上限
        for _ in range(0, 10):

            # ボックスを開く
            self.box_open()

            # 手持ちが1体か確認（ボックス操作は失敗しやすいので念のため実施）
            if 1 == self.box_party_count():
                print("[changeparty_hatchedeggs_put]手持ちが1体になったため終了")
                # ボックスを移動した場合戻る
                self.pressRep(Button.L, count_move_box, interval=0.1)
                # 次処理用にボックス名が見える位置にカーソルを移動
                self.box_cursor_move(row=1, column=0)
                self.wait(1)
                return True

            # 「たまご」ボックスへ移動（ボックス操作は失敗しやすいので念のため実施）
            self.box_box_move_target(self.PATH_BOX_NAME_EGG,left_flag=False)

            # 移動先のボックス空き列を探す、成功するまで繰り返す
            for _ in range(0, 10):
                row, column = self.box_cell_find_posirion(path=self.PATH_BOX_NULL_COLUMN)
                if row is None:
                    print("[changeparty_hatchedeggs_put]空き列の画像が認識できませんでした")
                    print("[changeparty_hatchedeggs_put]隣のボックスへ移動します")
                    self.press(Button.R, wait=0.8)
                    count_move_box += 1
                else:
                    print(f"[changeparty_hatchedeggs_put]{column}列目へポケモンを移動します")
                    break
            else:
                print("[changeparty_hatchedeggs_put]RETRY:空き列が見つからなかったため開きなおします")
                self.field_return()
                continue

            # 手持ちの2体目～6体目を範囲選択する
            self.box_cursor_move(row=2, column=0)
            self.box_pressbutton_minus()
            self.press(Direction.DOWN, duration=1,wait=0.3)  # 一番下まで移動
            self.press(Button.A, wait=0.5)  # pull
            self.box_cursor_move(row=1, column=column)
            self.press(Button.A, wait=0.3)  # put

        else:
            print("[changeparty_egg_pull]ERROR：リトライ上限に達しました")
            self.finish()

    def reset_position_zerogate(self) -> bool:
        """開始位置の初期化

        そらをとんでゼロゲート前に移動

        Returns
        -------
        bool
            成否

        """
        print("[reset_position_zerogate]ゼロゲート前に移動")
        # 変数設定
        ANGLE_LEFTSTICK = [0, 60, 120, 180, -120, -60, 0]   # 左スティック方向 0=右、180=左、-90=下、90=上

        # フィールド表示であることを確認
        self.field_return()

        # Yメニューを開く
        for _ in range(20):
            self.press(Button.Y, wait=2)
            if self.isContainTemplate(self.PATH_YMENU_MAP):
                break
        else:
            print("[reset_position_zerogate]ERROR：Yメニューの画像認識失敗")
            return False

        # カーソル移動してAボタン
        for angle_count in ANGLE_LEFTSTICK:
            self.press(Button.PLUS)
            self.press(Direction(Stick.LEFT, angle_count, 0.2), duration=0.2)
            self.wait(0.5)
            self.press(Button.A, wait=0.5)
            if self.isContainTemplate(self.PATH_YMENU_SORAWOTOBU):
                break
            else:
                # +を押下してカーソル位置を初期化
                self.press(Button.B, wait=0.5)
        else:
            print("[reset_position_zerogate]ERROR：空を飛ぶコマンドの画像認識失敗")
            return False

        # Yメニューが消えるまでA押下
        for _ in range(10):
            if not self.isContainTemplate(self.PATH_YMENU_MAP):
                break
            else:
                self.press(Button.A, wait=1)
        else:
            print("[reset_position_zerogate]ERROR：Yメニュークローズ失敗")
            return False
        # プレイヤーの向きを初期化

        print("[reset_position_zerogate]プレイヤー位置初期化")
        self.wait(5)
        self.press(Button.L, wait=1.5)
        # 歩いて移動
        self.press(Direction(Stick.LEFT, 60), duration=3.5, wait=0.5)
        return True