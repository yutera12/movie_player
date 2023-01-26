# 環境構築手順

## サムネイルの作成

* `cd movie_player`
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
