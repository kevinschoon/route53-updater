Route53-Updater
===============
This is a simple service to update Amazon Route53 DNS names based on an EC2 instance name. It runs as a service and provides a simple REST API for health checking which is intended to be used for job scheduler services like [Marathon]('https://mesosphere.github.io/marathon/docs/').

Credentials
-----------

Your AWS credentials need to be available to the service for it to run. You can either set them in a `~/.boto` file or configure them as environment variables. See the [Boto Getting Started](http://boto.readthedocs.org/en/latest/getting_started.html#configuring-boto-credentials) documentation for more details.

Python 3.4
----------
Python 3.4 is a requirement for running this tool.

Installation
-----

Locally:

```bash
$ cd route53-updater
$ pip install .
```

Build a container:
```bash
$ cd route-53-updater
$ docker build -t route53-updater .
```

Usage
-----

Running locally:
```bash
$ export AWS_ACCESS_KEY_ID=AAA...
$ export AWS_SECRET_ACCESS_KEY=BBB...
$ 53Updater --match "*" # This will match ALL server name tags.
  INFO:root:Running Route53 Updater
  INFO:root:Status server running @ 0.0.0.0:8888
```

Running in a container:
```bash
docker run -p 8888:8888 -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -d route53-udpater 53Updater --match "*"
```

Access the REST API:

**Note**: There is not too much here at the moment.. mostly just for health checking but it will likely be used for scheduling DNS updates in the future.
```bash
$ curl -X GET http://localhost:8888/status
  {"is_running": false, "run_time": 4.0699091240239795}
```
