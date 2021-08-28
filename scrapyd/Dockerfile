# Assumes building from parent directory using:
# docker build -t quotes-scrapyd -f scrapyd/Dockerfile .

# For some reason I've yet to understand, the scrapyd server
# needs to have all the dependencies of the spiders installed.
# I have no idea what the deploy step does then...

FROM vimagick/scrapyd:py3

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

