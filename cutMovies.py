import json
import subprocess
import os

def main():
    with open('images/info.json', 'r', encoding='utf-8') as f:
        info = json.load(f)
    info_short = []
    dateOld = ""
    for dt in info['short']:
        filename = dt["fileName"]
        playTime = dt["playTime"]
        time1 = playTime[0][0] * 60 + playTime[0][1]
        time2 = playTime[1][0] * 60 + playTime[1][1]
        thumbTime = dt['thumbnailTime']
        comment = dt["comment"]
        date = dt["date"]
        if date != dateOld:
            count = 0
        else:
            count += 1
        new_filename = f"{date}_{count}.mp4"
        #cmd = f"ffmpeg -ss {time1} -to {time2} -i images/images/{filename} -c copy images/images/{new_filename}"
        cmd = f"ffmpeg -ss {time1} -to {time2} -i images/images/{filename} images/images/{new_filename}"
        dateOld = date
        #if not os.path.exists(f'images/images/{new_filename}'):
        #    subprocess.run(cmd)
        timeThumbSec = (thumbTime[0] * 60 + thumbTime[1]) - time1
        totalTime = time2 - time1
        if timeThumbSec == totalTime:
            timeThumbSec -= 0.1
        timeThumbMin = timeThumbSec // 60
        timeThumbSec = timeThumbSec % 60
        totalTimeMin = totalTime // 60
        totalTimeSec = totalTime % 60
        xxx = {"fileName": new_filename,
               "comment": comment,
               "date": date,
               "thumbnailFile": new_filename,
               "thumbnailTime": [timeThumbMin, timeThumbSec],
               "totalTime" : [totalTimeMin, totalTimeSec]
               }
        info_short.append(xxx)
    with open("images/info_short_2.json", "w", encoding="utf-8") as f:
        json.dump(info_short, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()