import os
import json
import shutil
import cv2
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

    with open('images/info_thumb.json', 'r', encoding='utf-8') as f:
        info_thumb = json.load(f)

    for filename, dt in info_thumb.items():
        f_noExt, _ = os.path.splitext(filename)
        time = dt[0] * 60 + dt[1]
        fThumb = f'{f_noExt}__{time}.png'
        if not os.path.exists(f'images/thumbnails/{fThumb}'):
            video = cv2.VideoCapture(f'images/images/{filename}')
            video.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
            _, img = video.read()
            img = scale(img, 400)
            cv2.imwrite('images/thumbnails/temp.png', img)
            shutil.move('images/thumbnails/temp.png', f'images/thumbnails/{fThumb}')

    with open('images/info_long.json', 'r', encoding='utf-8') as f:
        info_long = json.load(f)
    for dt in info_long:
        filename = dt["thumbnailFile"]
        time = dt["thumbnailTime"][0] * 60 + dt["thumbnailTime"][1]
        fThumb = f'{f_noExt}__{time}.png'
        if not os.path.exists(f'images/thumbnails/{fThumb}'):
            video = cv2.VideoCapture(f'images/images/{filename}')
            video.set(cv2.CAP_PROP_POS_MSEC, time * 1000)
            _, img = video.read()
            img = scale(img, 400)
            cv2.imwrite('images/thumbnails/temp.png', img)
            shutil.move('images/thumbnails/temp.png', f'images/thumbnails/{fThumb}')


    # photo
    photoFiles, _ = selectFiles(os.listdir("images/images"))
    for filename in tqdm(photoFiles):
        if not os.path.exists(f'images/thumbnails/{filename}'):
            img = cv2.imread(f"images/images/{filename}")
            img = scale(img, 400)
            cv2.imwrite('images/thumbnails/temp.png', img)
            shutil.move('images/thumbnails/temp.png', f'images/thumbnails/{filename}')

if __name__ == '__main__':
    main()