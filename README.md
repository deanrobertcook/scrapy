# Automating scrapyd deployments
## Overview
This repo demonstrates a simple scrapyd build and deployment complete with the [quotes spider](https://docs.scrapy.org/en/latest/intro/tutorial.html), all automated using [Github actions](https://docs.github.com/en/actions/learn-github-actions/introduction-to-github-actions) and deployed to a [Digital Ocean "droplet"](https://www.digitalocean.com/products/droplets/). This is a quick tour of the different parts to pay attention to here:

1. `.github/workflows/ci.yml`: where the github actions live. 
2. the `/scrapyd/Dockerfile`
3. `tutorial/spiders/quotes_spider.py` - the code for the spider itself
4. the `scrapy.cfg` file
5. secrets stored in the Github repository settings 
6. my Dockerhub repo
7. my droplet

and that's really it! At a high level, the Github workflow does a few key things: 

1. It first builds the scrapyd-server Docker image, defined by `/scrapyd/Dockerfile` and pushes the resulting image to my Dockerhub repo 
2. It ssh's into the droplet, pulls the image down and replaces the running container with the new image
3. It runs the `scrapyd-deploy` tool that packages the actual spider code and deploys it on the scrapyd server instance we set up.
4. At all key steps it injects environment variables either as build args into the built Docker image or into the environment when starting up the scrapyd-server and deploying spiders.

**Note:** Since the droplet and a Github action are run from different parts of the Internet, the scrapyd-server instance has to be Internet-facing. For this reason, the Dockerfile includes some stuff to provide HTTP basic auth protection to the server, based off of the [scrapyd-authenticated](https://github.com/cdrx/scrapyd-authenticated) Dockerfile.

## The result
1. Fully automatic builds, hosted by Github, that can be triggered by any of [these events](https://docs.github.com/en/actions/reference/events-that-trigger-workflows) - typically on pushing to master or a PR or tagging a commit etc. 
    - **Note:** relevant to scrapy, Github also allows [scheduled events](https://docs.github.com/en/actions/reference/events-that-trigger-workflows#scheduled-events)
2. Fast builds (1-2 minutes on average depending on what can be salvaged from previously cached builds, which is typically a lot)
3. A simple secrets and environment variable injection mechanism (scrapy doesn't make it easy)

## Making the builds fast
Due to the nature of running web scrapers, it very quickly becomes necessary to test and debug from as close to the production environment as possible (e.g., to test proxies, location blocking, bot-detection mechanisms etc.). For this reason, you want the code-push-deploy-test loop to be as small as possible. 

That's why here I've put some effort into:
1. Slimming down the image to make uploading and downloading to the Dockerhub repo faster, e.g. by using a slim base image.
2. Taking advantage of Docker layer caching as well as Github action's caching.

There's more that could be done though. For example:
- Using multistage builds
- Optimizing the python dependencies for `scrapyd-deploy` or
- Prebuilding a docker image with `scrapyd-deploy` ready to go - Github actions could just pull it and run within seconds

### Bypass scrapyd
In the world of containerisation and PaaS, it doesn't make much sense to have a process manager that lives indefinitely inside a container and waits for events to trigger processes: containers themselves are about process management. Using scrapyd in this way is a bit of a double-wrap-burrito in terms of abtractions. 

Things scrapyd provides:
- An API for deploying spiders so they're ready to run, maintaining version numbers across deployments
- An API for starting processes
- Process and resource management
- A web interface
- Logging and storage data related to completed processes

Which, without having to squint too much, looks like a list of features you might find in just about any container orchestration environment (including running a container on your local Docker host).

Ideally, we'd have a docker image that has the basic `scrapy` command-line tool and the code for the spider(s) built into it. Then, whenever you want to run the spider, you fire up the container somewhere (say, in a lambda function!) and the spider pulls data out of the internet into a stable database located somewhere else. 

This project arose out of the need to simplify a scrapyd deployment, and so being able to respond to scrapyd API commands is essential as a first step.

If you're building a scraper project from sratch, [here's a very slim Docker image](https://github.com/aciobanu/docker-scrapy/blob/master/Dockerfile) that contains just spider code and executes `scrapy` more-or-less as [scrapyd does](https://github.com/aciobanu/docker-scrapy/blob/master/Dockerfile). With a little tinkering, you could bundle your own spider in there and have it run as the default docker command.

## Useful local commands for testing

### Build
```
docker build -t quotes-scrapyd:latest -f scrapyd/Dockerfile .
```
Due to the way that our spider's dependencies need to be installed on the scrapyd server (why?), we need to make the `requirements.txt` file for our spider code visible to the Dockerfile at build time. Hence why we're building from the parent directory and using the -f arg. 

### Run
```bash
docker run -d \
-p 6800:6800 \
-v data:/var/lib/scrapyd \
-v /usr/local/lib/python3.7/dist-packages \
-e USERNAME=<username> -e PASSWORD=<passsword>
quotes-scrapyd
```
The `USERNAME` and `PASSWORD` environment variables are picked up by the HTTP basic auth layer protecting the scrapdy server. 

### Deploying spiders
Be sure to update the `scrapy.cfg` with the correct url for the scrapyd API, as well as the username and password:
```
[settings]
default = tutorial.settings

[deploy]
project = tutorial
url = http://<scrapyd_ip>:6800/
username = <username>
password = <password>
```
then run:
```
scrapyd-client deploy
```

### Schedule a spider
```
curl -u <username>:<password> http://<scrapyd_ip>:6800/schedule.json -d project=tutorial -d spider=quotes
```

### Check the logs
visit `http://<scrapyd_ip_here>:6800/`, pass in `<username>` and `<password>` and click around.
