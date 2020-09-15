[![Build Status](https://travis-ci.org/dtcarls/fantasy_football_chat_bot.svg?branch=master)](https://travis-ci.org/dtcarls/fantasy_football_chat_bot)
[![Come join the chat](https://badges.gitter.im/dtcarls/Lobby.svg)](https://gitter.im/dtcarls/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d8506396005d48d1a52dee114f2c05ae)](https://www.codacy.com/app/dtcarls/ff_bot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=dtcarls/ff_bot&amp;utm_campaign=Badge_Grade)

Like the bot? Star the repository and consider making a donation to buy me a coffee
------
[![paypal](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=ZDLFECJVGG6RG&currency_code=USD&source=url)
* BTC: 3C8SEcDh52iDSYQY55kwELrNWoQRMkXLCR
* ETH: 0xA098c4e8CC1c12422d5B34d6454133190CDdCAC3
* LTC: MHx74YbrHE592ePBbdQ4cL9ZQC15xaAjtM

# ESPN Fantasy Football GroupMe Slack and Discord Chat Bot

This package creates a docker container that runs a GroupMe, Discord, or Slack chat bot to send
ESPN Fantasy Football information to a GroupMe, Discord or Slack chat room.

**What does this do?**

- Sends out the following messages on this schedule:
- Close Scores - Mon - 18:30 east coast time (Games that are within 16 points of eachother to keep an eye on during the Monday night game)
- Scoreboard - Mon,Tue,Fri - 7:30 local time (Current ESPN fantasy scoreboard)
- Trophies- Tue - 7:30 local time (High score, low score, biggest win, closest win)
- Power rankings - Tue -18:30 local time
- Matchups - Thu - 19:30 east coast time (Upcoming matchups)
- Scoreboard - Sun - 16:00, 20:00 east coast time (Current ESPN fantasy scoreboard)

Table of Contents
=================

  * [Setting up GroupMe, Discord, or Slack, and deploying app in Heroku](#setting-up-groupme-discord-or-slack-and-deploying-app-in-heroku)
     * [GroupMe Setup](#groupme-setup)
     * [Slack setup](#slack-setup)
     * [Discord setup](#discord-setup)
     * [Heroku setup](#heroku-setup)
     * [Private Leagues](#private-leagues)
  * [Troubleshooting / FAQ](#troubleshooting--faq)
  * [Getting Started for development and testing](#getting-started-for-development-and-testing)
     * [Installing for development](#installing-for-development)
     * [Environment Variables](#environment-variables)
     * [Running with Docker](#running-with-docker)
     * [Running without Docker](#running-without-docker)
     * [Running the tests](#running-the-tests)

## Setting up GroupMe, Discord, or Slack, and deploying app in Heroku

**Do not deploy 2 of the same bot in the same chat. In general, you should let your commissioner do the setup**

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

### Slack setup

Go to https://slack.com/signin and sign in to the workspace the bot will be in

If you don't have one for your league already, create a new League Channel

Next we will setup the bot for Slack

Go to https://api.slack.com/apps/new

Name the app, and choose the intended workspace from the dropdown.

Select the Incoming Webhooks section on the side.

![](https://i.imgur.com/ziRQCVP.png)

Change the toggle from Off to On.

Select Add New Webhook to Workspace

![](https://i.imgur.com/tJRRrfz.png)

In the Post to dropdown, select the channel you want to send messages to, then
select Authorize.

This page is important as you will need the "Webhook URL" on this page.

![](https://i.imgur.com/mmzhDS0.png)

### Discord setup

Log into or create a discord account

Go to or create a discord server to receive messages in

Open the server settings

![](https://i.imgur.com/bDk2ttJ.png)

Go to Webhooks

![](https://i.imgur.com/mfFHGbT.png)

Create a webhook, give it a name and pick which channel to receive messages in

![](https://i.imgur.com/NAJLv6D.png)

Save the "Webhook URL" on this page

![](https://i.imgur.com/U4MKZSY.png)

### Heroku setup

Heroku is what we will be using to host the chat bot (for free)

**You should not need to enter credit card information for this hosting service for our needs.**
You **may** run out of free hours without a credit card linked. If you decide to link your credit card you will have enough free hours for the month for a single application since this more than doubles your available hours. We are not responsible for any charges associated with Heroku.

Go to https://id.heroku.com/login and sign up or login


**!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!**

**Click this handy button:**
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

**!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!**

Go to your dashboard (https://dashboard.heroku.com/apps)
Now you will need to setup your environment variables so that it works for your league. Click Settings at your dashboard. Then click "Reveal Config Vars" button and you will see something like this.

![](https://i.imgur.com/7a1V6v8.png)

Now we will need to edit these variables (click the pencil to the right of the variable to modify)
Note: App will restart when you change any variable so your chat room may be semi-spammed with the init message of "Hi" you can change the INIT_MSG variable to be blank to have no init message. It should also be noted that Heroku seems to restart the app about once a day

- BOT_ID: This is your Bot ID from the GroupMe developers page (REQUIRED IF USING GROUPME)
- SLACK_WEBHOOK_URL: This is your Webhook URL from the Slack App page (REQUIRED IF USING SLACK)
- DISCORD_WEBHOOK_URL: This is your Webhook URL from the Discord Settings page (REQUIRED IF USING DISCORD)
- LEAGUE_ID: This is your ESPN league id (REQUIRED)
- START_DATE: This is when the bot will start paying attention and sending messages to your chat. (2020-09-10 by default)
- END_DATE: This is when the bot will stop paying attention and stop sending messages to your chat. (2020-12-30 by default)
- LEAGUE_YEAR: ESPN League year to look at (2020 by default)
- TIMEZONE: The timezone that the messages will look to send in. (America/New_York by default)
- INIT_MSG: The message that the bot will say when it is started (“Hi” by default, can be blank for no message)
- ESPN_S2: Used for private leagues. See [Private Leagues Section](#private-leagues) for documentation
- SWID: Used for private leagues. See [Private Leagues Section](#private-leagues) for documentation
- ESPN_USERNAME: Used for private leagues. See [Private Leagues Section](#private-leagues) for documentation **Experimental, currently not working**
- ESPN_PASSWORD: Used for private leagues. See [Private Leagues Section](#private-leagues) for documentation **Experimental, currently not working**

After you have setup your variables you will need to turn it on. Navigate to the "Resources" tab of your Heroku app Dashboard.
You should see something like below. Click the pencil on the right and toggle the buton so it is blue like depicted and click "Confirm."
![](https://i.imgur.com/J6bpV2I.png)

You're done! You now have a fully featured GroupMe/Slack/Discord chat bot for ESPN leagues! If you have an INIT_MSG you will see it exclaimed in your GroupMe, Discord, or Slack chat room.

Unfortunately to do auto deploys of the latest version you need admin access to the repository on git. You can check for updates on the github page (https://github.com/dtcarls/ff_bot/commits/master) and click the deploy button again; however, this will deploy a new instance and the variables will need to be edited again.

#### Private Leagues
For private league you will need to get your swid and espn_s2.
You can find these two values after logging into your espn fantasy football account on espn's website.
(Chrome Browser)
Right click anywhere on the website and click inspect option.
From there click Application on the top bar.
On the left under Storage section click Cookies then http://fantasy.espn.com.
From there you should be able to find your swid and espn_s2 variables and values.

There is a new **Experimental (may not work)** option to use a username and password for espn to access private leagues instead of having to use swid and s2.

## Troubleshooting / FAQ

**League must be full.**

The bot isn't working
Did you miss a step in the instructions? Try doing it from scratch again. If still no luck, open an issue (https://github.com/dtcarls/fantasy_football_chat_bot/issues) so the answer can be shared with others.

How are power ranks calculated?
They are calculated using 2 step dominance, as well as a combination of points scored and margin of victory. Weighted 80/15/5 respectively. I wouldn't so much pay attention to the actual number but more of the gap between teams. Full source of the calculations can be seen here: https://github.com/cwendt94/ff-espn-api/commit/61f8a34de5c42196ba0b1552aa25282297f070c5

Is there a version of this for Yahoo/CBS/NFL/[insert other site]?
No, this would require a significant rework for other sites.

I'm not getting the init message
Are you sure you flipped the switch in Heroku to activate the worker (the toggle should be blue)? The other common mistake is misconfigured environment variables.

I keep getting the init message
Remove your init message and it will stop. The init message is really for first setup to ensure it is working.

How do I set another timezone?
Specify your variable https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List

Is there a version of this for Messenger/WhatsApp/[insert other chat]?
No, but I am open to pull requests implementing their API for additional cross platform support.

## Getting Started for development and testing

These instructions will get you a copy of the project up and running
on your local machine for development and testing purposes.

### Installing for development
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

### Environment Variables

- BOT_ID: This is your Bot ID from the GroupMe developers page (REQUIRED IF USING GROUPME)
- SLACK_WEBHOOK_URL: This is your Webhook URL from the Slack App page (REQUIRED IF USING SLACK)
- DISCORD_WEBHOOK_URL: This is your Webhook URL from the Discord Settings page (REQUIRED IF USING DISCORD)
- LEAGUE_ID: This is your ESPN league id (REQUIRED)
- START_DATE: This is when the bot will start paying attention and sending messages to your chat. (2020-09-10 by default)
- END_DATE: This is when the bot will stop paying attention and stop sending messages to your chat. (2020-12-30 by default)
- LEAGUE_YEAR: ESPN League year to look at (2020 by default)
- TIMEZONE: The timezone that the messages will look to send in. (America/New_York by default)
- INIT_MSG: The message that the bot will say when it is started (“Hi” by default, can be blank for no message)
- ESPN_S2: Used for private leagues. See [Private Leagues Section](#private-leagues) for documentation
- SWID: Used for private leagues. See [Private Leagues Section](#private-leagues) for documentation
- ESPN_USERNAME: Used for private leagues. See [Private Leagues Section](#private-leagues) for documentation **Experimental, currently not working**
- ESPN_PASSWORD: Used for private leagues. See [Private Leagues Section](#private-leagues) for documentation **Experimental, currently not working**

### Running with Docker

Use BOT_ID if using Groupme, DISCORD_WEBHOOK_URL if using Discord, and SLACK_WEBHOOK_URL if using Slack (or multiple to get messages in multiple places)

```bash
>>> export BOT_ID=[enter your GroupMe Bot ID]
>>> export WEBHOOK_URL=[enter your Webhook URL]
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

Use BOT_ID if using Groupme, DISCORD_WEBHOOK_URL if using Discord, and SLACK_WEBHOOK_URL if using Slack (or multiple to get messages in multiple places)

```bash
>>> export BOT_ID=[enter your GroupMe Bot ID]
>>> export WEBHOOK_URL=[enter your Webhook URL]
>>> export LEAGUE_ID=[enter ESPN league ID]
>>> export LEAGUE_YEAR=[enter league year]
>>> cd ff_bot
>>> python3 ff_bot/ff_bot.py
```

### Running the tests

Automated tests for this package are included in the `tests` directory. After installation,
you can run these tests by changing the directory to the `ff_bot` directory and running the following:

```python3
python3 setup.py test
```
