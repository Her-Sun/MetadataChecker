#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import webbrowser
from pathlib import Path
from typing import List, Optional
from send2trash import send2trash

from PIL import Image
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter, QFont, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                            QWidget, QTextEdit, QHBoxLayout, QPushButton, QMessageBox)


class ImageFileManager:
    """画像ファイルの管理を行うクラス"""

    def __init__(self, target_path: Path) -> None:
        self.target_path = target_path
        self.current_index = 0
        self.png_files: List[Path] = []
        self._load_png_files()

    def _load_png_files(self) -> None:
        """PNGファイルの一覧を読み込む"""
        backup_target_path = self.target_path
        if self.target_path.is_file():
            # ファイルが指定された場合、親ディレクトリを対象とする
            self.target_path = self.target_path.parent

        self.png_files = sorted(
            [f for f in self.target_path.glob("*.png")
             if f.is_file()])

        # ファイルが指定された場合、そのファイルを現在のファイルとして設定
        if backup_target_path.is_file():
            for i, file in enumerate(self.png_files):
                if file == backup_target_path:
                    self.current_index = i
                    break

    def update_file_list(self) -> None:
        """ファイルリストを更新する"""
        current_file = self.get_current_file()
        self._load_png_files()
        
        # 現在のファイルが存在する場合、そのインデックスを維持
        if current_file and current_file in self.png_files:
            self.current_index = self.png_files.index(current_file)
        else:
            # 現在のファイルが存在しない場合、インデックスを調整
            if self.current_index >= len(self.png_files):
                self.current_index = max(0, len(self.png_files) - 1)

    def get_current_file(self) -> Optional[Path]:
        """現在の画像ファイルを取得"""
        if not self.png_files:
            return None
        return self.png_files[self.current_index]

    def next_file(self) -> Optional[Path]:
        # 1. 現在のリストの「表示済み部分」を確保
        shown_list = self.png_files[:self.current_index + 1]
        # 2. リストを更新
        self._load_png_files()
        if not self.png_files:
            return None
        # 3. shown_listの末尾から一致する画像を探す
        for path in reversed(shown_list):
            if path in self.png_files:
                idx = self.png_files.index(path)
                next_idx = (idx + 1) % len(self.png_files)
                self.current_index = next_idx
                return self.get_current_file()
        # 4. 一致しなければ先頭を表示
        self.current_index = 0
        return self.get_current_file()

    def previous_file(self) -> Optional[Path]:
        self.update_file_list()

        """前の画像ファイルを取得"""
        if not self.png_files:
            return None
        self.current_index = (self.current_index - 1) % len(self.png_files)
        return self.get_current_file()

    def delete_current_file(self) -> Optional[Path]:
        """現在のファイルをごみ箱に移動し、次のファイルを返す"""
        if not self.png_files:
            return None

        current_file = self.png_files[self.current_index]
        try:
            send2trash(str(current_file))  # ファイルをごみ箱に移動
            self.png_files.pop(self.current_index)  # リストから削除
            
            # インデックスの調整
            if not self.png_files:  # ファイルがなくなった場合
                return None
            if self.current_index >= len(self.png_files):
                self.current_index = 0
            
            return self.get_current_file()
        except Exception as e:
            print(f"ファイルの移動に失敗しました: {e}")
            return None

    def has_files(self) -> bool:
        """画像ファイルが存在するかどうかを確認"""
        return len(self.png_files) > 0


