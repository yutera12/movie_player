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

# 環境構築手順

## 設定ファイルとサムネイルの作成

* `cd movie_player`
* `python makeInfo.py`
* `python makeThumb.py`

## 開発用サーバの起動

* node.jsのインストール
* `cd movie_player`
* `npm install`
* `npm run dev`

## build & 簡易サーバの起動

* `cd movie_player`
* `npm run build`
* コマンドプロンプトで`mklink /d .\dist\images ..\images`
* (vscode live serverの場合)distフォルダを開きgo liveをクリック
* http://localhost:5500
