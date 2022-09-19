FROM python:3.9.9-slim-bullseye

# Install app
ADD . /usr/src/gamedaybot
WORKDIR /usr/src/gamedaybot
RUN python3 setup.py install

# Launch app
CMD ["python3", "gamedaybot/ff_bot.py"]