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
    複数の検出領域から最適な領域を選択する関数（Non Maximum Suppression）

    同じ物体を複数回検出した場合に、重なり合う検出領域をまとめて
    最も確度の高い検出結果だけを残すための処理を行います。

    Parameters
    ----------
    boxes: numpy array (N, 4)
        検出された矩形の座標情報 [x1, y1, x2, y2]
    scores: numpy array (N,)
        各矩形の検出スコア（確度）
    overlap_thresh: float
        重なり具合の閾値（0～1）。この値より重なりが大きい場合、
        スコアの低い方の矩形を除去します
    sort_by_distance: bool
        True: 座標(0,0)からの距離順にソート
        False: スコアの高い順にソート

    Returns
    -------
    numpy array (M, 4)
        選択された矩形の座標情報のリスト
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
    指定した色の範囲のみを抽出するマスク画像を作成する関数

    HSV色空間（色相・彩度・明度）を使用して、特定の色の範囲だけを
    抽出するためのマスク（白黒画像）を作成します。
    例：赤色の物体だけを検出したい場合などに使用します。

    Parameters
    ----------
    hsv: numpy array
        HSV色空間に変換された入力画像
    hue: int
        抽出したい色の色相値（0～255）
    salute: int
        抽出したい色の彩度値（0～255）
    value: int
        抽出したい色の明度値（0～255）
    tolerance: int
        色の許容範囲（±この値の範囲を許容）

    Returns
    -------
    mask: numpy array
        指定した色範囲が白（255）、それ以外が黒（0）のマスク画像
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
        画面内から特定の画像パターンを検索して、その数と位置を返す関数

        指定した画像（テンプレート）と似た部分を画面内から探し、
        一定以上の類似度を持つ領域の数と座標を返します。
        複数のポケモンや同じアイテムなどを一度に検出する際に使用します。

        Parameters
        ----------
        template_path: str
            探したい画像（テンプレート）のファイルパス
        threshold: float
            検出する類似度の閾値（0.0～1.0）
        use_gray: bool
            グレースケール画像で比較するかどうか（処理速度向上）
        use_edge: bool
            エッジ（輪郭）情報で比較するかどうか
        show_value: bool
            類似度や検出数を表示するかどうか
        show_position: bool
            検出位置を画面上に表示するかどうか
        save_debug_img: bool
            デバッグ用の画像を保存するかどうか
        ms: int
            検出位置の表示時間（ミリ秒）
        crop: list
            画面の検索範囲を制限する場合の座標 [x1, y1, x2, y2]
        edgeparam: list
            エッジ検出時のパラメータ [閾値1, 閾値2]
        mask_path: str
            マスク画像のファイルパス（特定領域のみ検索する場合）
        sort_by_distance: bool
            検出結果を左上からの距離順にソートするかどうか

        Returns
        -------
        tuple (int, list)
            検出された領域の数と、各領域の座標情報のリスト
        """

        # 処理結果格納用の配列を初期化
        boxes = []          # 検出された領域の座標を一時保存
        result_boxes = []   # 最終的な検出結果の座標を保存
        method = cv2.TM_CCORR_NORMED  # テンプレートマッチングの手法を指定

        # 現在の画面をキャプチャして読み込み
        src = self.camera.readFrame()
        # 必要に応じてグレースケール変換
        src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY) if use_gray else src
        # 指定された範囲でトリミング
        if len(crop) == 4:
            src = src[crop[1]: crop[3], crop[0]: crop[2]]

        # 探したい画像（テンプレート）を読み込み
        template = cv2.imread(
            _get_template_filespec(template_path),
            cv2.IMREAD_GRAYSCALE if use_gray else cv2.IMREAD_COLOR,
        )
        # テンプレート画像のサイズを取得
        w, h = template.shape[1], template.shape[0]

        # マスク画像の処理
        if mask_path == None:
            mask = None
            # マスクがない場合は相関係数を使用
            method = cv2.TM_CCOEFF_NORMED
        else:
            # マスク画像を読み込み（グレースケール）
            mask = cv2.imread(_get_template_filespec(mask_path), 0)

        # エッジ検出を使用する場合の処理
        if use_edge:
            # 画面とテンプレート両方にエッジ検出を適用
            src = cv2.Canny(src, edgeparam[0], edgeparam[1])
            template = cv2.Canny(template, edgeparam[0], edgeparam[1])
            method = cv2.TM_CCORR_NORMED  # エッジ用のマッチング手法

        # デバッグ用の画像を保存
        cv2.imwrite(_get_template_filespec("debug_isContainTemplateCount_template.png"), template)
        cv2.imwrite(_get_template_filespec("debug_isContainTemplateCount.png"), src)

        # テンプレートマッチング実行
        res = cv2.matchTemplate(src, template, method, mask)
        # マッチング結果の最小値、最大値、その位置を取得
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # マッチング結果が閾値以上の場合の処理
        if max_val >= threshold:
            # 閾値以上の類似度を持つ位置をすべて取得
            positions = np.where(res >= threshold)
            scores = res[positions]
            # 検出位置表示用の一意なタグを生成
            tag = str(time.perf_counter()) + str(random.random())
            # トリミング補正用の値を初期化
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
        min_stats=300,  # あると判断する色の面積指定
        tolerance=20,  # 色の許容度
        use_blur=True
    ) -> any:
        """
        指定した画像の色情報を使って、画面内から同じ色の領域を検出する関数

        テンプレート画像の平均的な色（HSV値）を計算し、その色に近い
        領域を画面内から探し出します。特定の色のオブジェクトを
        検出したい場合に使用します。

        引数:
        template_path: str
            基準となる画像のファイルパス
        show_value: bool
            HSV値を表示するかどうか
        show_position: bool
            検出位置を画面上に表示するかどうか
        show_only_true_rect: bool
            検出成功時のみ枠を表示するかどうか
        ms: int
            検出位置の表示時間（ミリ秒）
        crop: list
            画面の検索範囲を制限する場合の座標 [x1, y1, x2, y2]
        min_stats: int
            検出と判定する最小の面積（ピクセル数）
        tolerance: int
            色の許容範囲（±この値の範囲を許容）
        use_blur: bool
            ノイズ除去のためのぼかしを適用するかどうか

        戻り値:
        list or None
            検出成功時: [x, y, 幅, 高さ, 重心x, 重心y]
            検出失敗時: None
        """

        # 画面をキャプチャして読み込み
        src = self.camera.readFrame()
        # 指定範囲でトリミング
        if len(crop) == 4:
            src = src[crop[1]: crop[3], crop[0]: crop[2]]

        # 画像の前処理（見やすくするための補正）
        # まずBGRからYUV色空間に変換（輝度と色情報を分離）
        src_yuv = cv2.cvtColor(src, cv2.COLOR_BGR2YUV)
        # 輝度のヒストグラム平坦化用のオブジェクトを作成
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        # 輝度チャンネルのみヒストグラム平坦化を適用（コントラスト改善）
        src_yuv[:, :, 0] = clahe.apply(src_yuv[:, :, 0])
        # YUVからBGRに戻す
        src_bgr = cv2.cvtColor(src_yuv, cv2.COLOR_YUV2BGR)

        # ノイズ除去のためのぼかし処理
        if use_blur:
            # 5x5ピクセルの範囲で平均化
            src_bgr = cv2.blur(src_bgr, (5, 5))

        # 色検出しやすいようにHSV色空間に変換
        src_hsv = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2HSV)

        # 基準となる画像を読み込んでHSV平均値を計算
        template = cv2.imread(_get_template_filespec(template_path))
        templateHsv = cv2.cvtColor(template, cv2.COLOR_BGR2HSV)
        # 各チャンネル（色相、彩度、明度）の平均値を計算
        hue = templateHsv.T[0].flatten().mean()    # 色相（色合い）
        salute = templateHsv.T[1].flatten().mean() # 彩度（鮮やかさ）
        value = templateHsv.T[2].flatten().mean()  # 明度（明るさ）

        # 計算したHSV値を使ってマスク画像を作成
        mask = create_hue_mask(src_hsv, hue=hue, salute=salute, value=value, tolerance=tolerance)

        # HSV値を表示（デバッグ用）
        if show_value:
            print("Hue(色相): %.2f" % (hue))
            print("Salute(彩度): %.2f" % (salute))
            print("Value(明度): %.2f" % (value))
        # マスク画像を保存（デバッグ用）
        cv2.imwrite(_get_template_filespec("debug_isContainTemplateHSV_mask.png"), mask)

        # マスクを使って元画像から特定の色の領域だけを抽出
        masked_img = cv2.bitwise_and(src_bgr, src_bgr, mask=mask)

        # マスク画像内の連結成分を解析（つながっている領域をグループ化）
        num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask)
        # 背景ラベル（最初の要素）を削除
        num_labels = num_labels - 1
        stats = np.delete(stats, 0, 0)
        centroids = np.delete(centroids, 0, 0)

        # 検出された領域が1つ以上ある場合の処理
        if num_labels >= 1:
            # 最大面積を持つ領域のインデックスを取得
            max_index = np.argmax(stats[:, 4])

            # 最大領域の情報を取得
            x = stats[max_index][0]      # 左上のx座標
            y = stats[max_index][1]      # 左上のy座標
            w = stats[max_index][2]      # 幅
            h = stats[max_index][3]      # 高さ
            s = stats[max_index][4]      # 面積（ピクセル数）
            # 重心座標を計算（トリミング補正も加える）
            mx = int(centroids[max_index][0])+crop[0]  # x座標
            my = int(centroids[max_index][1])+crop[1]  # y座標

            # デバッグ用に検出領域を四角で囲んだ画像を保存
            cv2.rectangle(masked_img, (x, y), (x+w, y+h), (255, 0, 255))
            cv2.imwrite(_get_template_filespec("debug_isContainTemplateHSV.png"), masked_img)

            # トリミングされている場合は座標を補正
            if len(crop) == 4:
                x = x+crop[0]
                y = y+crop[1]

            # 検出情報を表示（デバッグ用）
            if show_value:
                print("重心:(x=%d,y=%d) 面積:%d ピクセル" % (mx, my, s))
                print("検出領域: x=%d, y=%d, 幅=%d, 高さ=%d" % (x, y, w, h))
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
        print("目標物が見当たりません！！")
        return None