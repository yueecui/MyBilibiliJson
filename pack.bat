@venv\Scripts\pyinstaller -c --onefile --version-file "VersionInfo"  --workpath "build" --distpath "dist" --icon="res\gem.ico" -y "MyBilibiliJson.py"
@pause