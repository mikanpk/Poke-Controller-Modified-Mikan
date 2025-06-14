#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import ImageProcPythonCommand, _get_template_filespec
import cv2
import numpy as np
import time
import random
import os as os


def non_max_suppression(boxes, scores, overlap_thresh=0, sort_by_distance=True):
    """
    Non Maximum Suppression (NMS) を行う。
    画像認識などで複数の矩形（バウンディングボックス）が検出されたとき、
    重なりが大きいものをまとめて、最もスコアの高いものだけを残す処理です。
    例えば、同じ物体を複数回検出してしまった場合に、
    1つだけに絞り込むために使います。

    Parameters
    ----------
    boxes : numpy array of shape (N, 4)
        検出された矩形群（各矩形は [x1, y1, x2, y2] の形式）
    scores : numpy array of shape (N,)
        各矩形のスコア（信頼度や類似度など）
    overlap_thresh : float, default=0
        重なりの閾値（0～1）。この値より重なりが大きい場合、スコアの低い方を除去します。
    sort_by_distance : bool, default=True
        Trueなら座標 (0,0) に近い順にソート、Falseならスコアの高い順（降順）にソート

    Returns
    -------
    numpy array of shape (M, 4)
        NMS 後に残った矩形群（整数型）
    """
    # 入力のboxesをfloat型に変換して計算しやすくする
    boxes = boxes.astype("float")

    # 矩形が1件以下の場合は、そのまま返す（必ず2次元の形状にする）
    if boxes.shape[0] <= 1:
        return boxes.astype("int")

    # boxesをx1, y1, x2, y2に分割
    # np.splitは(N, 1)の配列を返すので、np.squeezeで(N,)に変換
    x1, y1, x2, y2 = np.squeeze(np.split(boxes, 4, axis=1))

    # 各矩形の面積を計算
    area = (x2 - x1 + 1) * (y2 - y1 + 1)

    # スコアで昇順ソート（最後の要素が最もスコアが高い）
    indices = np.argsort(scores)
    selected = []  # NMSで選択された矩形のインデックス

    # indicesがなくなるまでループ
    while len(indices) > 0:
        last = len(indices) - 1
        selected_index = indices[last]
        selected.append(selected_index)
        remaining_indices = indices[:last]

        # 選択された矩形と残りの矩形との重なり部分の座標を計算
        i_x1 = np.maximum(x1[selected_index], x1[remaining_indices])
        i_y1 = np.maximum(y1[selected_index], y1[remaining_indices])
        i_x2 = np.minimum(x2[selected_index], x2[remaining_indices])
        i_y2 = np.minimum(y2[selected_index], y2[remaining_indices])

        # 重なり部分の幅と高さ（負の値にならないように0でクリップ）
        i_w = np.maximum(0, i_x2 - i_x1 + 1)
        i_h = np.maximum(0, i_y2 - i_y1 + 1)

        # 重なり率（IoUではなく、残り矩形の面積に対する割合）を計算
        overlap = (i_w * i_h) / area[remaining_indices]

        # 重なり率が閾値を超える矩形のインデックスを削除
        indices = np.delete(
            indices, np.concatenate(([last], np.where(overlap > overlap_thresh)[0]))
        )

    # 選択された矩形情報を取得
    selected_boxes = boxes[selected].astype("int")
    selected_scores = scores[selected]

    # フラグに応じてソート
    if sort_by_distance:
        # 座標(0,0)からの距離でソート
        distances = np.sqrt(selected_boxes[:, 0]**2 + selected_boxes[:, 1]**2)
        sorted_indices = np.argsort(distances)
        return selected_boxes[sorted_indices]
    else:
        # スコアの高い順（降順）にソート
        sorted_indices = np.argsort(selected_scores)[::-1]
        return selected_boxes[sorted_indices]

