Shoutout to /u/rbart65 on reddit and rbarton65 on github for creating the original version of the chatbot and the ESPN FF API

[![Build Status](https://travis-ci.org/dtcarls/ff_bot.svg?branch=master)](https://travis-ci.org/dtcarls/ff_bot)

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# ESPN Fantasy Football GroupMe Bot

This package creates a docker container that runs a GroupMe chat bot to send 
ESPN Fantasy Football information to a GroupMe chat room.

## Getting Started

These instructions will get you a copy of the project up and running 
on your local machine for development and testing purposes.

### Installing
With Docker:
```bash
git clone https://github.com/dtcarls/ff_bot

cd ff_bot

docker build -t ff_bot .
```

Without Docker:

```bash
git clone https://github.com/dtcarls/ff_bot

cd ff_bot

python3 setup.py install
```


## Basic Usage

This gives an overview of all the features of `ff_bot`

### Environment Variables

- BOT_ID: This is your Bot ID from the GroupMe developers page (REQUIRED)
- LEAGUE_ID: This is your ESPN league id (REQUIRED)
- START_DATE: This is when the bot will start paying attention and sending messages to GroupMe. (2017-09-05 by default)
- END_DATE: This is when the bot will stop paying attention and stop sending messages to GroupMe. (2017-12-26 by default)
- LEAGUE_YEAR: ESPN League year to look at (2017 by default)
- TIMEZONE: The timezone that the messages will look to send in. (America/New_York by default)
- INIT_MSG: The message that the bot will say when it is started (“Hai” by default, can be blank for no message)

### Running with Docker

```bash
>>> export BOT_ID=[enter your GroupMe Bot ID]
>>> export LEAGUE_ID=[enter ESPN league ID]
>>> export LEAGUE_YEAR=[enter league year]
>>> cd ff_bot
>>> docker run --rm=True \
-e BOT_ID=$BOT_ID \
-e LEAGUE_ID=$LEAGUE_ID \
-e LEAGUE_YEAR=$LEAGUE_YEAR \
ff_bot
```

### Running without Docker

```bash
>>> export BOT_ID=[enter your GroupMe Bot ID]
>>> export LEAGUE_ID=[enter ESPN league ID]
>>> export LEAGUE_YEAR=[enter league year]
>>> cd ff_bot
>>> python3 ff_bot/ff_bot.py
```

## Running the tests

Automated tests for this package are included in the `tests` directory. After installation,
you can run these tests by changing the directory to the `ff_bot` directory and running the following:

```python3
python3 setup.py test
```

## Setting up GroupMe, and deploying app in Heroku

### GroupMe Setup

Go to www.groupme.com and sign up or login

If you don't have one for your league already, create a new "Group Chat"

![](https://i.imgur.com/32ioDoZ.png)

Next we will setup the bot for GroupMe

Go to https://dev.groupme.com/session/new and login

Click "Create Bot"

![](https://i.imgur.com/TI1bpwE.png)

Create your bot. GroupMe does a good job explaining what each thing is.

![](https://i.imgur.com/DQUcuuI.png)

After you have created your bot you will see something similar to this. Click "Edit"

![](https://i.imgur.com/Z9vwKKt.png)

This page is important as you will need the "Bot ID" on this page.You can also send a test message with the text box to be sure it is connected to your chat room.
Side note: If you use the bot id depicted in the page you will spam an empty chat room so not worth the effort

![](https://i.imgur.com/k65EZFJ.png)

### Heroku setup

Heroku is what we will be using to host the chat bot (for free)

**You will never need to enter credit card information for this hosting service for our needs.**

Go to https://id.heroku.com/login and sign up or login

**Click this handy button:**
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

Go to your dashboard (https://dashboard.heroku.com/apps)
Now you will need to setup your environment variables so that it works for your league. Click Settings at your dashboard. Then click "Reveal Config Vars" button and you will see something like this.

![](https://i.imgur.com/7a1V6v8.png)

Now we will need to edit these variables (click the pencil to the right of the variable to modify)
Note: App will restart when you change any variable so your chat room may be semi-spammed with the init message of "Hai" you can change the INIT_MSG variable to be blank to have no init message. It should also be noted that Heroku seems to restart the app about once a day

- BOT_ID: This is your Bot ID from the GroupMe developers page (REQUIRED)
- LEAGUE_ID: This is your ESPN league id (REQUIRED)
- START_DATE: This is when the bot will start paying attention and sending messages to GroupMe. (2017-09-05 by default)
- END_DATE: This is when the bot will stop paying attention and stop sending messages to GroupMe. (2017-12-26 by default)
- LEAGUE_YEAR: ESPN League year to look at (2017 by default)
- TIMEZONE: The timezone that the messages will look to send in. (America/New_York by default)
- INIT_MSG: The message that the bot will say when it is started (“Hai” by default, can be blank for no message)

After you have setup your variables you will need to turn it on. Navigate to the "Resources" tab of your Heroku app Dashboard.
You should see something like below. Click the pencil on the right and toggle the buton so it is blue like depicted and click "Confirm."
![](https://i.imgur.com/J6bpV2I.png)

You're done! You now have a fully featured GroupMe chat bot for ESPN leagues! If you have an INIT_MSG you will see it exclaimed in your GroupMe chat room.

Unfortunately to do auto deploys of the latest version you need admin access to the repository on git. You can check for updates on the github page (https://github.com/dtcarls/ff_bot/commits/master) and click the deploy button again; however, this will deploy a new instance and the variables will need to be edited again.
