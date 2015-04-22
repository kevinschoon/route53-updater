"""
CLI Interface to Route53Updater
"""

import argparse
import logging
import asyncio
import os

from updater.status import StatusWrapper
from updater.update import Route53Updater

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.getLogger(__name__)

UPDATER_LOGGING_LEVEL = os.getenv('UPDATER_LOGGING_LEVEL', 'INFO')
UPDATER_NAME_MATCH = os.getenv('UPDATER_NAME_MATCH', '')
UPDATER_CYCLE = os.getenv('UPDATER_CYCLE', 15)
UPDATER_REGION = os.getenv('UPDATER_REGION', 'us-east-1')


def run_event_loop(args):

    updater = Route53Updater(args.match, args.region)

    loop = asyncio.get_event_loop()
    s = StatusWrapper(loop, updater, cycle=args.cycle)
    loop.call_soon(s.schedule_check)
    loop.run_until_complete(s.init())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass


def main():
    parser = argparse.ArgumentParser(prog='Route53 Updater', description='Route53 Updater Tool')
    parser.add_argument('-l', '--level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR'], default=UPDATER_LOGGING_LEVEL)

    parser.add_argument('-m', '--match', default=UPDATER_NAME_MATCH)
    parser.add_argument('-c', '--cycle', default=UPDATER_CYCLE)
    parser.add_argument('-r', '--region', default=UPDATER_REGION)
    args = parser.parse_args()

    logging.basicConfig(level=args.level)
    run_event_loop(args)


if __name__ == '__main__':
    main()


