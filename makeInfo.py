import os
import subprocess
import json
import cv2
import numpy as np
from tqdm import tqdm


def selectFiles(files):
    photoFiles = []
    movieFiles = []
    for file in files:
        _, ext = os.path.splitext(file)
        if ext == '.jpg' or  ext == '.JPG' or ext == ".png" or ext == ".PNG" :
            photoFiles.append(file)
        elif ext == ".mp4":
            movieFiles.append(file)
        else:
            assert False, file
    return photoFiles, movieFiles

def ms2s(time):
    return time[0] * 60 + time[1]


def totalTimeThumb(time):
    if time > 59.5:
        m = np.floor(np.round(time) / 60)
        s = np.round(time - m * 60)
        return f'{m}分{s}秒'
    return f'{np.round(time)}秒'


def main():
    # 古いinfo.jsonの読み込み
    if os.path.isfile("images/info.json"):
        with open("images/info.json", 'r', encoding='utf-8') as f:
            info_old = json.load(f)
    else:
        info_old = {
            "birth": [],
            "short": [],
            "long": [],
            "photo": [],
            "thumb": []
        }

    # birth
    info_new = {}
    with open("images/info_birth.json", 'r', encoding='utf-8') as f:
        info_new["birth"] = json.load(f)
    # thumb
    with open("images/info_thumb.json", 'r', encoding='utf-8') as f:
        info_thumb = json.load(f)
    # photo
    # 処理に時間がかかるので、info_oldに存在する情報は流用する
    info_new["photo"] = []
    preproccedPhotoFiles = [f["fileName"] for f in info_old["photo"]]
    photoFiles, _ = selectFiles(os.listdir("images/images"))
    for filename in tqdm(photoFiles):
        if filename in preproccedPhotoFiles:
            idx = preproccedPhotoFiles.index(filename)
            info_new["photo"].append(info_old["photo"][idx])
        else:
            im = cv2.imread(f"images/images/{filename}")
            row = im.shape[0]
            col = im.shape[1]
            aspectRatio = col / row
            yyyymmdd = filename[:8]
            year = int(filename[:4])
            month = int(filename[4:6])
            day = int(filename[6:8])
            yyyymm = year * 100 + month
            info_new["photo"].append({
                "fileName": "images/images/" + filename,
                "thumbnailFile": "images/thumbnails/" + filename,
                "date": f"{year}年{month}月{day}日",
                # "yyyymmdd": yyyymmdd,
                "yyyymm": yyyymm,
                # "year": year,
                # "month": month,
                # "day": day,
                "aspectRatio": aspectRatio
            })
    # short
    # 処理に時間がかかるので、info_oldに存在する情報は流用する
    info_new["short"] = []
    preproccedShortMovieFiles = [f["fileName"] for f in info_old["short"]]
    _, movieFiles = selectFiles(os.listdir("images/images"))
    errFiles = []
    for filename in tqdm(movieFiles):
        filenameWOext = os.path.splitext(os.path.basename(filename))[0]
        if filename in preproccedShortMovieFiles:
            idx = preproccedShortMovieFiles.index(filename)
            info_new["short"].append(info_old["short"][idx])
        else:
            cmd = f"ffprobe images/images/{filename} -hide_banner -show_entries format=duration"
            r = subprocess.run(cmd, stdout=subprocess.PIPE)
            totalTime = float(str(r.stdout)[23:-18])
            cmd = f"ffmpeg -i images/images/{filename}"
            r = subprocess.run(cmd, stderr=subprocess.PIPE)
            if "16:9" in str(r.stderr) or "1920x1080" in str(r.stderr):
                aspectRatio = 16 / 9
            else:
                assert False, str(r.stderr)
            if filename[:8].isdecimal():
                yyyymmdd = int(filename[:8])
                year = int(filename[:4])
                month = int(filename[4:6])
                day = int(filename[6:8])
                yyyymm = year * 100 + month
                if not(1950 <= year <= 2100) or not(1 <= month <= 12) or not(1 <= day <= 31):
                    errFiles.append(filename)
                else:
                    info_new["short"].append({
                        "fileName": "images/images/" + filename,
                        "totalTime": totalTime,
                        "totalTimeThumb": totalTimeThumb(totalTime),
                        "yyyymm": yyyymm,
                        "date": f"{year}年{month}月{day}日",
                        "aspectRatio": aspectRatio,
                        "thumbnailFile": 'images/thumbnails/'
                          + filenameWOext
                          + '__'
                          + str(ms2s(info_thumb[filename])) +'.png'
                    })
                    # date: year + "年" + month + "月" + day + "日"
            else:
                errFiles.append(filename)
    # long
    # 処理に時間がかかるので、info_oldに存在する情報は流用する
    with open("images/info_long.json", 'r', encoding='utf-8') as f:
        info_long = json.load(f)
    info_new["long"] = []
    preproccedLongMovieFiles = [f["fileName"] for f in info_old["long"]]
    for dt in tqdm(info_long):
        fileNames = dt["fileName"]
        if fileNames in preproccedLongMovieFiles:
            idx = preproccedLongMovieFiles.index(fileNames)
            info_new["long"].append(info_old["long"][idx])
        else:
            times = []
            for f in fileNames:
                cmd = f"ffprobe images/images/{f} -hide_banner -show_entries format=duration"
                r = subprocess.run(cmd, stdout=subprocess.PIPE)
                totalTime = float(str(r.stdout)[23:-18])
                times.append(totalTime)
                cmd = f"ffmpeg -i images/images/{filename}"
                r = subprocess.run(cmd, stderr=subprocess.PIPE)
                if "16:9" in str(r.stderr):
                    aspectRatio = 16 / 9
                else:
                    assert False, "error"

            filenameWOext = os.path.splitext(os.path.basename(dt["thumbnailFile"]))[0]

            info_new["long"].append(
                {"fileName": ["images/images/" + f for f in dt["fileName"]],
                 "date": dt["date"],
                 "thumbnailFile": 'images/thumbnails/' + filenameWOext + '__' + str(ms2s(dt["thumbnailTime"])) +'.png',
                 "totalTime": times,
                 "totalTimeThumb": totalTimeThumb(np.sum(times)),
                 "aspectRatio": aspectRatio})

    # dump
    with open("images/info.json", "w", encoding="utf-8") as f:
        json.dump(info_new, f, ensure_ascii=False, indent=2)

    print(errFiles)


if __name__ == '__main__':
    main()