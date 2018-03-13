#!/usr/bin/env python

from __future__ import print_function
import os
from flask.ext.script import Manager, Server
from app import create_app

application = create_app()
manager = Manager(application)
port = int(os.environ.get('PORT', 6016))
manager.add_command("runserver", Server(host='0.0.0.0', port=port))


if __name__ == '__main__':
    manager.run()
