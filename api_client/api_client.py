import requests
import os
from time import time, sleep, strftime, gmtime
from multiprocessing import Pool
# from load import Load


class ApiClient:

    def __init__(self, stand, token, threads, files, description=f'API-Load: {strftime("%d-%m-%Y %H:%M", gmtime())}'):
        self.stand = stand
        self.description = description
        self.token = token
        self.threads = threads
        self.files = files
        # self.load = Load()

    def send_files(self, file):
        sleep(2)
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

    def execute_send_files(self):
        with Pool(self.threads) as p:

            # while len(os.listdir('/home/eduard/scripts/api_client/RandomFiles')):
            #
            #     if len(os.listdir('/home/eduard/scripts/api_client/RandomFiles')) < 10:
            #         print('Files count is less 10')
            #         self.load.generate_files(files_count=2, folder='/home/eduard/scripts/api_client/')

            p.map(self.send_files, self.files)
