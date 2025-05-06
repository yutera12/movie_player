# 環境構築手順

## 写真・動画の格納
* `movie_player/images/images`に写真、動画を格納
  * ファイル名は、`yyyymmdd*.{拡張子}`。例えば、`20230405.jpeg`、`20230405-01.jpeg`、`202304051223.mp4`など
  * 画像の対応フォーマットは、`.jpeg`, `.jpg`, `.png`, `.JPEG`, `.JPG`, `.PNG`。
  * 動画は、`.mp4`など
* `movie_player/images/birth.json`に誕生日情報を記述。内容の例は下の通り。
  ```
  [
    {"name": "a", "date": 20200115},
    {"name": "b", "date": 20210204}
  ]
  ```
* `movie_player/images/info_thumb.json`に動画のサムネイル情報を記述。内容は下の通り。
  * この場合、`202304051223.mp4`の動画については0分1.31秒の瞬間がサムネイル画像となる。`"20230407_1.mp4"`の動画については2分0秒の瞬間がサムネイル画像となる。
  ```
  {
    "202304051223.mp4": [0, 1.31],
    "20230407_1.mp4": [2, 0]
  }
  ```

## 設定ファイルとサムネイルの作成
* `cd movie_player`
* `python preprocess.py`
  * `movie_player/images`に`info_image.json`と`info_vue.json`が生成される

## サーバの起動

* node.jsのインストール
* `cd movie_player`
* `npm install`
* `npm run dev`
* ブラウザで、 http://localhost:5500 へアクセス

# コンポーネントの構成

```
App
|--Home
|  |--Nav
|  |  |--Table
|  |
|  |--Thumb
|
|--Play
|--View
```

* 思想
  * `Home`で設定ファイルを読み込み
  * どの月を選択したか: `Table` -> `Nav` -> `Home` -> `App` -> `Home` -> `Thumb`
  * どの動画を再生するか: `Thumb` -> id -> `Home` -> info, id -> `App` -> info, id -> `Play`
