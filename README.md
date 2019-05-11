# ICO DAY

[**Telegram Hyip Bot**](https://t.me/ico_day_bot)

[**Marketing Page**](https://telegra.ph/Dobro-pozhalovat-v-ICO-DAY-05-10)

![](https://telegra.ph/file/ebbd34f093f0afb72c6f5.jpg)

Financial pyramid developed by me, for which I was not paid.

**Python 3.6 required**

**Main features**

- Everyday payments
- Intuitive interface
- Refferals excel export
- Detailed transaction history
- Automated flood detecting and ban system
- Web admin page
- Realtime new refferals, daily income and account top up notifications
- Payments from unknown wallets can be managed in admin section
- Blockcypher integration for payments accepting
- Conversation authsave on app shutdown
- Hi-load

**Main stack**
 - [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
 - [flask](https://github.com/pallets/flask)
 - [peewee](https://github.com/coleifer/peewee)

The motivation behind it is to keep things small and not redundant.

**Notes**

This project has been developed with weak python knowledge, so some parts of my code may look ugly. If I've been developing it now I would:

- Used Decimals over floats
- Created two separate apps (web app preferably Django + REST) and use bot as a GUI
- Used multilanguage strings

**Setup**

Before running the app you need to tweak two configs.

- config.py stores some info which is accessed from different app parts.

- config.json stores private information.

```
{
  "token": "YOUR TELEGRAM TOKEN",
  "admin": {
    "username": "name",
    "password": "pass"
  },
  "blockcypher_key": "YOUR BLOCKCYPHER TOKEN"
}
```

If you wanna use webhook instead of websockets you should place it like this.

```
...
 |___telegram-hyip
|___keys
```

Keys folder must be if the same place with the telegram-hyip project.

**To run** the app just run `python flask_app.py`.

**To shutdown** the app you can use `CTRL + C`, but make sure that it saved all conversation data before pressing `CTRL + C` again.