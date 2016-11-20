[![Build Status](https://travis-ci.org/rbarton65/ff_bot.svg?branch=master)](https://travis-ci.org/rbarton65/ff_bot)

# ESPN Fantasy Football GroupMe Bot

This package creates a docker container that runs a GroupMe chat bot to send 
ESPN Fantasy Football information to a GroupMe chat room.

## Getting Started

These instructions will get you a copy of the project up and running 
on your local machine for development and testing purposes.

### Installing
With Docker:
```bash
git clone https://github.com/rbarton65/ff_bot

cd ff_bot

docker build -t ff_bot .
```

Without Docker:

```bash
git clone https://github.com/rbarton65/ff_bot

cd ff_bot

python3 setup.py install
```


## Basic Usage

This gives an overview of all the features of `ff_bot`

### Running with Docker

```bash
>>> export BOT_ID = [enter your GroupMe Bot ID]
>>> cd ff_bot
>>> docker run -e BOT_ID=$BOT_ID ff_bot
```

## Running the tests

Automated tests for this package are included in the `tests` directory. After installation,
you can run these tests by changing the directory to the `ff_bot` directory and running the following:

```python3
python3 setup.py test
```