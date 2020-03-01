FROM python:latest

# Install app
ADD . /usr/src/fantasy_football_bot
WORKDIR /usr/src/fantasy_football_bot
RUN python3 setup.py install

# Launch app
CMD ["python3", "fantasy_football_bot/fantasy_football_bot.py"]