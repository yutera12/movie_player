import os
import subprocess
import json
import shutil
import cv2
import numpy as np
from tqdm import tqdm


def extractDateFromFilename(filename: str):
    """
    ファイル名から日付を返す
    """
    assert filename[:8].isdecimal(), f"ファイル名が{filename}です。ファイル名が日付になっていません。"
    year = int(filename[:4])
    month = int(filename[4:6])
    day = int(filename[6:8])
    yyyymm = int(filename[:6])
    assert (1900 <= year <= 2200) and (1 <= month <= 12) and (1 <= day <= 31), f"日付が{year}年{month}月{day}日"
    return year, month, day, yyyymm


def selectFiles(files: list[str]):
    """
    ファイルリストから画像ファイル一覧と、動画ファイル一覧をそれぞれ返す
    """
    photoFiles = []
    movieFiles = []
    for file in files:
        _, ext = os.path.splitext(file)
        if ext.lower() in [".jpg", ".jpeg", ".png"]:
            photoFiles.append(file)
        elif ext == ".mp4":
            movieFiles.append(file)
        else:
            assert False, f"{file}は、指定の画像ファイルでも動画ファイルでもありません。"
    return photoFiles, movieFiles


def scale(img, px: int):
    """
    アスペクト比を変えずに、画像の縦横のうち長いほうを指定のピクセルにそろえる。
    """
    h, w = img.shape[:2]
    if h > w:
        img = scale_to_height(img, px)
    else:
        img = scale_to_width(img, px)
    return img


def scale_to_width(img, width):
    """
    アスペクト比を変えずに、画像の横を指定のピクセルにそろえる。
    """
    h, w = img.shape[:2]
    height = round(h * (width / w))
    dst = cv2.resize(img, dsize=(width, height))
    return dst


def scale_to_height(img, height):
    """
    アスペクト比を変えずに、画像の縦を指定のピクセルにそろえる。
    """
    h, w = img.shape[:2]
    width = round(w * (height / h))
    dst = cv2.resize(img, dsize=(width, height))
    return dst


def ms2s(time: list[float]):
    """
    例：
    　time = [1, 7]の場合、67が返る
    　1分7秒を67秒に変換している。

    """
    return time[0] * 60 + time[1]


def sec2h(x: float):
    """
    x秒が入力された場合に人に分かりやすい形式で返す。
    例 x = 674の場合、11分14秒という文字列を返す
    例 x = 4000の場合、1時間6分40秒という文字列を返す
    例 x = 600の場合、10分という文字列を返す
    """
    x = int(x)
    h = x // 3600
    r = x % 3600
    m = r // 60
    s = r % 60
    ret = ""
    if h > 0:
        ret += f"{h}時間"
    if m > 0:
        ret += f"{m}分"
    if s > 0:
        ret += f"{s}秒"
    return ret


def yyyymmdd2pos(yyyymmdd, yearList, monthList):
    """
    yyyymmddを入力すると、home画面上部の月のリストのどの位置に相当するかを返す

    例
    yearList : [2020, 2021]
    monthList : [[10, 12], [1, 2]]

    yyyymmdd | return
    -------- | -----
    0        | -1     # 0が入力されたら-1を返す
    20200910 | 0      # 2020/09/10は2000/10の箱（一つ目の箱）よりも前なので0
    20201010 | 0.333  # 2020/10/10は2000/10の箱の中の1/3の位置に相当するので、1/3
    20201110 | 1      # 2020/11/10は2000/10の箱と2020/12の箱の間に相当するので1
    20201210 | 1.333
    20210110 | 2.333
    20210210 | 3.333
    20210310 | -1     # 2021/03/10は最後の箱(2021/2の箱)の外側に相当するので-1
    */
    """
    if yyyymmdd == 0:
        return -1
    yyyymm = int(np.floor(yyyymmdd / 100))
    dd = yyyymmdd - yyyymm * 100
    pos = 0
    for year, month_li in zip(yearList, monthList):
        for month in month_li:
            if year * 100 + month == yyyymm:
                return pos + dd / 30
            elif year * 100 + month > yyyymm:
                return pos
            pos += 1
    return -1


