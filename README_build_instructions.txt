pyinstaller --clean --onefile --noconsole --noconfirm ^
  --name=BookReviewSystem ^
  --add-data "src;src" ^
  --hidden-import=core ^
  --hidden-import=core.database ^
  --hidden-import=ui ^
  --hidden-import=ui.screens ^
  --add-data ".env;." ^
  --collect-data sqlalchemy ^
  --collect-data bcrypt ^
  main.py