def create_hue_mask(hsv, hue, salute, value, tolerance=30):
    """
    色マスク作成関数
    指定したHSV値（色相・彩度・明度）と許容幅（tolerance）に基づき、
    画像から特定の色だけを抽出するためのマスク画像を作ります。
    例えば「赤っぽい部分だけを抽出したい」などの用途で使います。
    HSV色空間は色相(Hue)・彩度(Saturation)・明度(Value)で色を表現します。

    Parameters
    ----------
    hsv : numpy.ndarray
        入力のHSV画像（cv2.cvtColor()などで変換済み）
    hue : int or float
        中心となる色相値（0～255の整数）
    salute : int
        中心となる彩度（0～255の整数）
    value  : int
        中心となる明度（0～255の整数）
    tolerance : int
        許容幅（±の範囲、例:30）

    Returns
    -------
    mask : numpy.ndarray
        指定色の範囲だけが255（白）、それ以外が0（黒）のマスク画像。
        赤色など色相が0付近でラップする場合は2つの範囲を合成します。
    """
    # HSVでの下限値・上限値を計算
    lower_hue = hue - tolerance
    upper_hue = hue + tolerance
    s_range = [max(salute-tolerance, 0), min(salute+tolerance, 255)]
    v_range = [max(value-tolerance, 0), min(value+tolerance, 255)]
    # 色相が0未満や255超えの場合はラップ（赤色など）
    if lower_hue < 0:
        # 例: hue=10, tolerance=30 → lower_hue=-20, upper_hue=40
        # マスク1 : 上側 ( 256-20～255 )
        mask1 = cv2.inRange(hsv,
                            (256 + lower_hue, s_range[0], v_range[0]),
                            (255, s_range[1], v_range[1]))
        # マスク2 : 下側 ( 0～40 )
        mask2 = cv2.inRange(hsv,
                            (0, s_range[0], v_range[0]),
                            (upper_hue, s_range[1], v_range[1]))
        mask = cv2.bitwise_or(mask1, mask2)
    elif upper_hue > 255:
        # 例: hue=250, tolerance=30 → lower_hue=220, upper_hue=280
        # マスク1 : 下側 ( 220～255 )
        mask1 = cv2.inRange(hsv,
                            (lower_hue, s_range[0], v_range[0]),
                            (255, s_range[1], v_range[1]))
        # マスク2 : 上側 ( 0～(280-256)=24 )
        mask2 = cv2.inRange(hsv,
                            (0, s_range[0], v_range[0]),
                            (upper_hue - 256, s_range[1], v_range[1]))
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        # 範囲内なら1つでOK
        mask = cv2.inRange(hsv,
                           (lower_hue, s_range[0], v_range[0]),
                           (upper_hue, s_range[1], v_range[1]))
    return mask

