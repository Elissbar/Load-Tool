import requests
import os
from time import time, sleep, strftime, gmtime
from multiprocessing import Pool
# from load import Load
from client import Client


class APIClient(Client):

    def __init__(self, *args):
        super().__init__(*args)
        # self.stand = stand
        self.description = f'API-Load: {strftime("%d-%m-%Y %H:%M", gmtime())}'
        # self.token = token
        # self.threads = threads
        # self.files = files
        # self.load = Load()

    def send(self, file):
        sleep(5)
        payload = {'force': 'true', 'description': self.description}
        headers = {'X-Auth-Token': self.token}
        data = {"file": open(file, 'rb')}

        response = requests.post(
            f'https://{self.stand}/api/v1/submit/file',
            verify=False,
            headers=headers,
            data=payload,
            files=data)
        print(response.status_code)
        os.remove(file)
        return response.status_code

    # def execute_send_files(self):
    #     with Pool(self.threads) as p:
    #         p.map(self.send_files, self.files)
