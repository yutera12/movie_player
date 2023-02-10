import os
import json
import shutil
import cv2
from tqdm import tqdm


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


def main():
    if not os.path.exists("images/thumbnails"):
        os.makedirs("images/thumbnails")
    with open('images/info.json', 'r', encoding='utf-8') as f:
        info = json.load(f)
    for dt in tqdm(info["short"] + info["long"]):
        if not isinstance(dt["fileName"], list):
            isShort = True
        else:
            isShort = False
        if isShort:
            f = dt['fileName']
            f_noExt, _ = os.path.splitext(f)
            time = info["thumb"][f]
            time = time[0] * 60 + time[1]
        else:
            f = dt["thumbnailFile"]
            f_noExt, _ = os.path.splitext(f)
            time = dt["thumbnailTime"][0] * 60 + dt["thumbnailTime"][1]
        fThumb = f'{f_noExt}__{time}.png'
        if not os.path.exists(f'images/thumbnails/{fThumb}'):
            video = cv2.VideoCapture(f'images/images/{f}')
            video.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
            _, img = video.read()
            img = scale(img, 400)
            cv2.imwrite('images/thumbnails/temp.png', img)
            shutil.move('images/thumbnails/temp.png', f'images/thumbnails/{fThumb}')
    # photo
    for dt in tqdm(info["photo"]):
        filename = dt["fileName"]
        if not os.path.exists(f'images/thumbnails/{filename}'):
            img = cv2.imread(f"images/images/{filename}")
            img = scale(img, 400)
            cv2.imwrite('images/thumbnails/temp.png', img)
            shutil.move('images/thumbnails/temp.png', f'images/thumbnails/{filename}')

if __name__ == '__main__':
    main()