def preprocess_photo(files):
    """
    写真のサムネイル作成と情報（日付、アスペクト比など）の取得
    （処理に時間がかかるので、一度処理した情報は再利用する）
    """

    # サムネイル作成
    info_ret = {}
    if not os.path.exists("images/thumbnails"):
        os.makedirs("images/thumbnails")
    for filename in tqdm(files, desc="photo thumbnail"):
        thumbnail_filename = f"images/thumbnails/{filename}"
        info_ret[filename] = {"thumbnail_filename": thumbnail_filename}
        if os.path.exists(f"images/thumbnails/{filename}"):
            continue    # 処理済みのものはskip
        img = cv2.imread(f"images/images/{filename}")
        img = scale(img, 400)
        cv2.imwrite("images/thumbnails/temp.png", img)  # 日本語ファイル名対策
        shutil.move("images/thumbnails/temp.png", thumbnail_filename)

    # 情報取得
    cache_filename = os.path.join("images", "info_photo_cache.json")
    if os.path.isfile(cache_filename):
        with open(cache_filename, "r", encoding="utf-8") as f:
            info_photo_cache = json.load(f) # 処理済みの情報の読み込み
    else:
        info_photo_cache = {}
    preproccedPhotoFiles = list(info_photo_cache.keys())    # 処理済みファイルリスト
    for filename in tqdm(files, desc="photo info"):
        if filename in preproccedPhotoFiles:
            info_ret[filename] = info_photo_cache[filename]
            continue    # 処理済みのものはcacheを使う
        im = cv2.imread(f"images/images/{filename}")
        row = im.shape[0]
        col = im.shape[1]
        aspectRatio = col / row
        info_ret[filename]["aspectRatio"] = aspectRatio
    with open("images/info_photo_cache.json", "w", encoding="utf-8") as f:
        json.dump(info_ret, f, ensure_ascii=False, indent=2)
    return info_ret


def preprocess_movie(files, info):
    """
    動画のサムネイル作成との情報（日付、長さ、アスペクト比など）の取得
    （処理に時間がかかるので、一度処理した情報は再利用する）
    """
    if not os.path.exists("images/thumbnails"):
        os.makedirs("images/thumbnails")
    # サムネイル作成
    info_ret = {}
    for filename in tqdm(files, desc="movie thumbnail"):
        filename_woExt = os.path.splitext(os.path.basename(filename))[0]
        dt = info[filename]["thumbnail"]
        time = ms2s(dt)
        thumbnail_filename = f"images/thumbnails/{filename_woExt}__{time}.png"
        info_ret[filename] = {"thumbnail_filename": thumbnail_filename}

        if os.path.exists(thumbnail_filename):
            continue    # 処理済みの場合skip
        video = cv2.VideoCapture(f"images/images/{filename}")
        video.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
        _, img = video.read()
        img = scale(img, 400)
        cv2.imwrite("images/thumbnails/temp.png", img)
        shutil.move("images/thumbnails/temp.png", thumbnail_filename)

    # 情報の取得
    cache_filename = os.path.join("images", "info_movie_cache.json")
    if os.path.isfile(cache_filename):
        with open(cache_filename, "r", encoding="utf-8") as f:
            info_movie_cache = json.load(f) # 処理済みの情報の読み込み
    else:
        info_movie_cache = {}
    preproccedMovieFiles = list(info_movie_cache.keys())
    for filename in tqdm(files):
        if filename in preproccedMovieFiles:
            info_ret[filename] = info_movie_cache[filename]
            continue    # 処理済みのものはcacheを使う
        cmd = f"ffprobe images/images/{filename} -hide_banner -show_entries format=duration"
        r = subprocess.run(cmd, stdout=subprocess.PIPE)
        assert r.stdout[:19] == b'[FORMAT]\r\nduration='
        assert r.stdout[-13:] == b'\r\n[/FORMAT]\r\n', r.stdout
        totalTime = float(r.stdout[19:-13])
        cmd = f"ffmpeg -i images/images/{filename}"
        r = subprocess.run(cmd, stderr=subprocess.PIPE)
        assert "16:9" in str(r.stderr) or "1920x1080" in str(r.stderr), str(r.stderr)
        aspectRatio = 16 / 9
        info_ret[filename]["totalTime"] = totalTime
        info_ret[filename]["aspectRatio"] = aspectRatio
    with open("images/info_movie_cache.json", "w", encoding="utf-8") as f:
        json.dump(info_ret, f, ensure_ascii=False, indent=2)
    return info_ret