class ImageMetadata:
    """画像のメタデータを管理するクラス"""

    def __init__(self, image_path: Path, image: Optional[Image.Image] = None) -> None:
        self.image_path = image_path
        self._load_metadata(image)

    def _load_metadata(self, image: Optional[Image.Image] = None) -> None:
        """画像のメタデータを読み込む"""
        if image is None:
            with Image.open(self.image_path) as img:
                self._extract_metadata(img)
        else:
            self._extract_metadata(image)

    def _extract_metadata(self, image: Image.Image) -> None:
        """画像からメタデータを抽出"""
        self.metadata = image.info
        self.format = image.format
        self.size = image.size
        self.mode = image.mode

    def get_formatted_metadata(self) -> str:
        """メタデータを整形して返す"""
        metadata_str = f"ファイル名: {self.image_path.name}\n"
        metadata_str += f"フォーマット: {self.format}\n"
        metadata_str += f"サイズ: {self.size[0]}x{self.size[1]}\n"
        metadata_str += f"モード: {self.mode}\n"
        metadata_str += "Parameters:\n"

        # parametersパラメータの値を取得
        parameters = self.metadata.get('parameters', '')
        if not parameters:
            metadata_str += "    なし\n"
            return metadata_str

        # Negative Prompt以降を削除
        if 'Negative prompt:' in parameters:
            parameters = parameters.split('Negative prompt:')[0].strip()

        # すべての改行を削除
        parameters = ' '.join(parameters.split())

        # カッコ内の文字列を一時的に置換
        import re
        parentheses_content = []
        def replace_parentheses(match):
            parentheses_content.append(match.group(1))
            return f"(__PAREN_{len(parentheses_content)-1}__)"

        # カッコ内の文字列を置換
        parameters = re.sub(r'\((.*?)\)', replace_parentheses, parameters)

        # カンマの連続を1つにまとめる
        parameters = re.sub(r',\s*,+', ',', parameters)

        # カンマとBREAKの後に改行を追加
        parameters = parameters.replace(',', ',\n')
        parameters = parameters.replace('BREAK', 'BREAK\n\n')  # BREAKの後に改行を2つ追加

        # 置換したカッコ内の文字列を元に戻す
        for i, content in enumerate(parentheses_content):
            parameters = parameters.replace(f"(__PAREN_{i}__)", f"({content})")

        # 行頭のスペースを削除し、4スペースのインデントを追加
        parameters = '\n'.join('    ' + line.lstrip() for line in parameters.split('\n'))

        # パラメータ値を表示
        if parameters:
            metadata_str += parameters
        else:
            metadata_str += "    なし"

        return metadata_str


class RotatedButton(QPushButton):
    """90度回転したボタンクラス"""
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(27, 100)
        self.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # ボタンの背景を描画
        if self.isDown():
            painter.fillRect(self.rect(), QColor("#b71c1c"))
        elif self.underMouse():
            painter.fillRect(self.rect(), QColor("#d32f2f"))
        else:
            painter.fillRect(self.rect(), QColor("#f44336"))
        
        # テキストを90度回転して描画
        painter.translate(self.width() / 2, self.height() / 2)
        painter.rotate(90)
        painter.translate(-self.height() / 2, -self.width() / 2)
        
        # フォントを設定
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        
        # テキストを中央揃えで描画
        painter.setPen(QColor("white"))
        painter.drawText(0, 0, self.height(), self.width(),
                        Qt.AlignmentFlag.AlignCenter, self.text())


