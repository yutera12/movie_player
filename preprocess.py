import os
import subprocess
import json
import shutil
import cv2
import numpy as np
from tqdm import tqdm


def extractDataFromFilename(filename):
    if filename[:8].isdecimal():
        year = int(filename[:4])
        month = int(filename[4:6])
        day = int(filename[6:8])
        yyyymm = int(filename[:6])
        if not(1950 <= year <= 2100) or not(1 <= month <= 12) or not(1 <= day <= 31):
            return None, None, None, None
        return year, month, day, yyyymm
    return None, None, None, None


def selectFiles(files):
    photoFiles = []
    movieFiles = []
    for file in files:
        _, ext = os.path.splitext(file)
        if ext == '.jpg' or  ext == '.JPG' or ext == '.png' or ext == '.PNG' :
            photoFiles.append(file)
        elif ext == '.mp4':
            movieFiles.append(file)
        else:
            assert False, file
    return photoFiles, movieFiles


def scale(img, px):
    h, w = img.shape[:2]
    if h > w:
        img = scale_to_height(img, px)
    else:
        img = scale_to_width(img, px)
    return img


def scale_to_width(img, width):
    h, w = img.shape[:2]
    height = round(h * (width / w))
    dst = cv2.resize(img, dsize=(width, height))
    return dst


def scale_to_height(img, height):
    h, w = img.shape[:2]
    width = round(w * (height / h))
    dst = cv2.resize(img, dsize=(width, height))
    return dst


def ms2s(time):
    return time[0] * 60 + time[1]


def create_thumbnail(time, thumbFileName, orgFileName):
    if not os.path.exists(f'images/thumbnails/{thumbFileName}'):
        video = cv2.VideoCapture(f'images/images/{orgFileName}')
        video.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
        _, img = video.read()
        img = scale(img, 400)
        cv2.imwrite('images/thumbnails/temp.png', img)
        shutil.move('images/thumbnails/temp.png', f'images/thumbnails/{thumbFileName}')


def totalTimeThumb(time):
    if time > 59.5:
        m = int(np.floor(np.round(time) / 60))
        s = np.round(time - m * 60)
        return f'{m}分{s}秒'
    return f'{np.round(time)}秒'


