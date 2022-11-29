import os
import subprocess
import shutil
from random import randint
from time import time, sleep, strftime, localtime
from requests.exceptions import Timeout
from threading import Thread
from faker import Faker
from api_client.api_client import file_send, link_send
from icap_client.icap_client import icap_client
from smtp_client.smtp_client import smtp_client
import warnings
import logging
import argparse
warnings.filterwarnings("ignore")

logging.getLogger().name = 'load'
logging.basicConfig(
    format='%(asctime)s -- %(threadName)-14s -- %(name)s -- %(message)s',
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
        self.lag = args.lag
        self.types = args.types
        self.static_only = args.static_only
        self.description = f'{strftime("%d-%m-%Y %H:%M", localtime())}'
        self.fake = Faker()
        self.clients = {
            'api': (file_send, "443"),
            'link': (link_send, "443"),
            'icap': (icap_client, args.icap_port),
            'smtp': (smtp_client, args.smtp_port)
        }
    
    @staticmethod
    def clear(item):
        if isinstance(item, list):
            for f in item:
                os.remove(f)
        else:
            os.remove(item)

    def generate_files(self, files_count=200, folder=None):
        full_path = os.path.join(self.root_dir, folder)
        if os.path.exists(full_path):
            logging.info(f'Удаление папки: {full_path}')
            shutil.rmtree(full_path)

        logging.info(f'Создание папки: {full_path}')
        os.makedirs(full_path)
        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder])
        return full_path


    def take_client(self, thread_name, client):
        start_time = time()
        while self.condition(time(), start_time, self.duration):
            if client == 'link':
                items = [self.fake.image_url() for _ in range(50)]
            else:
                parent_folder = os.path.join(f'{client}_client', thread_name)
                files_folder = self.generate_files(files_count=int(20/self.threads), folder=parent_folder)
                items = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]
                if client == 'smtp':
                    new_files = []
                    while items:
                        count = randint(1, 3)
                        new_files.append(items[:count])
                        items[:count] = []
                    items = new_files

            for item in items:
                if not self.condition(time(), start_time, self.duration):
                    break
                try:
                    func, port = self.clients[client]
                    func(
                        stand=self.stand, 
                        token=self.x_auth_token, 
                        desc=self.description, 
                        item=item, 
                        port=port, 
                        static_only=self.static_only
                    )
                    logging.info(f'Успешная отправка {"файла" if client != "link" else "ссылки"} в {self.stand}.')
                    self.clear(item) if client != 'link' else 0
                    sleep(self.lag)
                except Timeout as e:
                    logging.error(f'Ошибка при отправке по {client.upper()}. Стенд: {self.stand}. Порт: {port}.\nСообщение об ошибке: {e}')
                except Exception as e:
                    logging.error(f'Ошибка при отправке по {client.upper()}. Стенд: {self.stand}. Порт: {port}.\nСообщение об ошибке: {e}')
                    shutil.rmtree(files_folder)
                    return
        if client != 'link':
            shutil.rmtree(files_folder)

    def run(self):
        """
        Параметр th - указывает кол-во потоков для каждого источника ['api', 'icap', 'smtp', 'link']
        (Например: th = 11, источники указаны все ['api', 'icap', 'smtp', 'link'], общее кол-во потоков будет 11 * 4 = 44)

        Если общее кол-во потоков (th * кол-во источников) > максимального кол-ва потоков на процессоре,
        кол-во потоков для каждого источника будет расчитано так: максимальное кол-во потоков / кол-во источников
        """
        max_threads = min(32, os.cpu_count() + 4)
        logging.warning(f'Максимальное кол-во потоков {max_threads}')
        
        client_threads_count = self.threads # Кол-во потоков для каждого клиента
        total_count_threads = self.threads * len(self.types)
        if total_count_threads > max_threads:
            total_count_threads = max_threads
            client_threads_count = int(max_threads / len(self.types)) # Кол-во потоков для каждого клиента, если общее кол-во потоков больше максимального
        logging.warning(f'Кол-во потоков для каждого источника: {client_threads_count}. Общее кол-во потоков: {total_count_threads}')
        
        for i in range(client_threads_count):
            for tp in self.types:
                thread_name = f'{tp.upper()}_Client_{i}'
                new_thread = Thread(target=self.take_client, args=(thread_name, tp, ), name=thread_name)
                new_thread.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', help='Адрес стенда', required=True)
    parser.add_argument('-t', help='X-Auth-Token', default=None)
    parser.add_argument('-d', help='Длительность нагрузки в минутах', default=False)
    parser.add_argument('-icap_port', help='Порт ICAP', type=int, default=1344)
    parser.add_argument('-smtp_port', help='Порт SMTP', type=int, default=25)
    parser.add_argument('-lag', help='Задержка перед отправкой', type=int, default=0)
    parser.add_argument('-types', help='Виды нагрузки', nargs='*', default=['api', 'icap', 'smtp', 'link'])
    parser.add_argument('-static_only', help='Только статика', default=True)
    parser.add_argument('-th', help='Кол-во потоков', type=int, default=1)
    args = parser.parse_args()

    for source in args.types:
        if source not in ['api', 'icap', 'smtp', 'link']:
            raise argparse.ArgumentError(None, f"Указан неверный источник: {source}. Возможные значения: {'[api, icap, smtp, link]'}")
        if source in ['api', 'link'] and not args.t:
            raise argparse.ArgumentError(None, f"При отправку по API (файлов/ссылок) нужно указать X-Auth-Token в параметре -t")
    
    Load(args).run()
