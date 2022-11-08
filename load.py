import os
import subprocess
import shutil
from random import randint
from time import time, sleep, strftime, gmtime
from threading import Thread
from api_client.api_client import api_client
from icap_client.icap_client import icap_client
from smtp_client.smtp_client import smtp_client
import smtplib
import warnings
import logging
import argparse
warnings.filterwarnings("ignore")


logging.getLogger().name = 'load'
logging.basicConfig(
    format='%(asctime)s -- %(threadName)s -- %(name)s -- %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('log_file.txt', mode='w'),
    ]
)


class Load:

    def __init__(self, args):
        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        self.stand = args.s
        self.x_auth_token = args.t
        self.duration = int(args.d * 60)
        self.condition = lambda x, y, z: True if self.duration is False else x - y < z
        self.threads = args.th
        self.icap_port = args.icap
        self.lag = args.lag
        self.types = args.types
        self.description = f'{strftime("%d-%m-%Y %H:%M", gmtime())}'
        self.smtp_port = 25

    def generate_files(self, files_count=200, folder=None):
        full_path = os.path.join(self.root_dir, folder)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            logging.info(f'Создание папки: {full_path}')

        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder])
        return os.path.join(self.root_dir, folder)

    def api(self, thread_name):
        start_time = time()
        parent_folder = os.path.join('api_client', thread_name)
        while self.condition(time(), start_time, self.duration):

            files_folder = self.generate_files(files_count=int(100/self.threads), folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            for file in files:
                if not self.condition(time(), start_time, self.duration):
                    break
                try:
                    logging.info(f'Отправка файла в {self.stand} по API. Имя файла: {os.path.basename(file)}')
                    api_client(self.stand, self.x_auth_token, self.description, file)
                    os.remove(file)
                    sleep(self.lag)
                except Exception as e:
                    logging.error(
                        f'Ошибка при отправке по API. Стенд: {self.stand}. Токен: {self.x_auth_token}.\nСообщение об ошибке: {e}'
                    )

        shutil.rmtree(files_folder)

    def smtp(self, thread_name):
        start_time = time()
        parent_folder = os.path.join('smtp_client', thread_name)
        while self.condition(time(), start_time, int(self.duration * 60)):

            files_folder = self.generate_files(files_count=int(100/self.threads), folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            new_files = []
            while files:
                count = randint(1, 5)
                new_files.append(files[:count])
                files[:count] = []

            for list_files in new_files:
                if not self.condition(time(), start_time, int(self.duration * 60)):
                    break
                try:
                    logging.info(f'Отправка файла в {self.stand} по SMTP. Порт: {self.smtp_port}')
                    smtp_client(self.stand, self.smtp_port, self.description, list_files)
                    for f in list_files:
                        os.remove(f)
                    sleep(self.lag)
                except smtplib.SMTPSenderRefused as e:
                    logging.error(f'Ошибка при отправке по SMTP. Стенд: {self.stand}. Порт: {self.smtp_port}.\nСообщение об ошибке: {e}')
                    shutil.rmtree(parent_folder)
                    return

        shutil.rmtree(parent_folder)

    def icap(self, thread_name):
        start_time = time()
        parent_folder = os.path.join('icap_client', thread_name)
        while self.condition(time(), start_time, int(self.duration * 60)):

            files_folder = self.generate_files(files_count=int(100/self.threads), folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            for file in files:
                if not self.condition(time(), start_time, int(self.duration * 60)):
                    break
                try:
                    logging.info(f'Отправка файла в {self.stand} по ICAP. Порт: {self.icap_port}')
                    icap_client(self.stand, self.icap_port, self.description[-5:], file)
                    os.remove(file)
                    sleep(self.lag)
                except ConnectionRefusedError as e:
                    logging.error(f'Ошибка при отправке по ICAP. Стенд: {self.stand}. Port: {self.icap_port}.\nСообщение об ошибке: {e}')
                    shutil.rmtree(files_folder)
                    return

        shutil.rmtree(files_folder)

    def run_load(self):
        for i in range(self.threads):
            for tp in self.types:
                thread_name = f'{tp.upper()}_Client_{i}'
                new_thread = Thread(target=__class__.__dict__[tp], args=(self, thread_name, ), name=thread_name)
                new_thread.start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', help='Адрес стенда', required=True)
    parser.add_argument('-t', help='X-Auth-Token', required=True)
    parser.add_argument('-d', help='Длительность нагрузки в минутах', default=False)
    parser.add_argument('-th', help='Кол-во потоков', type=int, default=1)
    parser.add_argument('-icap', help='Порт ICAP', type=int, default=1344)
    parser.add_argument('-lag', help='Задержка перед отправкой', type=int, default=0)
    parser.add_argument('-types', help='Виды нагрузки', nargs='*', default=['api', 'icap', 'smtp'])
    args = parser.parse_args()

    Load(args).run_load()
