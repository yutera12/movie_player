import os
import shutil
import json
import subprocess
from tqdm import tqdm


def selectFiles(files):
    photoFiles = []
    movieFiles = []
    for file in files:
        _, ext = os.path.splitext(file)
        if ext.lower() in [".jpg", ".jpeg", ".png"]:
            photoFiles.append(file)
        elif ext == ".mp4":
            movieFiles.append(file)
        else:
            assert False, file
    return photoFiles, movieFiles


photoFiles, movieFiles = selectFiles(os.listdir("images/images"))

with open("images/info_thumb.json", "r", encoding="utf-8") as f:
    info_thumb = json.load(f)

info_thumb_small = {}
with open("small_project_list.txt", "r") as f:
    filelist = f.readlines()
    for file in filelist:
        file = file.strip()
        if file in movieFiles:
            info_thumb_small[file] = info_thumb[file]
            outputPath = os.path.join("small_project", file)
            if not os.path.exists(outputPath):
                cmd = f"ffmpeg -i images/images/{file}"
                r = subprocess.run(cmd, stderr=subprocess.PIPE)
                if "1920x1080" in str(r.stderr):
                    target = "1280x720"
                else:
                    assert False
                cmd = f"ffmpeg -i images/images/{file} -s {target} {outputPath}"
                r = subprocess.run(cmd)  # , stderr=subprocess.PIPE)
        elif file in photoFiles:
            shutil.copy(os.path.join("images", "images", file), "small_project")
with open("info_thumb_small.json", "w", encoding="utf-8") as f:
    json.dump(info_thumb_small, f, ensure_ascii=False, indent=2)
