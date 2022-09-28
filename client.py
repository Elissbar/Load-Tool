from concurrent.futures import ThreadPoolExecutor
from threading import current_thread

# thread_name = current_thread().name

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(threadName)s'
)

log = logging.getLogger('Load')


class Client:
    def __init__(self, stand, token, host='192.192.192.192'):
        self.stand = stand
        self.token = token
        self.host = host

    def send(self, *args):
        pass

    def initializer(self, client):
        logging.debug(f'Client is: {client}')

    def run(self, files, threads):
        client = repr(self).split('.')[2].split(' ')[0]
        # print('Client is:', client)
        with ThreadPoolExecutor(max_workers=threads, initializer=self.initializer, initargs=(client, )) as executor:
            executor.map(self.send, files)