class ImageViewer(QMainWindow):
    """画像ビューアーのメインウィンドウ"""

    def __init__(self, target_path: Path) -> None:
        super().__init__()
        self.file_manager = ImageFileManager(target_path)
        self._setup_ui()
        self._show_current_image()

    def _setup_ui(self) -> None:
        """UIの初期設定"""
        self.setWindowTitle("PNG Viewer")
        self.setGeometry(100, 100, 1200, 600)

        # アプリケーション全体のスタイルを設定
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTextEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                line-height: 1.5;
            }
            QLabel {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)

        # メインウィジェットとレイアウトの設定
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        layout.setSpacing(16)  # ウィジェット間の間隔を設定
        layout.setContentsMargins(16, 16, 16, 16)  # マージンを設定

        # 画像表示用ラベル
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setFixedSize(800, 600)  # サイズを固定
        self.image_label.setStyleSheet("""
            QLabel {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        self.image_label.mousePressEvent = self._handle_image_click
        layout.addWidget(self.image_label)

        # 中央のボタン配置用レイアウト
        center_layout = QVBoxLayout()
        center_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 削除ボタンの作成
        delete_button = RotatedButton("Delete")
        delete_button.clicked.connect(self._delete_current_image)
        center_layout.addWidget(delete_button)
        
        layout.addLayout(center_layout)

        # メタデータ表示用テキストエリア
        self.metadata_text = QTextEdit()
        self.metadata_text.setReadOnly(True)
        self.metadata_text.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.metadata_text.customContextMenuRequested.connect(self._handle_context_menu)
        self.metadata_text.setMinimumWidth(400)
        self.metadata_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #333333;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
                line-height: 1.5;
            }
        """)
        self.metadata_text.installEventFilter(self)
        layout.addWidget(self.metadata_text)

    def _show_current_image(self) -> None:
        """現在の画像を表示"""
        
        current_file = self.file_manager.get_current_file()
        if not current_file:
            return

        # 画像を一度だけ開く
        with Image.open(current_file) as pil_image:
            # メタデータの取得
            metadata = ImageMetadata(current_file, pil_image)
            self.metadata_text.setText(metadata.get_formatted_metadata())

            # PIL画像をQPixmapに変換
            # PIL画像をバイト配列に変換
            if pil_image.mode == "RGBA":
                format = QImage.Format.Format_RGBA8888
            else:
                format = QImage.Format.Format_RGB888
                pil_image = pil_image.convert("RGB")

            # 画像データをバイト配列として取得
            image_data = pil_image.tobytes("raw", pil_image.mode)
            
            # QImageを作成
            qimage = QImage(
                image_data,
                pil_image.width,
                pil_image.height,
                pil_image.width * len(pil_image.mode),
                format
            )

            # QPixmapに変換
            pixmap = QPixmap.fromImage(qimage)
            scaled_pixmap = pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)

    def _handle_image_click(self, event) -> None:
        """画像のクリックイベントを処理"""
        # 画像の幅を取得
        image_width = self.image_label.width()
        # クリック位置が画像の右半分か左半分かを判定
        if event.position().x() > image_width / 2:
            # 右半分をクリックした場合、次の画像へ
            if self.file_manager.next_file():
                self._show_current_image()
        else:
            # 左半分をクリックした場合、前の画像へ
            if self.file_manager.previous_file():
                self._show_current_image()

    def _delete_current_image(self) -> None:
        """現在の画像をごみ箱に移動"""
        current_file = self.file_manager.get_current_file()
        if not current_file:
            return

        if self.file_manager.delete_current_file():
            self._show_current_image()
        else:
            self.close()  # ファイルがなくなった場合はアプリを終了

    def keyPressEvent(self, event) -> None:
        """キー入力の処理"""
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() == Qt.Key.Key_Right:
            if self.file_manager.next_file():
                self._show_current_image()
        elif event.key() == Qt.Key.Key_Left:
            if self.file_manager.previous_file():
                self._show_current_image()
        elif event.key() == Qt.Key.Key_Delete:
            self._delete_current_image()

    def _handle_context_menu(self, position) -> None:
        """右クリックメニューの処理"""
        cursor = self.metadata_text.cursorForPosition(position)
        selected_text = self.metadata_text.textCursor().selectedText().strip()
        if selected_text:
            # 範囲選択されている場合はその部分を検索
            search_text = selected_text.replace('\\', '').replace(',', '')
        else:
            # 範囲選択されていない場合は行全体を検索
            cursor.select(cursor.SelectionType.LineUnderCursor)
            line_text = cursor.selectedText().strip()
            search_text = line_text.replace('\\', '').replace(',', '')
        if search_text:
            search_url = f"https://www.google.com/search?q={search_text}&tbm=isch"
            webbrowser.open(search_url)

    def eventFilter(self, obj, event) -> bool:
        """イベントフィルター"""
        if obj == self.metadata_text and event.type() == event.Type.KeyPress:
            # キーイベントを親ウィンドウに転送
            self.keyPressEvent(event)
            return True
        return super().eventFilter(obj, event)


def main() -> None:
    """メイン関数"""
    if len(sys.argv) != 2:
        print("使用方法: python png_viewer.py <ファイルまたはフォルダのパス>")
        sys.exit(1)

    target_path = Path(sys.argv[1])
    if not target_path.exists():
        print("指定されたパスが存在しません。")
        sys.exit(1)

    # PNGファイルが指定された場合、ファイルの存在を確認
    if target_path.is_file() and target_path.suffix.lower() != '.png':
        print("指定されたファイルがPNGファイルではありません。")
        sys.exit(1)

    app = QApplication(sys.argv)
    viewer = ImageViewer(target_path)
    viewer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 