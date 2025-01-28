import datetime
import telebot
import os

bot = telebot.TeleBot(' ')

def parse_time(log_string):
    timestamp = log_string.split(" ")[0]
    dt = datetime.datetime.fromisoformat(timestamp)
    return dt.strftime("%d %B %Y %H:%M:%S")

def read_logs_file(file_name):
    log_info = []
    with open(file_name) as fd:
        log = fd.readlines()
        for log_string in log:
            log_string = log_string.strip()
            if not log_string:
                continue
            try:
                formatted_time = parse_time(log_string)
                log_string = log_string.replace(log_string.split(" ")[0], formatted_time)
                if "[ERROR]" in log_string:
                    log_info.append(log_string)
            except ValueError:
                log_info.append(f"Ошибка: {log_string}")
    return "\n".join(log_info)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop_path, message.document.file_name)
        with open(file_path, 'wb') as new_file:
            new_file.write(downloaded_file)

        log_info = read_logs_file(file_path)

        if len(log_info) > 4096:
            with open("logs.txt", "w") as file:
                file.write(log_info)
            with open("logs.txt", 'rb') as file:
                bot.send_message(message.chat.id, "Файл слишком большой (более 4096 символов), держи формат .txt!")
                bot.send_document(message.chat.id, file)
        else:
            bot.send_message(message.chat.id, log_info if log_info else "ОшЫбки в логах не найдены (префиксы ERROR)")

    except Exception as e:
        bot.reply_to(message, e)

bot.polling(none_stop=True, interval=0)
