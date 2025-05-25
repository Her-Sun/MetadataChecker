# PNG Viewer

PNG画像ビューアーアプリケーション。SOLID原則とPEP8に準拠した設計で、画像の閲覧とメタデータの表示、検索機能を提供します。

## 機能

- PNG画像の表示とナビゲーション
  - 矢印キー（←→）で画像の切り替え
  - 画像の左右クリックで画像の切り替え
  - DeleteキーまたはDeleteボタンで現在の画像をごみ箱に移動
  - Escキーでアプリケーションを終了
- メタデータの表示
  - ファイル名、フォーマット、サイズ、モード
  - Parameters情報の整形表示
    - Negative Prompt以降を非表示
- 右クリック機能
  - クリックした行のテキストをGoogle画像検索

## システム構成

```mermaid
classDiagram
    class ImageViewer {
        -画像ファイル管理クラス
        -画像表示ラベル
        -メタデータ表示テキストエリア
        -回転Deleteボタン
        +初期化(対象パス)
        -UI設定
        -現在の画像表示
        -右クリックメニュー処理
        -画像クリック処理
        -画像ごみ箱移動処理
        +キー入力処理
        +イベントフィルター
    }

    class ImageFileManager {
        -対象パス
        -現在のインデックス
        -PNGファイルリスト
        +初期化(対象パス)
        -PNGファイル読み込み
        +ファイルリスト更新
        +現在のファイル取得
        +次のファイル取得
        +前のファイル取得
        +現在のファイルごみ箱移動
        +ファイル存在確認
    }

    class ImageMetadata {
        -画像パス
        -メタデータ辞書
        -画像フォーマット
        -画像サイズ
        -画像モード
        +初期化(画像パス, 画像)
        -メタデータ読み込み
        -メタデータ抽出
        +整形済みメタデータ取得
    }

    class RotatedButton {
        -固定サイズ
        +初期化(テキスト)
        +描画イベント処理
    }

    ImageViewer --> ImageFileManager : 使用
    ImageViewer --> ImageMetadata : 使用
    ImageViewer --> RotatedButton : 使用
    ImageFileManager --> Path : 管理
    ImageMetadata --> Image : 処理
```

## 必要条件

- Python 3.8以上
- 必要なパッケージ（requirements.txtに記載）:
  - PyQt6
  - Pillow
  - send2trash

## インストール方法

1. リポジトリをクローン:
```bash
git clone [repository-url]
cd png-viewer
```

2. 仮想環境を作成して有効化:
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
venv\Scripts\activate     # Windowsの場合
```

3. 依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

## 使用方法

1. アプリケーションを起動:
```bash
python png_viewer.py <画像ファイルまたはフォルダのパス>
```

2. 操作方法:
   - 左右矢印キー: 画像の切り替え
   - 画像の左右クリック: 画像の切り替え
   - DeleteキーまたはDeleteボタン: 現在の画像をごみ箱に移動
   - Escキー: アプリケーションを終了
   - 右クリック: クリックした行のテキストでGoogle画像検索

## ライセンス

MIT License 