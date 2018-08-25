import flask_app
from flask_app import saveData


def worker_exit(server, worker):
    print('SHUTTING DOWN...')
    saveData()
    print('CONVERSATION DATA SAVED')