def main():
    ###################
    # info.jsonの作成 #
    ###################
    info_new = {}  # info.jsonの元

    # 古いinfo.jsonの読み込み
    if os.path.isfile('images/info.json'):
        with open('images/info.json', 'r', encoding='utf-8') as f:
            info_old = json.load(f)
    else:
        info_old = {'birth': [], 'short': [], 'long': [], 'photo': []}

    # birth
    with open('images/info_birth.json', 'r', encoding='utf-8') as f:
        info_new['birth'] = json.load(f)

    # thumb
    with open('images/info_thumb.json', 'r', encoding='utf-8') as f:
        info_thumb = json.load(f)

    # photo (処理に時間がかかるので、info_oldに存在する情報は流用)
    info_new['photo'] = []
    preproccedPhotoFiles = [f['fileName'] for f in info_old['photo']]
    photoFiles, _ = selectFiles(os.listdir('images/images'))
    for filename in tqdm(photoFiles):
        if filename in preproccedPhotoFiles:
            idx = preproccedPhotoFiles.index(filename)
            info_new['photo'].append(info_old['photo'][idx])
        else:
            im = cv2.imread(f'images/images/{filename}')
            row = im.shape[0]
            col = im.shape[1]
            aspectRatio = col / row
            year, month, day, yyyymm = extractDataFromFilename(filename)
            assert not year is None
            info_new['photo'].append({
                'fileName': f'images/images/{filename}',
                'thumbnailFile': f'images/thumbnails/{filename}',
                'date': f'{year}年{month}月{day}日',
                'yyyymm': yyyymm,
                'aspectRatio': aspectRatio
            })
    # short
    # 処理に時間がかかるので、info_oldに存在する情報は流用する
    info_new['short'] = []
    preproccedShortMovieFiles = [f['fileName'] for f in info_old['short']]
    _, movieFiles = selectFiles(os.listdir('images/images'))
    errFiles = []
    for filename in tqdm(movieFiles):
        filenameWOext = os.path.splitext(os.path.basename(filename))[0]
        if filename in preproccedShortMovieFiles:
            idx = preproccedShortMovieFiles.index(filename)
            info_new['short'].append(info_old['short'][idx])
        else:
            cmd = f'ffprobe images/images/{filename} -hide_banner -show_entries format=duration'
            r = subprocess.run(cmd, stdout=subprocess.PIPE)
            totalTime = float(str(r.stdout)[23:-18])
            cmd = f'ffmpeg -i images/images/{filename}'
            r = subprocess.run(cmd, stderr=subprocess.PIPE)
            if '16:9' in str(r.stderr) or '1920x1080' in str(r.stderr):
                aspectRatio = 16 / 9
            else:
                assert False, str(r.stderr)
            year, month, day, yyyymm = extractDataFromFilename(filename)
            if year is None:
                errFiles.append(filename)
            else:
                info_new['short'].append({
                    'fileName': f'images/images/{filename}',
                    'totalTime': totalTime,
                    'totalTimeThumb': totalTimeThumb(totalTime),
                    'yyyymm': yyyymm,
                    'date': f'{year}年{month}月{day}日',
                    'aspectRatio': aspectRatio,
                    'thumbnailFile': f'images/thumbnails/{filenameWOext}__'
                      + str(ms2s(info_thumb[filename])) +'.png'
                })

    # long
    # 処理に時間がかかるので、info_oldに存在する情報は流用する
    with open('images/info_long.json', 'r', encoding='utf-8') as f:
        info_long = json.load(f)
    info_new['long'] = []
    preproccedLongMovieFiles = [f['fileName'] for f in info_old['long']]
    for dt in tqdm(info_long):
        fileNames = dt['fileName']
        if fileNames in preproccedLongMovieFiles:
            idx = preproccedLongMovieFiles.index(fileNames)
            info_new['long'].append(info_old['long'][idx])
        else:
            times = []
            for f in fileNames:
                cmd = f'ffprobe images/images/{f} -hide_banner -show_entries format=duration'
                r = subprocess.run(cmd, stdout=subprocess.PIPE)
                totalTime = float(str(r.stdout)[23:-18])
                times.append(totalTime)
                cmd = f'ffmpeg -i images/images/{filename}'
                r = subprocess.run(cmd, stderr=subprocess.PIPE)
                if '16:9' in str(r.stderr):
                    aspectRatio = 16 / 9
                else:
                    assert False, 'error'

            filenameWOext = os.path.splitext(os.path.basename(dt['thumbnailFile']))[0]

            info_new['long'].append(
                {'fileName': ['images/images/' + f for f in dt['fileName']],
                 'date': dt['date'],
                 'thumbnailFile': f'images/thumbnails/{filenameWOext}__' + str(ms2s(dt['thumbnailTime'])) +'.png',
                 'totalTime': times,
                 'totalTimeThumb': totalTimeThumb(np.sum(times)),
                 'aspectRatio': aspectRatio})

    # dump
    with open('images/info.json', 'w', encoding='utf-8') as f:
        json.dump(info_new, f, ensure_ascii=False, indent=2)

    print(errFiles)

    ###################
    # サムネイルの作成 #
    ###################
    if not os.path.exists('images/thumbnails'):
        os.makedirs('images/thumbnails')

    with open('images/info_thumb.json', 'r', encoding='utf-8') as f:
        info_thumb = json.load(f)
    for orgFileName, dt in info_thumb.items():
        f_noExt, _ = os.path.splitext(orgFileName)
        time = dt[0] * 60 + dt[1]
        thumbFileName = f'{f_noExt}__{time}.png'
        create_thumbnail(time, thumbFileName, orgFileName)

    with open('images/info_long.json', 'r', encoding='utf-8') as f:
        info_long = json.load(f)
    for dt in info_long:
        orgFileName = dt['thumbnailFile']
        f_noExt, _ = os.path.splitext(orgFileName)
        time = dt['thumbnailTime'][0] * 60 + dt['thumbnailTime'][1]
        thumbFileName = f'{f_noExt}__{time}.png'
        create_thumbnail(time, thumbFileName, orgFileName)

    photoFiles, _ = selectFiles(os.listdir('images/images'))
    for filename in tqdm(photoFiles):
        if not os.path.exists(f'images/thumbnails/{filename}'):
            img = cv2.imread(f'images/images/{filename}')
            img = scale(img, 400)
            cv2.imwrite('images/thumbnails/temp.png', img)
            shutil.move('images/thumbnails/temp.png', f'images/thumbnails/{filename}')

    # example
    #  yearMonthList : [200010, 200012, 200101, 200102]
    #  yearList : [2000, 2001]
    #  monthList : [[10, 12], [1, 2]]
    yearList = []
    monthList = [[]]
    yearMonthList = []
    for d in info_new['short'] + info_new['photo']:
        yearMonthList.append(d['yyyymm'])
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

    birthText = {}
    for yyyymm in yearMonthList:
        year = int(np.floor(yyyymm / 100))
        month = yyyymm - year * 100
        txt = ""
        for d in info_new['birth']:
            name = d['name']
            birthYYYYMM = int(np.floor(d['date'] / 100))
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
    info_vue = {
        'yearMonthList': yearMonthList,
        'yearList' : yearList,
        'monthList' : monthList,
        'birthText' : birthText
    }
    with open('images/info_vue.json', 'w', encoding='utf-8') as f:
        json.dump(info_vue, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()