"""
Status module for Route53 Updater.
When running in daemon mode this module will return an HTTP status code for use with job scheduling tools like Marathon.
"""

import logging
import asyncio
import json
from aiohttp import web


class StatusWrapper:
    """
    Class to provide a status endpoint for the Route53 Updater
    """
    def __init__(self, loop, updater, cycle=120, listen_address='0.0.0.0', listen_port=8888):
        self.loop = loop
        self.cycle = cycle  # Schedule the updater class to run every <cycle> seconds in the future.
        self.updater = updater
        self.listen_address = listen_address
        self.listen_port = listen_port
        self.running = False
        self.start_time = 0

    def call_updater(self):
        self.running = True
        self.start_time = self.loop.time()
        self.updater.run()  # Blocking
        self.running = False

    def schedule_check(self):
        if not self.running:  # Prevent multiple instances from running if the call takes longer than self.cycle
            logging.info('Running Route53 Updater')
            self.loop.run_in_executor(None, self.call_updater)
        self.loop.call_later(self.cycle, self.schedule_check)

    @asyncio.coroutine
    def get_status(self, request):
        logging.info('Processing status request: {}'.format(request))
        run_time = self.loop.time() - self.start_time
        return web.Response(body=json.dumps({'is_running': self.running, 'run_time': run_time}).encode('UTF-8'))

    @asyncio.coroutine
    def init(self):
        app = web.Application(loop=self.loop)
        app.router.add_route('GET', '/status', self.get_status)

        server = yield from self.loop.create_server(app.make_handler(), self.listen_address, self.listen_port)
        logging.info('Status server running @ {}:{}'.format(self.listen_address, self.listen_port))

        return server
