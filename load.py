import sys
import os
import subprocess
from random import randint
from time import time, sleep, strftime, gmtime
from threading import Thread
from api_client.api_client import ApiClient
from icap_client.icap_client import ICAPClient
from smtp_client.smtp_client import SMTPClient


class Load:

    def __init__(self):
        self.root_dir = os.path.abspath(os.path.dirname(__file__))
        _, self.stand = sys.argv
        self.start_time = f'API-Load: {strftime("%d-%m-%Y %H:%M", gmtime())}'
        self.payload = {'force': 'true', 'description': f'API-Load-{self.start_time}'}
        self.x_auth_token = 'f719284d-e2e7-4030-b342-3bbce631f3a9'

    def generate_files(self, files_count=200, folder=None):
        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder]) # python RandomFiles_12.py elf,sh 2 \
        subprocess.call(['python3', 'RandomFiles_12.py', 'docx,xlsx,pdf,sh,html', str(files_count), folder])
        return os.path.join(self.root_dir, folder, 'RandomFiles')

    def api_client(self):
        files_folder = self.generate_files(files_count=2, folder='api_client')
        files = [os.path.join(files_folder, file) for file in os.listdir(files_folder)]

        api_client = ApiClient(self.stand, self.x_auth_token, 1, files)
        api_client.execute_send_files()

    def smtp_client(self):
            files = self.generate_files(files_count=200, folder='smtp_client')
            files = [os.path.join(files, file) for file in os.listdir(files)]

            new_files = []
            while files:
                count = randint(1, 5)
                new_files.append(files[:count])
                files[:count] = []

            smtp_client = SMTPClient(self.stand, files=new_files, threads=1)
            smtp_client.execute_send_files()

    def icap_client(self): # Не работает
        files = self.generate_files(files_count=200, folder='icap_client')
        files = [os.path.join(files, file) for file in os.listdir(files)]
        # print('Files:', files)

        start_time = time()
        icap_client = ICAPClient(self.stand, threads=1, files=files, host='192.192.192.192')
        icap_client.execute_send_files()
        # print('Finish time is:', time() - start_time)

    def run_load(self):
        api = Thread(target=self.api_client)
        smtp = Thread(target=self.smtp_client)
        icap = Thread(target=self.icap_client)

        api.run()
        smtp.run()
        icap.run()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        raise RuntimeError(f'Нужно указать стенд: python3 {sys.argv[0]} domain_or_ip')
    # print(Load().stand)
    Load().generate_files(folder='api_client')
    # Load().api_client()
    # Load().icap_client()
    # Load().smtp_client()
