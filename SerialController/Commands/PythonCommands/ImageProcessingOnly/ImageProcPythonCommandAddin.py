#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from Commands.PythonCommandBase import ImageProcPythonCommand, _get_template_filespec
import cv2
import numpy as np
import time
import random


def non_max_suppression(boxes, scores, overlap_thresh=0):
    """
    Non Maximum Suppression (NMS) を行う。
    検出された矩形群から重複を除去し、最もスコアの高い矩形のみを残します。

    Parameters
    ----------
    boxes: (N, 4) の numpy 配列
        検出された矩形群（x1, y1, x2, y2）
    scores: (N,) の numpy 配列
        各矩形のスコア
    overlap_thresh: float, default=0.9
        重なりの閾値（0～1）

    Returns
    -------
    boxes: (M, 4) の numpy 配列
        NMS後に残った矩形群
    """
    if len(boxes) <= 1:
        return boxes

    # float型に変換
    boxes = boxes.astype("float")

    # (NumBoxes, 4) の numpy 配列を x1, y1, x2, y2 に分割
    x1, y1, x2, y2 = np.squeeze(np.split(boxes, 4, axis=1))

    # 矩形の面積を計算
    area = (x2 - x1 + 1) * (y2 - y1 + 1)

    indices = np.argsort(scores)  # スコアを降順にソートしたインデックス一覧
    selected = []  # NMS により選択されたインデックス一覧

    # indices がなくなるまでループ
    while len(indices) > 0:
        # indices は降順にソートされているので、一番最後の要素の値 (インデックス) が
        # 残っている中で最もスコアが高い
        last = len(indices) - 1

        selected_index = indices[last]
        remaining_indices = indices[:last]
        selected.append(selected_index)

        # 選択した矩形と残りの矩形の共通部分の x1, y1, x2, y2 を計算
        i_x1 = np.maximum(x1[selected_index], x1[remaining_indices])
        i_y1 = np.maximum(y1[selected_index], y1[remaining_indices])
        i_x2 = np.minimum(x2[selected_index], x2[remaining_indices])
        i_y2 = np.minimum(y2[selected_index], y2[remaining_indices])

        # 共通部分の幅・高さを計算（負の場合は0）
        i_w = np.maximum(0, i_x2 - i_x1 + 1)
        i_h = np.maximum(0, i_y2 - i_y1 + 1)

        # Overlap Ratio を計算
        overlap = (i_w * i_h) / area[remaining_indices]

        # Overlap Ratio が閾値以上の矩形を indices から削除
        indices = np.delete(
            indices, np.concatenate(
                ([last], np.where(overlap > overlap_thresh)[0]))
        )

    # 選択された矩形の一覧を返す
    return boxes[selected].astype("int")


