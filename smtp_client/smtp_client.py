from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
import smtplib
import os


def smtp_client(stand, port, desc, files, links):
    server = smtplib.SMTP(stand, port)
    # links = [fake.url() for _ in range(random.randint(2, 7))]

    msg = MIMEMultipart()
    msg['From'] = 'smtp_load@avsw.ru'
    msg['To'] = 'receiver@avsw.ru'
    msg['Subject'] = f'SMTP-Load: {desc}'
    msg['Message-ID'] = make_msgid()
    msg.attach(MIMEText('\n'.join(links)))

    for file in files:
        with open(file, 'rb') as fh:
            part = MIMEApplication(fh.read(), Name=os.path.basename(file))
        part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(file)
        msg.attach(part)

    server.sendmail(msg['From'], msg['To'], msg.as_string())