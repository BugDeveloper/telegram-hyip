import flask_app
from flask_app import save_data

workers = 5


def on_exit(server):
    print('SHUTTING DOWN')
    flask_app.stop_updater()
    save_data()
    print('CONVERSATION DATA SAVED, PRESS CTRL + Z TO SHUT DOWN')
    server.stop()
