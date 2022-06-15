from datetime import datetime


def time_now():
    now = datetime.now()
    return f'{now.strftime("%H:%M:%S")}'


def fmt(text):
    try:
        file = open('logs.txt', 'a')
    except:
        file = open('logs.txt', 'w')
    file.write(f'{time_now()} | {text}\n')
    print(f'{time_now()} | {text}')