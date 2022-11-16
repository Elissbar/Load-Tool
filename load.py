import os
import subprocess
import shutil
from random import randint
from time import time, sleep, strftime, localtime
from threading import Thread
from faker import Faker
import random
from api_client.api_client import file_send, link_send
from icap_client.icap_client import icap_client
from smtp_client.smtp_client import smtp_client
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
        self.duration = int(args.d) * 60
        self.condition = lambda x, y, z: True if self.duration == 0 else x - y < z
        self.threads = args.th
        # self.icap_port = args.icap
        self.lag = args.lag
        self.types = args.types
        self.description = f'{strftime("%d-%m-%Y %H:%M", localtime())}'
        # self.smtp_port = 25
        self.fake = Faker()
        self.ports = {
            'api': 0,
            'link': 0,
            'icap': args.icap,
            'smtp': 25
        }
        self.clients = {
            'api': file_send,
            'link': link_send,
            'icap': icap_client,
            'smtp': smtp_client
        }

    def generate_files(self, files_count=200, folder=None):
        full_path = os.path.join(self.root_dir, folder)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            logging.info(f'Создание папки: {full_path}')

        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder])
        return os.path.join(self.root_dir, folder)

    def run_client(self, thread_name, client):
        print('Client here:', client)
        start_time = time()
        parent_folder = os.path.join(f'{client}_client', thread_name)
        while self.condition(time(), start_time, self.duration):
            if client in ['api', 'icap', 'smtp']:
                files_folder = self.generate_files(files_count=int(50/self.threads), folder=parent_folder)
                files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]
            links = [self.fake.url() for _ in range(random.randint(2, 20))]

            if client == 'link':
                for link in links:
                    if not self.condition(time(), start_time, self.duration):
                        break
                    try:
                        logging.info(f'Отправка ссылки в {self.stand} по API. Ссылка: {os.path.basename(link)}')
                        link_send(stand=self.stand, token=self.x_auth_token, desc=self.description, link=link)
                        sleep(self.lag)
                    except Exception as e:
                        logging.error(
                            f'Ошибка при отправке по API. Стенд: {self.stand}. Токен: {self.x_auth_token}.\nСообщение об ошибке: {e}')
            else:
                if client == 'smtp':
                    new_files = []
                    while files:
                        count = randint(1, 5)
                        new_files.append(files[:count])
                        files[:count] = []
                    files = new_files

                for file in files:
                    if not self.condition(time(), start_time, self.duration):
                        break
                    try:
                        logging.info(f'Отправка файла в {self.stand} по {client.upper()}.')
                        self.clients[client](stand=self.stand, token=self.x_auth_token, desc=self.description, file=file, links=links, port=self.ports[client])
                        if isinstance(file, list):
                            for f in file:
                                os.remove(f)
                        else:
                            os.remove(file)
                        sleep(self.lag)
                    except Exception as e:
                        logging.error(f'Ошибка при отправке по {client.upper()}. Стенд: {self.stand}.\nСообщение об ошибке: {e}')
                        shutil.rmtree(files_folder)
                        return
        shutil.rmtree(parent_folder)


    def run_load(self):
        for i in range(self.threads):
            for tp in self.types:
                print('Type here:', tp)
                thread_name = f'{tp.upper()}_Client_{i}'
                new_thread = Thread(target=self.run_client, args=(thread_name, tp, ), name=thread_name)
                new_thread.start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', help='Адрес стенда', required=True)
    parser.add_argument('-t', help='X-Auth-Token', required=True)
    parser.add_argument('-d', help='Длительность нагрузки в минутах', default=False)
    parser.add_argument('-th', help='Кол-во потоков', type=int, default=1)
    parser.add_argument('-icap', help='Порт ICAP', type=int, default=1344)
    parser.add_argument('-lag', help='Задержка перед отправкой', type=int, default=0)
    parser.add_argument('-types', help='Виды нагрузки', nargs='*', default=['api', 'icap', 'smtp', 'link'])
    args = parser.parse_args()

    Load(args).run_load()
