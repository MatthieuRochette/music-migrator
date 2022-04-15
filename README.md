# Music Migrator

Have you ever wanted to change your music streaming platform ?
Well I did, but I had like 7000 titles in my favorites and other playlists.

Transfering manually was out of the question, and the one paid service I tried was purely a waste of 5€.
So here we are.

## Supported migrations:

- From Spotify to Deezer

## Other features

## Install guide
### Requirements
- Python 3.10+ installed
- Pip installed for your Python version

### Common
- Download or clone this repository
- Open a terminal inside the repository root folder
- Go to [the Spotify Developers Dashboard](https://developer.spotify.com/dashboard) to create your own app and use its credentials in the `config.toml` file.

### On windows

- Execute the command `python compile.py`. It creates an executable at the root of the repository.
- You can choose to copy or move the created executable file wherever you want, or leave it there. You can also create a shortcut.

### On Linux
Two options:  
- Just run `python3 main.py` at the root of the repo  
  
or  
  
- Run `make install`, which will create an executable copy of main.py that you can execute.

### Running the program
Music Migrator handles both CLI and GUI use cases.
If you want to run the GUI from the CLI, you can use the `-g` flag.

### Logs
The program always writes logs in the `.music_migrator_logs.txt` file.
When running in the command line, it also prints the logs in `stderr`. You can activate the debug mode, which will not be saved in the log file, only visible in the `stderr`.

## Contribution guide

Do not use `print()` but rather `from music_migrator.utils.custom_logger import logger` for all logging purposes.
Please submit a Pull Request or an Issue if you think you have an interesting addition/remark to make (be it a feature, bug report, suggestion...).
## Authors
- [Matthieu Rochette](https://github.com/MatthieuRochette)