def main():
    """
    メイン関数
    """
    photoFiles, movieFiles = selectFiles(os.listdir("images/images"))
    with open("images/info.json", "r", encoding="utf-8") as f:
        info_input = json.load(f)

    tag_list = []
    for x in list(info_input["movie"].values()) + list(info_input["photo"].values()):
        tag_list.extend(x["tag"])
    tag_list = sorted(list(set(tag_list))) 

    info_photo = preprocess_photo(photoFiles)
    info_movie = preprocess_movie(movieFiles, info_input["movie"])


    #####################
    # info_vue.json作成 #
    #####################
    info_vue = {}
    # example
    #  yearMonthList : [200010, 200012, 200101, 200102]
    #  yearList : [2000, 2001]
    #  monthList : [[10, 12], [1, 2]]
    yearList = []
    monthList = [[]]
    yearMonthList = []
    for filename in photoFiles + movieFiles:
        _, _, _, yyyymm = extractDateFromFilename(filename)
        yearMonthList.append(yyyymm)
    yearMonthList = sorted(list(set(yearMonthList)))
    for yyyymm in yearMonthList:
        yearList.append(int(np.floor(yyyymm / 100)))
    yearList = sorted(list(set(yearList)))
    monthList = [[] for _ in yearList]
    for yyyymm in yearMonthList:
        year = int(np.floor(yyyymm / 100))
        month = yyyymm - 100 * year
        idx = yearList.index(year)
        monthList[idx].append(month)
    info_vue["yearMonthList"] = yearMonthList
    info_vue["yearList"] = yearList
    info_vue["monthList"] = monthList

    # birth
    birthInfo = info_input["birth"]
    birthText = {}
    for yyyymm in yearMonthList:
        year = int(np.floor(yyyymm / 100))
        month = yyyymm - year * 100
        txt = ""
        for d in birthInfo:
            name = d["name"]
            birthYYYYMM = int(np.floor(d["date"] / 100))
            birthYYYY = int(np.floor(birthYYYYMM / 100))
            birthMM = birthYYYYMM - birthYYYY * 100
            yyyymm = year * 100 + month
            if yyyymm < birthYYYYMM:
                txt += f"{name}：誕生前、"
            elif yyyymm == birthYYYYMM:
                txt += f"{name}：誕生前～0歳0ヵ月、"
            elif yyyymm > birthYYYYMM:
                yyyy = int(np.floor(yyyymm / 100))
                mm = yyyymm - yyyy * 100
                diffMonth1 = (yyyy - birthYYYY) * 12 + (mm - birthMM) - 1
                diffMonth2 = diffMonth1 + 1
                ageY1 = int(np.floor(diffMonth1 / 12))
                ageM1 = diffMonth1 - ageY1 * 12
                ageY2 = int(np.floor(diffMonth2 / 12))
                ageM2 = diffMonth2 - ageY2 * 12
                txt += f"{name}：{ageY1}歳{ageM1}ヵ月"
                txt += f"～{ageY2}歳{ageM2}ヵ月、"
            birthText[yyyymm] = txt[:-1]
    info_vue["birthText"] = birthText

    infoGant = []
    for d in birthInfo:
        birthday = d["date"]
        data = {}
        age = -1
        while True:
            age += 1
            x1 = birthday + 10000 * age
            x2 = birthday + 10000 * (age + 1)
            if x1 > yearList[-1] * 10000 + monthList[-1][-1] * 100:
                break
            x1_pos = yyyymmdd2pos(x1, yearList, monthList)
            x2_pos = yyyymmdd2pos(x2, yearList, monthList)
            if (x1_pos == 0) & (x2_pos == 0):
                continue
            data[f'{d["name"]} {age}歳'] = [x1_pos, x2_pos]
        infoGant.append({"name": d["name"], "gant": data})
    info_vue["gant"] = infoGant

    yyyymm2pos = {}
    for yyyymm in [0] + yearMonthList:
        yyyymm2pos[yyyymm * 100] = yyyymmdd2pos(yyyymm * 100, yearList, monthList)
    info_vue["yyyymm2pos"] = yyyymm2pos

    yyyymm2text = {}
    for yyyymm in yearMonthList:
        year = int(np.floor(yyyymm / 100))
        month = yyyymm - year * 100
        yyyymm2text[yyyymm] = f"{year}年{month}月"
    info_vue["yyyymm2text"] = yyyymm2text


    infoPlayPhoto = {yyyymm: [] for yyyymm in yearMonthList}
    infoThumbPhoto = {yyyymm: [] for yyyymm in yearMonthList}
    infoPlayMovie = {yyyymm: [] for yyyymm in yearMonthList}
    infoThumbMovie = {yyyymm: [] for yyyymm in yearMonthList}
    infoPlayList = {
        "thumbnail": {
            "all": {tag: [] for tag in tag_list},
            "photo": {tag: [] for tag in tag_list},
            "movie": {tag: [] for tag in tag_list}
        },
        "play": {
            "photo": {tag: [] for tag in tag_list},
            "movie": {tag: [] for tag in tag_list}
        },
    }

    # photo
    id = 0
    for filename, property in info_photo.items():
        year, month, day, yyyymm = extractDateFromFilename(filename)
        date = f"{year}年{month}月{day}日"

        infoThumbPhoto[yyyymm].append(
            {"fileName": property["thumbnail_filename"],  "date": date, "aspectRatio": property["aspectRatio"], "id": id}
        )

        for tag in info_input["photo"][filename]["tag"]:
            infoPlayList["thumbnail"]["all"][tag].append(
                {"fileName": property["thumbnail_filename"],  "date": date, "aspectRatio": property["aspectRatio"], "id": id}
            )
            infoPlayList["thumbnail"]["photo"][tag].append(
                {"fileName": property["thumbnail_filename"],  "date": date, "aspectRatio": property["aspectRatio"], "id": id}
            )

        infoPlayPhoto[yyyymm].append(
            {"fileName": f"images/images/{filename}", "date": date, "id": id}
        )
        for tag in info_input["photo"][filename]["tag"]:
            infoPlayList["play"]["photo"][tag].append(
                {"fileName": f"images/images/{filename}", "date": date, "id": id}
            )

        id += 1

    # movie
    for filename, property in info_movie.items():
        year, month, day, yyyymm = extractDateFromFilename(filename)
        date = f"{year}年{month}月{day}日"

        infoThumbMovie[yyyymm].append(
            {"fileName": property["thumbnail_filename"], "date": date, "aspectRatio": property["aspectRatio"], "id": id}
        )
        for tag in info_input["movie"][filename]["tag"]:
            infoPlayList["thumbnail"]["all"][tag].append(
                {"fileName": property["thumbnail_filename"],  "date": date, "aspectRatio": property["aspectRatio"], "id": id}
            )
            infoPlayList["thumbnail"]["movie"][tag].append(
                {"fileName": property["thumbnail_filename"],  "date": date, "aspectRatio": property["aspectRatio"], "id": id}
            )

        infoPlayMovie[yyyymm].append(
            {"fileName": f"images/images/{filename}", "totalTime": property["totalTime"], "id": id}
        )
        for tag in info_input["movie"][filename]["tag"]:
            infoPlayList["play"]["movie"][tag].append(
            {"fileName": f"images/images/{filename}", "totalTime": property["totalTime"], "id": id}
        )

        id += 1

    info_vue["playPhoto"] = infoPlayPhoto
    info_vue["thumbPhoto"] = infoThumbPhoto
    info_vue["playMovie"] = infoPlayMovie
    info_vue["thumbMovie"] = infoThumbMovie
    info_vue["playList"] = infoPlayList
    with open("images/info_vue.json", "w", encoding="utf-8") as f:
        json.dump(info_vue, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
