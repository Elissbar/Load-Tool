import sys
import os
import subprocess
import shutil
import threading
from random import randint
from time import time, sleep, strftime, gmtime
from threading import Thread, enumerate
from client import Client
from api_client.api_client import APIClient
from icap_client.icap_client import ICAPClient
from smtp_client.smtp_client import SMTPClient
import warnings
import logging
warnings.filterwarnings("ignore")

logging.basicConfig(
    format='%(asctime)s -- %(message)s -- %(threadName)s',
    filename='log_file.txt'
)


class Load:

    def __init__(self):
        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        _, self.stand = sys.argv
        self.start_time = f'API-Load: {strftime("%d-%m-%Y %H:%M", gmtime())}'
        self.payload = {'force': 'true', 'description': f'API-Load-{self.start_time}'}
        self.x_auth_token = 'ae64b514-8183-4a55-8cf2-000e48fc223e'
        self.threads = 2
        # self.client = Client(self.stand, self.x_auth_token, host='192.192.192.192')

    def generate_files(self, files_count=200, folder=None):
        full_path = os.path.join(self.root_dir, folder)
        # print('Folder is:', full_path)
        if not os.path.exists(full_path):
            os.makedirs(full_path)

        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder]) # python RandomFiles_12.py elf,sh 2 \
        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder])
        return os.path.join(self.root_dir, folder)

    def api_client(self, folder_name):
        iteration = 0
        start_time = time()
        parent_folder = os.path.join('api_client', folder_name)
        while time() - start_time < 60:
            # print('API iteration is:', iteration)
            iteration += 1

            files_folder = self.generate_files(files_count=1, folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            api_client = APIClient(self.stand, self.x_auth_token)
            # api_client.run(files, 1)
            for file in files:
                api_client.send(file)

        shutil.rmtree(files_folder)

    def smtp_client(self, folder_name):
        iteration = 0
        start_time = time()
        parent_folder = os.path.join('smtp_client', folder_name)
        while time() - start_time < 60:
            # print('SMTP iteration is:', iteration)
            iteration += 1

            files_folder = self.generate_files(files_count=1, folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            new_files = []
            while files:
                count = randint(1, 5)
                new_files.append(files[:count])
                files[:count] = []

            smtp_client = SMTPClient(self.stand, self.x_auth_token)
            for list_files in new_files:

                smtp_client.send(list_files)
            # smtp_client.run(new_files, 1)

        shutil.rmtree(files_folder)

    def icap_client(self, folder_name):
        iteration = 0
        start_time = time()
        parent_folder = os.path.join('icap_client', folder_name)
        while time() - start_time < 20:
            # print('ICAP iteration is:', iteration)
            iteration += 1

            files_folder = self.generate_files(files_count=1, folder=parent_folder)
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]
            # print('Files:', files)

            start_time = time()
            icap_client = ICAPClient(self.stand, self.x_auth_token, '111.111.111.111')
            for file in files:
                try:
                    icap_client.send(file)
                except ConnectionRefusedError:
                    # print('HERE')
                    shutil.rmtree(files_folder)
                    return
            # icap_client.run(files, 1)
            # print('Finish time is:', time() - start_time)

        shutil.rmtree(files_folder)

    def run_load(self):
        for i in range(self.threads):
            api_name, smtp_name, icap_name = f'API_Client_Thread_{i}', f'SMTP_Client_Thread_{i}', f'ICAP_Client_Thread_{i}'

            api = Thread(target=self.api_client, args=(api_name, ), name=api_name)
            smtp = Thread(target=self.smtp_client, args=(smtp_name, ), name=smtp_name)
            icap = Thread(target=self.icap_client, args=(icap_name, ), name=icap_name)

            api.start()
            smtp.start()
            icap.start()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        raise RuntimeError(f'Нужно указать стенд: python3 {sys.argv[0]} domain_or_ip')

    Load().run_load()
