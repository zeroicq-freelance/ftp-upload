#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path
from paramiko import SSHClient, AutoAddPolicy
import pathlib

from credentials import Credentials

# CONFIGURATION
PATH_TO_FILES = Path(r'C:\Users\alexey\dev\ftp-upload\txt')
FILENAMES = [
    'protowords.txt',
    'synonyms.txt',
    'synonyms_querytime.txt'
]
CMD = 'salam'

live_credentials = Credentials(
    host='ip',
    user='aaa',
    port=220,
    password='bbb',
    paths=[
        '/var/solr/data/trenddeko/conf',
        '/var/solr/data/trenddeko_swap/conf'
    ]
)
editorial_credentials = Credentials(
    host='localhost',
    port=2222,
    user='user',
    password='pass',
    paths=[
        '/var/solr/data/trenddeko/conf',
        '/var/solr/data/trenddeko_swap/conf'
    ]
)
# END OF CONFIGURATION

LIVE_TYPE = 'live'
EDITORIAL_TYPE = 'redaktionsystem'

cur_dir = pathlib.Path(__file__).parent.absolute()
logging.basicConfig(
    filename=cur_dir / 'log.txt',
    level=logging.DEBUG,
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'
)


def main(target_type: str):

    if target_type == LIVE_TYPE:
        creds = live_credentials
    else:
        creds = editorial_credentials

    ssh_client = SSHClient()
    try:
        ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        ssh_client.connect(
            hostname=creds.host,
            port=creds.port,
            username=creds.user,
            password=creds.password,
        )

        ftp_client = ssh_client.open_sftp()
        for server_path in creds.paths:
            for filename in FILENAMES:
                file_path = PATH_TO_FILES / filename
                if not file_path.is_file():
                    logging.info(f'{file_path} is not a file. Skipping.')
                    continue
                ftp_client.put(file_path, server_path + '/' + filename)
        ftp_client.close()

        stdin, stdout, stderr = ssh_client.exec_command(CMD)
        out = stdout.readlines()
        if out:
            logging.info(*out)

        errors = stderr.readlines()
        if errors:
            logging.error(*errors)

    finally:
        ssh_client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload files to FTP and execute command')
    parser.add_argument('target_type', choices=[LIVE_TYPE, EDITORIAL_TYPE])
    args = parser.parse_args()
    target_type = args.target_type
    logging.debug(target_type)
    main(target_type)
