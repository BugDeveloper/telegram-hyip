import flask_app
from flask_app import saveData


def on_exit(server):
    print('SHUTTING DOWN')
    flask_app.stop_updater()
    saveData()
    print('CONVERSATION DATA SAVED, PRESS CTRL + Z TO SHUT DOWN')
    server.stop()
