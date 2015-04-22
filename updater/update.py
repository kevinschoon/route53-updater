"""
Simple script to update DNS entries in Route53 for EC2 instances
"""

import logging
from boto import ec2, route53


class Ec2Service:
    def __init__(self, name_match, aws_region='us-east-1'):
        self.aws_region = aws_region
        self.match = name_match
        self.connection = None

    def connect(self):
        self.connection = ec2.connect_to_region(self.aws_region)

    def get_instances(self):
        return [x for x in self.connection.get_only_instances(filters={'tag:Name': self.match})]


class Route53Service:
    def __init__(self, aws_region='us-east-1'):
        self.aws_region = aws_region
        self.connection = None
        self.change_set = list()

    def connect(self):
        self.connection = route53.connect_to_region(region_name=self.aws_region)

    def get_zone(self, zone_name):
        return self.connection.get_zone(zone_name)

    def get_zones_for_domain(self, domain, ip_address):
        ip = ip_address.split('.')
        ptr_name = '.'.join([ip[1], ip[0]]) + '.in-addr.arpa.'

        private_zone = [z for z in self.connection.get_zones()
                        if all([z.name == domain, z.config['PrivateZone'] == 'true'])]
        public_zone = [z for z in self.connection.get_zones()
                       if all([z.name == domain, z.config['PrivateZone'] == 'false'])]
        reverse_zone = [z for z in self.connection.get_zones() if z.name == ptr_name]

        return private_zone[0], public_zone[0], reverse_zone[0]

    def schedule_record(self, name, record_type, zone, ip_address, fqdn):
        change_set = {'name': name, 'record_type': record_type, 'zone': zone, 'ip_address': ip_address, 'fqdn': fqdn}
        self.change_set.append(change_set)

    def get_zone_id(self, zone_name):
        return self.connection.get_zone(zone_name).id

    def commit_changes(self):
        for change_set in self.change_set:
            self.set_record(**change_set)

    @staticmethod
    def get_record(name, record_type, zone):
        record = zone.find_records(name=name, type=record_type)
        logging.info('Search for record {} ({}) returned: {}'.format(name, record_type, record))
        return record

    @staticmethod
    def set_record(name, record_type, zone, ip_address, fqdn):
        print('Setting record: {} {} {} {} {}'.format(name, record_type, zone, ip_address, fqdn))
        if record_type == 'PTR':
            zone.add_record(resource_type=record_type, name=name, value=fqdn, comment='Updated with DNS Updater')
        if record_type == 'A':
            zone.add_record(resource_type=record_type, name=name, value=ip_address, comment='Updated with DNS Updater')


class Route53Updater:
    def __init__(self, name_match='mesos-*', aws_region='us-east-1'):
        self.match = name_match
        self.aws_region = aws_region
        self.ec2 = Ec2Service(name_match=name_match, aws_region=aws_region)
        self.route_53 = Route53Service(aws_region=aws_region)

    def refresh(self):
        self.ec2.connect()
        self.route_53.connect()

    @staticmethod
    def get_fqdn(instance):
        return instance.tags['Name']

    @staticmethod
    def get_ptr(instance):
        return '.'.join(reversed(instance.private_ip_address.split('.'))) + '.in-addr.arpa.'

    @staticmethod
    def get_domain(instance):
        return '.'.join(instance.tags['Name'].split('.')[1:]) + '.'

    def run(self):

        self.refresh()

        instances = self.ec2.get_instances()

        if not instances:
            logging.warning('Could not find any EC2 instances matching: {}'.format(self.match))

        for instance in instances:

            fqdn = self.get_fqdn(instance)
            domain = self.get_domain(instance)
            ptr = self.get_ptr(instance)

            private, public, reverse = self.route_53.get_zones_for_domain(domain, instance.private_ip_address)

            if not self.route_53.get_record(name=fqdn, record_type='A', zone=private):
                self.route_53.schedule_record(name=fqdn, record_type='A', zone=private,
                                              ip_address=instance.private_ip_address, fqdn=fqdn)

            if not self.route_53.get_record(name=ptr, record_type='PTR', zone=reverse):
                self.route_53.schedule_record(name=ptr, record_type='PTR', zone=reverse,
                                              ip_address=instance.private_ip_address, fqdn=fqdn)

            """ For now I will only update internal record sets
            #if public:
            #    if not self.route_53.get_record(name=fqdn, record_type='A', zone=public):
            #        self.route_53.schedule_record(name=fqdn, record_type='A', zone=public)
            """

        self.route_53.commit_changes()
