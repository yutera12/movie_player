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
    return f'{int(np.round(time))}秒'


def yyyymmdd2pos(yyyymmdd, yearList, monthList):
    '''
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
    '''
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


def main():

    if not os.path.exists('images/thumbnails'):
        os.makedirs('images/thumbnails')

    ####################################
    # info_image.json、サムネイルの作成 #
    ####################################
    info_image = {}  # info_image.jsonの元

    # 古いinfo_image.jsonの読み込み
    if os.path.isfile('images/info_image.json'):
        with open('images/info_image.json', 'r', encoding='utf-8') as f:
            info_old = json.load(f)
    else:
        info_old = {'short': [], 'long': [], 'photo': []}

    # thumb
    with open('images/info_thumb.json', 'r', encoding='utf-8') as f:
        info_thumb = json.load(f)

    # photo (処理に時間がかかるので、info_oldに存在する情報は流用)
    info_image['photo'] = []
    preproccedPhotoFiles = [f['fileName'] for f in info_old['photo']]
    photoFiles, _ = selectFiles(os.listdir('images/images'))
    for filename in tqdm(photoFiles):

        # サムネイル作成
        if not os.path.exists(f'images/thumbnails/{filename}'):
            img = cv2.imread(f'images/images/{filename}')
            img = scale(img, 400)
            cv2.imwrite('images/thumbnails/temp.png', img)
            shutil.move('images/thumbnails/temp.png', f'images/thumbnails/{filename}')

        if f'images/images/{filename}' in preproccedPhotoFiles:
            idx = preproccedPhotoFiles.index(f'images/images/{filename}')
            info_image['photo'].append(info_old['photo'][idx])
        else:
            im = cv2.imread(f'images/images/{filename}')
            row = im.shape[0]
            col = im.shape[1]
            aspectRatio = col / row
            year, month, day, yyyymm = extractDataFromFilename(filename)
            assert not year is None
            info_image['photo'].append({
                'fileName': f'images/images/{filename}',
                'thumbnailFile': f'images/thumbnails/{filename}',
                'date': f'{year}年{month}月{day}日',
                'yyyymm': yyyymm,
                'aspectRatio': aspectRatio
            })
    # short
    # 処理に時間がかかるので、info_oldに存在する情報は流用する
    info_image['short'] = []
    preproccedShortMovieFiles = [f['fileName'] for f in info_old['short']]
    _, movieFiles = selectFiles(os.listdir('images/images'))
    errFiles = []
    for filename in tqdm(movieFiles):
        filenameWOext = os.path.splitext(os.path.basename(filename))[0]
        year, month, day, yyyymm = extractDataFromFilename(filename)

        # サムネイル作成
        if not year is None:
            dt = info_thumb[filename]
            time = dt[0] * 60 + dt[1]
            thumbFileName = f'{filenameWOext}__{time}.png'
            create_thumbnail(time, thumbFileName, filename)

            if f'images/images/{filename}' in preproccedShortMovieFiles:
                idx = preproccedShortMovieFiles.index(f'images/images/{filename}')
                info_image['short'].append(info_old['short'][idx])
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
                info_image['short'].append({
                    'fileName': f'images/images/{filename}',
                    'totalTime': totalTime,
                    'totalTimeThumb': totalTimeThumb(totalTime),
                    'yyyymm': yyyymm,
                    'date': f'{year}年{month}月{day}日',
                    'aspectRatio': aspectRatio,
                    'thumbnailFile': f'images/thumbnails/{filenameWOext}__'
                      + str(ms2s(info_thumb[filename])) +'.png'
                })
        else:
            errFiles.append(filename)

    if len(errFiles) > 0:
        print(f'{errFiles}はshort動画に含まれません')

    # long
    # 処理に時間がかかるので、info_oldに存在する情報は流用する
    with open('images/info_long.json', 'r', encoding='utf-8') as f:
        info_long = json.load(f)
    info_image['long'] = []
    preproccedLongMovieFiles = [f['fileName'] for f in info_old['long']]
    for dt in tqdm(info_long):
        fileNames = dt['fileName']

        # サムネイル作成
        f_noExt, _ = os.path.splitext(dt['thumbnailFile'])
        time = dt['thumbnailTime'][0] * 60 + dt['thumbnailTime'][1]
        thumbFileName = f'{f_noExt}__{time}.png'
        create_thumbnail(time, thumbFileName, dt['thumbnailFile'])

        if [f'images/images/{f}' for f in fileNames] in preproccedLongMovieFiles:
            idx = preproccedLongMovieFiles.index([f'images/images/{f}' for f in fileNames])
            info_image['long'].append(info_old['long'][idx])
        else:
            times = []
            for filename in fileNames:
                cmd = f'ffprobe images/images/{filename} -hide_banner -show_entries format=duration'
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

            info_image['long'].append(
                {'fileName': ['images/images/' + f for f in dt['fileName']],
                 'date': dt['date'],
                 'thumbnailFile': f'images/thumbnails/{filenameWOext}__' + str(ms2s(dt['thumbnailTime'])) +'.png',
                 'totalTime': times,
                 'totalTimeThumb': totalTimeThumb(np.sum(times)),
                 'aspectRatio': aspectRatio})

    # dump
    with open('images/info_image.json', 'w', encoding='utf-8') as f:
        json.dump(info_image, f, ensure_ascii=False, indent=2)


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
    for d in info_image['short'] + info_image['photo']:
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
    info_vue['yearMonthList'] = yearMonthList
    info_vue['yearList'] = yearList
    info_vue['monthList'] = monthList

    # birth
    with open('images/info_birth.json', 'r', encoding='utf-8') as f:
        birthInfo = json.load(f)
    birthText = {}
  
    for yyyymm in yearMonthList:
        year = int(np.floor(yyyymm / 100))
        month = yyyymm - year * 100
        txt = ""
        for d in birthInfo:
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
    info_vue['birthText'] = birthText


    infoGant = []
    for d in birthInfo:
        birthday = d['date']
        info = {}
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
            info[f'{d["name"]} {age}歳'] = [x1_pos, x2_pos]
        infoGant.append({'name': d["name"], 'gant': info})
    info_vue['gant'] = infoGant

    yyyymm2pos = {}
    for yyyymm in [0] + yearMonthList:
        yyyymm2pos[yyyymm * 100] = yyyymmdd2pos(yyyymm * 100, yearList, monthList)
    info_vue['yyyymm2pos'] = yyyymm2pos

    yyyymm2text = {}
    for yyyymm in yearMonthList:
        year = int(np.floor(yyyymm / 100))
        month = yyyymm - year * 100
        yyyymm2text[yyyymm] = f'{year}年{month}月'
    info_vue['yyyymm2text'] = yyyymm2text

    infoPlayPhoto = {}
    infoThumbPhoto = {}
    infoPlayMovie = {}
    infoThumbMovie = {}
    for yyyymm in [0] + yearMonthList:
        infoPlayPhoto[yyyymm] = []
        infoThumbPhoto[yyyymm] = []
        infoPlayMovie[yyyymm] = []
        infoThumbMovie[yyyymm] = []

    id_photo = 0
    for d in info_image['photo']:
        infoThumbPhoto[d['yyyymm']].append(
            {
              'fileName': d['thumbnailFile'],
              'id': id_photo,
              'date': d['date'],
              'aspectRatio': d['aspectRatio']
            }
        )
        infoPlayPhoto[d['yyyymm']].append(
            {
                'fileName': d['fileName'],
                'date': d['date'],
                'id': id_photo
            }
        )
        infoPlayPhoto[0].append(
            {
                'fileName': d['fileName'],
                'date': d['date'],
                'id': id_photo
            }
        )
        id_photo += 1


    id_movie = 0
    # short
    for d in info_image['short']:
        infoThumbMovie[d['yyyymm']].append(
          {
            'fileName': d['thumbnailFile'],
            'id': id_movie,
            'totalTime': d['totalTimeThumb'],
            'date': d['date'],
            'aspectRatio': d['aspectRatio']
          }
        )
        # infoPlayMovie作成 //
        infoPlayMovie[d['yyyymm']].append(
          {
            'fileName': [d['fileName']],
            'totalTime': [d['totalTime']],
            'id': id_movie
          }
        )
        id_movie += 1
    # long
    for d in info_image['long']:
        infoThumbMovie[0].append(
          {
            'fileName': d['thumbnailFile'],
            'id': id_movie,
            'totalTime': d['totalTimeThumb'],
            'date': d['date'],
            'aspectRatio': d['aspectRatio']
          }
        )
        infoPlayMovie[0].append(
          {
            'fileName': d['fileName'],
            'totalTime': d['totalTime'],
            'id': id_movie
          }
        )
        id_movie += 1

    info_vue['playPhoto'] = infoPlayPhoto
    info_vue['thumbPhoto'] = infoThumbPhoto
    info_vue['playMovie'] = infoPlayMovie
    info_vue['thumbMovie'] = infoThumbMovie
    with open('images/info_vue.json', 'w', encoding='utf-8') as f:
        json.dump(info_vue, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    main()