FROM python:3.12.1 

WORKDIR /app
COPY discord-game-login-notifier/ .
COPY requirements.txt .
COPY rcon-cli /usr/local/bin/
RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "-u", "main.py" ]
