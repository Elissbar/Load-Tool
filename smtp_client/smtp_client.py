from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
import smtplib
import os
from time import time, sleep
from multiprocessing import Pool
from faker import Faker
import random
from client import Client
from time import time, sleep, strftime, gmtime


class SMTPClient(Client):

    def __init__(self, *args):
        super().__init__(*args)
        # self.stand = stand
        # self.files = files
        self.fake = Faker()
        # self.threads = threads
        self.port = 25
        self.description = f'SMTP-Load: {strftime("%d-%m-%Y %H:%M", gmtime())}'
        self.server = smtplib.SMTP(self.stand, self.port)

    def send(self, files):
        # sleep(5)
        links = [self.fake.url() for _ in range(random.randint(2, 7))]
        # print('Files:', len(files), '\n', 'Links:', len(links))

        msg = MIMEMultipart()
        msg['From'] = 'smtp_load@avsw.ru'
        msg['To'] = 'receiver@avsw.ru'
        msg['Subject'] = self.description
        msg['Message-ID'] = make_msgid()

        msg.attach(MIMEText('\n'.join(links)))

        for file in files:
            with open(file, 'rb') as fh:
                part = MIMEApplication(fh.read(), Name=os.path.basename(file))
            part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file)
            msg.attach(part)

        # print('SMTP response', self.server.sendmail(msg['From'], msg['To'], msg.as_string()))
        for file in files:
            os.remove(file)

    # def execute_send_files(self):
        # with Pool(self.threads) as p:
        #     p.map(self.send_letter, self.files)
        # from concurrent import futures
        # with futures.ThreadPoolExecutor(self.threads) as executor:
        #     executor.map(self.send_letter, self.files)
