import sys
import os
import subprocess
import shutil
from random import randint
from time import time, sleep, strftime, gmtime
from threading import Thread
from client import Client
from api_client.api_client import APIClient
from icap_client.icap_client import ICAPClient
from smtp_client.smtp_client import SMTPClient


class Load:

    def __init__(self):
        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        _, self.stand = sys.argv
        self.start_time = f'API-Load: {strftime("%d-%m-%Y %H:%M", gmtime())}'
        self.payload = {'force': 'true', 'description': f'API-Load-{self.start_time}'}
        self.x_auth_token = 'e1f0ec3d-e8a0-44fe-ab2e-07a5d2b2e71c'
        self.client = Client(self.stand, self.x_auth_token, host='192.192.192.192')

    def generate_files(self, files_count=200, folder=None):
        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder]) # python RandomFiles_12.py elf,sh 2 \
        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder])
        return os.path.join(self.root_dir, folder, 'RandomFiles')

    def api_client(self):
        iteration = 0
        start_time = time()
        while time() - start_time < 60:
            print('API iteration is:', iteration)
            iteration += 1

            files_folder = self.generate_files(files_count=1, folder='api_client')
            files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

            api_client = APIClient(self.stand, self.x_auth_token)
            api_client.run(files, 1)

    def smtp_client(self):
        iteration = 0
        start_time = time()
        while time() - start_time < 60:
            print('SMTP iteration is:', iteration)
            iteration += 1

            files = self.generate_files(files_count=1, folder='smtp_client')
            files = [os.path.join(files, file) for file in os.listdir(files)]

            new_files = []
            while files:
                count = randint(1, 5)
                new_files.append(files[:count])
                files[:count] = []

            smtp_client = SMTPClient(self.stand, self.x_auth_token)
            smtp_client.run(new_files, 1)

    def icap_client(self): # Не работает
        iteration = 0
        start_time = time()
        while time() - start_time < 60:
            print('ICAP iteration is:', iteration)
            iteration += 1

            files = self.generate_files(files_count=1, folder='icap_client')
            files = [os.path.join(files, file) for file in os.listdir(files)]
            # print('Files:', files)

            start_time = time()
            icap_client = ICAPClient(self.stand, self.x_auth_token)
            icap_client.run(files, 1)
            print('Finish time is:', time() - start_time)

    def run_load(self):
        api = Thread(target=self.api_client)
        smtp = Thread(target=self.smtp_client)
        icap = Thread(target=self.icap_client)

        # api.start()
        smtp.start()
        # icap.start()

        # api.join()
        smtp.join()
        # icap.join()

        # shutil.rmtree('/home/eduard/scripts/api_client/RandomFiles')
        shutil.rmtree('/home/eduard/scripts/smtp_client/RandomFiles')
        # shutil.rmtree('/home/eduard/scripts/icap_client/RandomFiles')


if __name__ == '__main__':
    if len(sys.argv) == 1:
        raise RuntimeError(f'Нужно указать стенд: python3 {sys.argv[0]} domain_or_ip')

    Load().run_load()
