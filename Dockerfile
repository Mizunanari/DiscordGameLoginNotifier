FROM python:3.12.1 

COPY .. ./DiscordGameLoginNotifier
WORKDIR /DiscordGameLoginNotifier
RUN pip install -r requirements.txt

ENTRYPOINT [ "python3","./discord-game-login-notifier/main.py" ]