import datetime


class Ban:

    BAN_MULTIPLIER = 3

    def __init__(self):
        self.banned_until = datetime.datetime.now()
        self.ban_hours = 1

    def set_banned(self):
        self.banned_until = datetime.datetime.now() + datetime.timedelta(hours=self.ban_hours)
        ban_hours = self.ban_hours
        self.ban_hours = self.ban_hours * self.BAN_MULTIPLIER
        return ban_hours

    def banned(self):
        return self.banned_until > datetime.datetime.now()