class ImageProcPythonCommandAddin(ImageProcPythonCommand):
    """
    ImageProcPythonCommandの拡張クラス
    画像処理コマンドに複数物体検出やテンプレートマッチングのカウント機能を追加します。
    """

    def isContainTemplateCount(
        self,
        template_path,
        threshold=0.7,
        use_gray=True,
        show_value=False,
        show_position=True,
        show_only_true_rect=True,
        ms=2000,
        crop=[],
        mask_path=None,
    ) -> int:
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

        Returns
        -------
        count: int
            閾値以上にマッチした箇所の個数
        """

        src = self.camera.readFrame()
        src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) if use_gray else src
        if len(crop) == 4:
            src = src[crop[1]: crop[3], crop[0]: crop[2]]

        template = cv2.imread(
            _get_template_filespec(template_path),
            cv2.IMREAD_GRAYSCALE if use_gray else cv2.IMREAD_COLOR,
        )

        # mask用画像読み込み
        if mask_path == None:
            mask = None
            method = cv2.TM_CCOEFF_NORMED
        else:
            mask = cv2.imread(_get_template_filespec(mask_path), 0)
            method = cv2.TM_CCORR_NORMED

        w, h = template.shape[1], template.shape[0]
        boxes = []

        # テンプレートマッチングを実行
        res = cv2.matchTemplate(src, template, method, mask)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)

        # マッチング結果が閾値未満の場合は0を返す
        if max_val < threshold:
            print(f"{template_path} value: {max_val}, count: {len(boxes)}")
            return 0

        # マッチング結果の処理
        # 類似度が threshold 以上の位置及びスコアを取得
        positions = np.where(res >= threshold)
        scores = res[positions]
        # 各要素が (x1, y1, x2, y2) である矩形一覧を作成
        for y, x in zip(*positions):
            boxes.append([x, y, x + w - 1, y + h - 1])
        boxes = np.array(boxes)
        boxes = non_max_suppression(boxes=boxes, scores=scores)

        # テンプレートマッチングの結果(類似度)を表示
        if show_value:
            print(f"{template_path} value: {max_val}, count: {len(boxes)}")

        # canvasに検出位置を表示
        tag = str(time.perf_counter()) + str(random.random())
        if boxes.size > 0:
            if self.gui is not None and show_position:
                for x1, y1, x2, y2 in boxes:
                    self.gui.ImgRect(
                        x1=x1, y1=y1, x2=x2, y2=y2, outline="sky blue", tag=tag, ms=ms
                    )
            else:
                pass

        return len(boxes)

    def isContainTemplateHSV(
        self,
        template_path,
        show_value=False,
        show_position=True,
        show_only_true_rect=True,
        ms=2000,
        crop=[],
        min_stats=300,
        use_blur=True
    ) -> any:

        # 色の許容度
        tolerance = 20

        # ゲーム画面の画像取得
        src = self.camera.readFrame()
        # トリミング
        if len(crop) == 4:
            src = src[crop[1]: crop[3], crop[0]: crop[2]]

        # 輝度にのみヒストグラム平坦化
        # RGB => YUV(YCbCr)
        src_yuv = cv2.cvtColor(src, cv2.COLOR_BGR2YUV)
        # claheオブジェクトを生成
        clahe = cv2.createCLAHE(
            clipLimit=2.0, tileGridSize=(8, 8))
        # 輝度にのみヒストグラム平坦化
        src_yuv[:, :, 0] = clahe.apply(src_yuv[:, :, 0])
        # YUV => RGB
        src = cv2.cvtColor(src_yuv, cv2.COLOR_YUV2BGR)
        if use_blur:
            # 平滑化フィルタを適用（カーネルの縦横(X,Y)のサイズのタプル）
            src = cv2.blur(src, (5, 5))
        # BGRからHSVに変換
        src_hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)

        # templateからHSV平均値を取得
        # flattenで一次元化しmeanで平均を取得
        template = cv2.imread(
            _get_template_filespec(template_path))  # 画像を読み込む
        templateHsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)

        hue = templateHsv.T[0].flatten().mean()
        salute = templateHsv.T[1].flatten().mean()
        value = templateHsv.T[2].flatten().mean()

        if show_value:
            print("Hue: %.2f" % (hue))
            print("Salute: %.2f" % (salute))
            print("Value: %.2f" % (value))

        mask = create_hue_mask(src_hsv, hue=hue, salute=salute, value=value, tolerance=tolerance)
        cv2.imwrite(_get_template_filespec("mask.png"), mask)  # 書き出す
        # 元画像から特定の色を抽出
        masked_img = cv2.bitwise_and(src, src, mask=mask)
        # 連結成分でラベリングする
        num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask)
        # 背景のラベルを削除
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        centroids = np.delete(centroids, 0, 0)
        # ラベルの有無で場合分け
        if num_labels >= 1:
            max_index = np.argmax(stats[:, 4])  # 最大面積のインデックスを取り出す
            # 以下最大面積のラベルについて考える crop[1]: crop[3], crop[0]: crop[2]]
            x = stats[max_index][0]
            y = stats[max_index][1]
            w = stats[max_index][2]
            h = stats[max_index][3]
            s = stats[max_index][4]
            mx = int(centroids[max_index][0])+crop[0]  # 重心のX座標
            my = int(centroids[max_index][1])+crop[1]  # 重心のY座標
            # 結果確認用画像の出力
            output_img = masked_img
            cv2.rectangle(output_img, (x, y), (x+w, y+h), (255, 0, 255))  # ラベルを四角で囲む
            cv2.imwrite(_get_template_filespec("debug_isContainTemplateHSV.png"), output_img)  # 書き出す
            # トリミングがあればその分の値を修正
            if len(crop) == 4:
                x = x+crop[0]
                y = y+crop[1]
            print("重心を表示:%d,%d" % (mx, my))  # 重心を表示
            print("面積を表示:%d" % (s))  # 面積を表示
            print("x:%d,y:%d,w:%d,h:%d" % (x, y, w, h))  # 面積を表示
            # GUIへの出力
            if show_position:
                tag = str(time.perf_counter()) + str(random.random())
                self.gui.delete("ImageRecRect")
                self.gui.ImgRect(x1=x, y1=y, x2=x+w, y2=y+h, outline="sky blue", tag=tag, ms=ms)            # 指定色の面積が所定の値以上の場合、目標物を見つけたと判断
            if min_stats < s:
                return [x, y, w, h, mx, my]
            else:
                print("指定の面積未満:%d < %d" % (s, min_stats))  # 面積を表示
        # ----------------------------------------------
        print("目標物が見当たりません！！")
        return None


def create_hue_mask(hsv, hue, salute, value, tolerance=30):
    """色マスク作成
    引数に基づいて、所定の範囲内の色のﾏｽｸを作成する

    Parameters
    ----------
    hsv :any
        入力のHSV画像（cv2.cvtColor()などで変換済み）
    hue :any
        中心となる色相値（0～255の整数）
    salute :int
        中心となる彩度（0～255の整数）
    value  :int
        中心となる明度（0～255の整数）
    tolerance :int
        ±の幅（例：30）

    returns
    -------
    mask  : 赤の場合はラップするため2個の領域を組み合わせたマスク、
            それ以外は1個のマスクを返す
    """

    # HSVでの下限値、上限値は3要素のタプル (H, S, V)

    # 領域計算
    lower_hue = hue - tolerance
    upper_hue = hue + tolerance
    s_range = [max(salute-tolerance, 0), min(salute+tolerance, 255)]
    v_range = [max(value-tolerance, 0), min(value+tolerance, 255)]
    # 入力値が赤で、色相範囲がはみ出す（ラップする）場合
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
