import json
import subprocess


def main():
    with open("images/info_long_org.json", "r", encoding="utf-8") as f:
        info = json.load(f)
    new_info = []
    for dt in info:
        files = dt["srcFileName"]
        with open("temp.txt", "w") as f:
            for fl in files:
                f.write(f"file images/movies/{fl}\n")
        outfilename = dt["distFileName"]
        cmd = f"ffmpeg -f concat -i temp.txt -c copy images/unitedMovies/{outfilename}"
        # cmd = f"ffmpeg -f concat -i temp.txt images/unitedMovies/{outfilename}"
        subprocess.run(cmd)
        cmd = f"ffprobe images/unitedMovies/{outfilename} -hide_banner -show_entries format=duration"
        r = subprocess.run(cmd, stdout=subprocess.PIPE)
        totalTime = float(str(r.stdout)[23:-18])
        totalTimeMin = totalTime // 60
        totalTimeSec = totalTime % 60
        date = outfilename.split(".")[0]
        xxx = {
            "fileName": outfilename,
            "date": date[:4] + "/" + date[4:6] + "/" + date[6:13] + "/" + date[13:15] + "/" + date[15:],
            "thumbnailFile": dt["thumbnailFile"],
            "thumbnailTime": dt["thumbnailTime"],
            "comment": dt["comment"],
            "totalTime": [totalTimeMin, totalTimeSec],
        }
    new_info.append(xxx)
    with open("images/info_long.json", "w", encoding="utf-8") as f:
        json.dump(new_info, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