class ImageProcPythonCommandAddin(ImageProcPythonCommand):
    """
    ImageProcPythonCommandの拡張クラス
    画像処理コマンドに複数物体検出やテンプレートマッチングのカウント機能を追加します。
    画像認識の自動化や複数検出、色抽出などを簡単に行うための便利なメソッドを提供します。
    """

    def isContainTemplateCount(
        self,
        template_path,
        threshold=0.7,
        use_gray=True,
        use_edge=False,
        show_value=False,
        show_position=True,
        save_debug_img=False,
        ms=1000,
        crop=[],
        edgeparam=[100, 200],
        mask_path=None,
        sort_by_distance=True
    ) -> any:
        """
        現在のスクリーンショットと指定した画像のテンプレートマッチングを行い、
        閾値以上にマッチした箇所の個数を戻り値とします。
        色の違いを考慮しないのであればパフォーマンスの点からuse_grayをTrueにして
        グレースケール画像を使うことを推奨します。

        Parameters
        ----------
        template_path: str
            テンプレート画像のパス
        threshold: float
            類似度の閾値
        use_gray: bool
            グレースケール化するかどうか
        show_value: bool
            類似度や検出数を表示するか
        show_position: bool
            検出位置をcanvasに表示するか
        show_only_true_rect: bool
            認識できなかった場合の枠表示方法
        ms: float
            枠の表示時間（ミリ秒）
        crop: List[int]
            入力画像のトリミング情報
        mask_path: str
            マスク画像のパス
        sort_by_distance : bool
            結果のソート順を、左上からの座標順にするかどうか

        Returns
        -------
        count: int
            閾値以上にマッチした箇所の個数
        result_boxes: np
            閾値以上にマッチした箇所の座標配列 [x1, y1, x2, y2]
        """

        # 処理結果格納用の配列
        boxes = []
        result_boxes = []
        method = cv2.TM_CCORR_NORMED

        # ゲーム画面の読み取り
        src = self.camera.readFrame()
        src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) if use_gray else src
        # ゲーム画面画像のトリミング
        if len(crop) == 4:
            src = src[crop[1]: crop[3], crop[0]: crop[2]]

        # テンプレート画像の読み取り
        template = cv2.imread(
            _get_template_filespec(template_path),
            cv2.IMREAD_GRAYSCALE if use_gray else cv2.IMREAD_COLOR,
        )
        # テンプレート画像のサイズ取得
        w, h = template.shape[1], template.shape[0]

        # mask画像が引数にある場合、マスク用画像読み込み
        if mask_path == None:
            mask = None
            method = cv2.TM_CCOEFF_NORMED
        else:
            mask = cv2.imread(_get_template_filespec(mask_path), 0)

        # 画像のエッジ処理・エッジ処理時のmethodパラメータの設定
        if use_edge:
            src = cv2.Canny(src, edgeparam[0], edgeparam[1])
            template = cv2.Canny(template, edgeparam[0], edgeparam[1])
            method = cv2.TM_CCORR_NORMED

        # デバッグ用画像を出力
        cv2.imwrite(_get_template_filespec("debug_isContainTemplateCount_template.png"), template)
        cv2.imwrite(_get_template_filespec("debug_isContainTemplateCount.png"), src)

        # マッチング
        res = cv2.matchTemplate(src, template, method, mask)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # マッチング結果が閾値以上の場合
        if max_val >= threshold:
            # 類似度が threshold 以上の位置及びスコアを取得
            positions = np.where(res >= threshold)
            scores = res[positions]
            # canvasに検出位置を表示するための準備
            tag = str(time.perf_counter()) + str(random.random())
            addx = 0
            addy = 0
            # 各要素が (x1, y1, x2, y2) である矩形一覧boxesを作成
            for y, x in zip(*positions):
                boxes.append([x, y, x + w - 1, y + h - 1])
            boxes = non_max_suppression(
                boxes=np.array(boxes),
                scores=scores,
                sort_by_distance=sort_by_distance
                )
            # canvasにトリミング範囲を表示
            if crop != []:
                self.gui.ImgRect(crop[0], crop[1], crop[2], crop[3], outline="orange", tag=tag, ms=ms)
                addx = crop[0]
                addy = crop[1]
            # 検出位置の表示
            for x1, y1, x2, y2 in boxes:
                result_boxes.append([x1+addx, y1+addy, x2+addx, y2+addy])
                if self.gui is not None and show_position:
                    self.gui.ImgRect(x1=x1+addx, y1=y1+addy, x2=x2+addx, y2=y2+addy, outline="sky blue", tag=tag, ms=ms)
        # デバッグ用
        elif save_debug_img:
            self.camera.saveCapture(filename=os.path.basename(template_path))
        # テンプレートマッチングの結果(類似度)を表示
        if show_value:
            print(f"{template_path} value:{max_val:.2f}")
            if max_val >= threshold:
                print(f"matchCount:{len(result_boxes)} x:{result_boxes[0][0]},{result_boxes[0][3]} y:{result_boxes[0][1]},{result_boxes[0][2]}")

        return len(result_boxes),result_boxes

    def isContainTemplateHSV(
        self,
        template_path,
        show_value=False,
        show_position=True,
        show_only_true_rect=True,
        ms=1000,
        crop=[],
        min_stats=300,
        tolerance=20,
        use_blur=True
    ) -> any:

        # 色の許容度 tolerance = 20

        # ゲーム画面の画像取得
        src = self.camera.readFrame()
        # トリミング
        if len(crop) == 4:
            src = src[crop[1]: crop[3], crop[0]: crop[2]]
        # 輝度にのみヒストグラム平坦化を適用
        # BGR => YUV(YCbCr)
        src_yuv = cv2.cvtColor(src, cv2.COLOR_BGR2YUV)
        # claheオブジェクトを生成
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        # 輝度にのみヒストグラム平坦化
        src_yuv[:, :, 0] = clahe.apply(src_yuv[:, :, 0])
        # YUV => BGR
        src_bgr = cv2.cvtColor(src_yuv, cv2.COLOR_YUV2BGR)
        # 平滑化フィルタを適用
        if use_blur:
            # カーネルの縦横(X,Y)のサイズのタプルで処理
            src_bgr = cv2.blur(src_bgr, (5, 5))
        # BGRからHSVに変換
        src_hsv = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2HSV)

        # templateからHSV平均値を取得
        # flattenで一次元化しmeanで平均を取得
        template = cv2.imread(_get_template_filespec(template_path))
        templateHsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        hue = templateHsv.T[0].flatten().mean()
        salute = templateHsv.T[1].flatten().mean()
        value = templateHsv.T[2].flatten().mean()

        # HSV価からマスクを作成
        mask = create_hue_mask(src_hsv, hue=hue, salute=salute, value=value, tolerance=tolerance)

        if show_value:
            print("Hue: %.2f" % (hue))
            print("Salute: %.2f" % (salute))
            print("Value: %.2f" % (value))
        # デバッグ用
        cv2.imwrite(_get_template_filespec("debug_isContainTemplateHSV_mask.png"), mask)

        # 元画像から特定の色を抽出
        masked_img = cv2.bitwise_and(src_bgr, src_bgr, mask=mask)
        # 連結成分でラベリングする
        num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask)
        # 背景のラベルを削除
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        centroids = np.delete(centroids, 0, 0)
        # ラベルの有無で場合分け
        if num_labels >= 1:
            # 最大面積のインデックスを取り出す
            max_index = np.argmax(stats[:, 4])
            # 以下最大面積のラベルについて考える crop[1]: crop[3], crop[0]: crop[2]]
            x = stats[max_index][0]
            y = stats[max_index][1]
            w = stats[max_index][2]
            h = stats[max_index][3]
            s = stats[max_index][4]
            mx = int(centroids[max_index][0])+crop[0]  # 重心のX座標
            my = int(centroids[max_index][1])+crop[1]  # 重心のY座標
            # デバッグ用 結果確認用画像の出力
            cv2.rectangle(masked_img, (x, y), (x+w, y+h), (255, 0, 255))  # ラベルを四角で囲む
            cv2.imwrite(_get_template_filespec("debug_isContainTemplateHSV.png"), masked_img)
            # トリミングがあればその分の値を修正
            if len(crop) == 4:
                x = x+crop[0]
                y = y+crop[1]
            if show_value:
                # 重心を表示
                print("重心:%d,%d 面積:%d x:%d,y:%d,w:%d,h:%d" % (mx, my, s, x, y, w, h))
            # GUIへの出力
            tag = str(time.perf_counter()) + str(random.random())
            if crop != []:
                self.gui.ImgRect(crop[0], crop[1], crop[2], crop[3], outline="orange", tag=tag, ms=ms)
            if show_position:
                tag = str(time.perf_counter()) + str(random.random())
                self.gui.delete("ImageRecRect")
                self.gui.ImgRect(x1=x, y1=y, x2=x+w, y2=y+h, outline="sky blue", tag=tag, ms=ms)
            if self.gui is not None and show_position and not show_only_true_rect:
                self.gui.ImgRect(
                    self.gui.ImgRect(x1=x, y1=y, x2=x+w, y2=y+h, outline="red", tag=tag, ms=ms)
                )
            # 指定色の面積が所定の値以上の場合、目標物を見つけたと判断
            if min_stats < s:
                return [x, y, w, h, mx, my]
            else:
                # 面積を表示
                print("指定の面積未満:%d < %d" % (s, min_stats))
        # ----------------------------------------------
        print("目標物が見当たりません！！")
        return None