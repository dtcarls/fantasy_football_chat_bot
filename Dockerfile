FROM python:3.12.5-slim-bullseye

# Install app
ADD . /usr/src/gamedaybot
WORKDIR /usr/src/gamedaybot
RUN python3 setup.py install

# Launch app
CMD ["python3", "gamedaybot/espn/espn_bot.py"]