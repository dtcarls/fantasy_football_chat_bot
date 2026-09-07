FROM python:3.11-slim-bookworm

# Do not write .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /usr/src/gamedaybot

# Install small set of build tools that some packages may require during pip install
RUN apt-get update \
	&& apt-get install -y --no-install-recommends build-essential gcc \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirement files first to leverage Docker cache when dependencies don't change
COPY requirements.txt requirements-test.txt ./

# Allow build to opt-out of test deps to produce a slimmer runtime image
ARG INSTALL_TEST_DEPS=true

# Upgrade pip and install dependencies. Conditionally install test requirements when
# INSTALL_TEST_DEPS is true. Use --no-cache-dir to reduce image size.
RUN python -m pip install --upgrade pip setuptools wheel \
	&& python -m pip install --no-cache-dir -r requirements.txt \
	&& if [ "${INSTALL_TEST_DEPS:-true}" = "true" ] ; then python -m pip install --no-cache-dir -r requirements-test.txt ; fi

# Copy the rest of the application
COPY . .

# Launch app
CMD ["python3", "gamedaybot/espn/espn_bot.py"]