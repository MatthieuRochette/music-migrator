from os import system

system("pip install -r requirements.txt")
system("pyinstaller -F --distpath ./ --name music-migrator main.py")