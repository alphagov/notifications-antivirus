import os

workers = 4
errorlog = "/home/vcap/logs/gunicorn_error.log"
bind = "0.0.0.0:{}".format(os.getenv("PORT"))
