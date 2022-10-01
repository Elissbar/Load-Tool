from concurrent.futures import ThreadPoolExecutor


class Client:
    def __init__(self, stand, token, host='192.192.192.192'):
        self.stand = stand
        self.token = token
        self.host = host

    def send(self, *args):
        pass

    # def initializer(self, client):
    #     logging.debug(f'Client is: {client}')

    def run(self, files, threads):
        client = repr(self).split('.')[2].split(' ')[0]
        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.send, files)
