FROM python:3.12.1 

WORKDIR /app
COPY discord-game-login-notifier/ .
COPY requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT [ "python3", "-u", "main.py" ]
