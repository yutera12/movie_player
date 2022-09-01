import os
import json
import shutil
import cv2

def scale_to_width(img, width):
    h, w = img.shape[:2]
    height = round(h * (width / w))
    dst = cv2.resize(img, dsize=(width, height))
    return dst

def main():
    with open('info.json', 'r', encoding='utf-8') as f:
        info = json.load(f)
    for data in info:
        for dt in data['data']:
            movie = dt['fileName']
            thumbnail = dt['thumbnailTime']
            thumbnail = thumbnail[0] * 60 + thumbnail[1]
            filename = f'{movie}__{thumbnail}'
            if not os.path.exists(f'thumbnails/{filename}.png'):
                video = cv2.VideoCapture(f'movies/{movie}')
                video.set(cv2.CAP_PROP_POS_MSEC, thumbnail * 1000)
                _, img = video.read()
                img = scale_to_width(img, 400)
                cv2.imwrite('thumbnails/temp.png', img)
                shutil.move('thumbnails/temp.png', f'thumbnails/{filename}.png')

if __name__ == '__main__':
    main()