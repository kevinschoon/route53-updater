import argparse
import logging
import asyncio
import os

from updater.updater import Route53Updater

FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.getLogger(__name__)

UPDATER_LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'INFO')
UPDATER_NAME_MATCH = os.getenv('NAME_MATCH', '')
UPDATER_CYCLE = os.getenv('CYCLE', 15)


def run_event_loop(args):

    loop = asyncio.get_event_loop()
    updater = Route53Updater(name_match=args.match, cycle=args.cycle, daemon_mode=args.daemon)
    loop.call_soon(updater.run, loop)

    loop.run_forever()


def main():
    parser = argparse.ArgumentParser(prog='Route53 Updater', description='Route53 Updater Tool')
    parser.add_argument('-l', '--level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR'], default=UPDATER_LOGGING_LEVEL)

    parser.add_argument('-m', '--match', default=UPDATER_NAME_MATCH)
    parser.add_argument('-c', '--cycle', default=UPDATER_CYCLE)
    parser.add_argument('-d', '--daemon', action='store_true', default=False)
    args = parser.parse_args()

    logging.basicConfig(level=args.level)
    run_event_loop(args)


if __name__ == '__main__':
    main()


