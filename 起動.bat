uv sync
REM callを使って仮想環境をアクティベート
call .\.venv\Scripts\activate.bat 
python SerialController/Window.py
REM 仮想環境の停止
deactivate