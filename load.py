import sys
import os
import subprocess
import shutil
from random import randint
from time import time, sleep, strftime, gmtime
from threading import Thread
from api_client.api_client import APIClient
from icap_client.icap_client import ICAPClient
from smtp_client.smtp_client import SMTPClient
import warnings
import logging
warnings.filterwarnings("ignore")


logging.getLogger().name = 'load'
logging.basicConfig(
    format='%(asctime)s -- %(threadName)s -- %(name)s -- %(message)s',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('log_file.txt', mode='w'),
        # logging.StreamHandler()
    ]
)


class Load:

    def __init__(self):
        print(sys.argv)
        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        _, self.stand = sys.argv[:2]
        self.duration = int(sys.argv[2]) if len(sys.argv) > 2 else False
        print('Duration is', self.duration)
        self.start_time = f'API-Load: {strftime("%d-%m-%Y %H:%M", gmtime())}'
        self.payload = {'force': 'true', 'description': f'API-Load-{self.start_time}'}
        self.x_auth_token = 'ae64b514-8183-4a55-8cf2-000e48fc223e'
        self.threads = 2
        self.icap_port = 1344

    def generate_files(self, files_count=200, folder=None):
        full_path = os.path.join(self.root_dir, folder)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
            logging.debug(f'Create folder: {full_path}')

        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder])
        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder])
        return os.path.join(self.root_dir, folder)

    def api_client(self, folder_name):
        start_time = time()
        parent_folder = os.path.join('api_client', folder_name)
        while time() - start_time < 60:
        # while self.condition:

            files_folder = self.generate_files(files_count=1, folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            api_client = APIClient(self.stand, self.x_auth_token)
            for file in files:
                logging.debug(f'Send file to {self.stand} via API. Filename is: {os.path.basename(file)}')
                api_client.send(file)

        shutil.rmtree(files_folder)

    def smtp_client(self, folder_name):
        start_time = time()
        parent_folder = os.path.join('smtp_client', folder_name)
        # while time() - start_time < 60:
        # if isinstance(self.duration)
        while self.condition(time(), start_time):

            files_folder = self.generate_files(files_count=1, folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            new_files = []
            while files:
                count = randint(1, 5)
                new_files.append(files[:count])
                files[:count] = []

            smtp_client = SMTPClient(self.stand, self.x_auth_token)
            for list_files in new_files:
                logging.debug(f'Send file to {self.stand} via SMTP. List files is: {list_files}')
                smtp_client.send(list_files)

        shutil.rmtree(files_folder)

    def icap_client(self, folder_name):
        start_time = time()
        parent_folder = os.path.join('icap_client', folder_name)
        # while time() - start_time < 20:
        if isinstance(self.duration, bool):
            condition = lambda x, y: True
        elif isinstance(self.duration, int):
            # condition = f'{time()} - f{start_time} < {self.duration}'
            condition = lambda x, y: x - y < self.duration
        while condition(time(), start_time):

            files_folder = self.generate_files(files_count=1, folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            start_time = time()
            icap_client = ICAPClient(self.stand, self.x_auth_token, self.icap_port, '192.192.192.192')
            for file in files:
                try:
                    logging.debug(f'Try to send file to {self.stand} via ICAP. Filename is: {os.path.basename(file)}')
                    os.remove(file)
                    # icap_client.send(file)
                except ConnectionRefusedError:
                    logging.error(f'ICAP sending error. Stand: {self.stand}. Port: {self.icap_port}')
                    shutil.rmtree(files_folder)
                    return

        shutil.rmtree(files_folder)
        print('Finish time:', time() - start_time)

    def run_load(self):
        for i in range(self.threads):
            api_name, smtp_name, icap_name = f'API_Client_Thread_{i}', f'SMTP_Client_Thread_{i}', f'ICAP_Client_Thread_{i}'

            api = Thread(target=self.api_client, args=(api_name, ), name=api_name)
            smtp = Thread(target=self.smtp_client, args=(smtp_name, ), name=smtp_name)
            icap = Thread(target=self.icap_client, args=(icap_name, ), name=icap_name)

            # api.start()
            # smtp.start()
            icap.start()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        raise RuntimeError(f'Нужно указать стенд: python3 {sys.argv[0]} domain_or_ip')

    Load().run_load()
