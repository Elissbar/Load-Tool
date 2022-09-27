from multiprocessing import Pool


class Client:
    def __init__(self, stand, token, host='192.192.192.192'):
        self.stand = stand
        self.token = token
        self.host = host

    def send(self, *args):
        pass

    def run(self, files, threads):
        # with Pool(threads) as p:
        #     p.map(self.send, files)

        # В smtp клиенте не работает с Pool, надо разобраться, либо оставить ThreadPoolExecutor для всех
        from concurrent import futures
        with futures.ThreadPoolExecutor(threads) as executor:
            executor.map(self.send, files)
