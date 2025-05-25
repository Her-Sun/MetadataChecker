cd /d %~dp0
call .\.env\Scripts\activate
python png_viewer.py %1