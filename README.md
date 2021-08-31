# Automating scrapyd deployments
## Overview
This repo demonstrates a simple scrapyd build and deployment complete with the [quotes spider](https://docs.scrapy.org/en/latest/intro/tutorial.html), all automated using [Github actions](https://docs.github.com/en/actions/learn-github-actions/introduction-to-github-actions) and deployed to a [Digital Ocean "droplet"](https://www.digitalocean.com/products/droplets/). Where possible, I have tried to put comments throught the `.github/workflows/ci.yml` and `/scrapyd/Dockerfile`.

This is a quick tour of the different parts to pay attention to here:

1. `.github/workflows/ci.yml`: where the github actions live. 
2. The `/scrapyd/Dockerfile`
3. `tutorial/spiders/quotes_spider.py`
4. the `scrapy.cfg` file
5. Secrets stored in the Github repository settings 
6. My Dockerhub repo
7. My droplet

And that's really it! At a high level, the Github workflow does a few key things: 

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
1. Slimming down the image (makes uploading and downloading to the Dockerhub repo faster)
2. Taking advantage of Docker layer caching as well as Github action's caching

Both of which aim to reduce build or up-and-download times.

## Future ideas
There's more that could be done though. For example:
- Using multistage builds
- More dockerfile hacks
- Improving the container security and reliability
- Optimizing the python dependencies for `scrapyd-deploy`

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

The problem with this is I'm not yet too sure of every function the scrapyd-server provides. Does a scrapy spider behave differently when run alone compared to within scrapyd? Probably at least a little bit? (Why am I only asking myself this now 🤦‍♂️)

At any rate, [here's a very slim Docker image](https://github.com/aciobanu/docker-scrapy/blob/master/Dockerfile) that contains just spider code and executes `scrapy` more-or-less as [scrapyd does](https://github.com/aciobanu/docker-scrapy/blob/master/Dockerfile). With a little tinkering, you could bundle a spider in there and have it run as the default docker command.

## Useful commands
TODO



1. Create your own scrapyd docker image (see `scrapyd/Dockerfile`). Build it using:  
    ```
    docker build -t quotes-scrapyd -f scrapyd/Dockerfile .
    ```
    
2. Run the image somewhere
    - On local Docker host:
    ```bash
    docker run -d \
    -p 6800:6800 \
    -v data:/var/lib/scrapyd \
    -v /usr/local/lib/python3.7/dist-packages \
    quotes-scrapyd
    ```
    
3. Deploy the spiders with `scrapyd-client deploy`
4. Schedule a spider with:
    ```
    scrapyd-client schedule -p tutorial quotes
    ```
    `tutorial` is the project name and `quotes` the spider
5. Check the logs of the spider that just ran - visit `http://localhost:6800/` (or wherever you ran the container)

# Run a secure scrapyd instance from a Digital Ocean Droplet
1. Sign up for and create a droplet on digital ocean. Droplets come with Docker preinstalled
2. Create an access token on Dockerhub - save it as a [secret](https://docs.github.com/en/actions/reference/encrypted-secrets). **Note**: the token is not stored on dockerhub, store it somewhere safe. On the free Dockerhub plan, you can also only have one.
3. On the droplet, log into your dockerhub registry using: `docker login -u <dockerhub_username>` and provide the token when prompted
4. Similar to the `scrapyd-docker` tutorial above, we now need to build our image. This time, however, we'll prefix the tag with our Dockerhub info and push the container. Note, that in this tutorial, I've changed the scrapyd Dockerfile to enable HTTP basic auth, based off the [scrapyd-authenticated image](https://github.com/cdrx/scrapyd-authenticated/blob/master/Dockerfile)
    ```
    docker build -t deanrobertcook/quotes-scrapyd:latest -f scrapyd/Dockerfile .
    docker push deanrobertcook/quotes-scrapyd:latest
    ```
5. Create another secret in the repository which will be used to authenticate deploy requests from the scrapyd-client (we'll use this in the upcoming Github action). Then, on the droplet, use our run command from before, this time passing in the password we created
    ```
    docker run -d \
    -p 6800:6800 \
    -v scrapyd:/scrapyd \
    -v /usr/local/lib/python3.7/dist-packages \
    -e USERNAME=quotes-deployer -e PASSWORD=<secret_here> \
    deanrobertcook/quotes-scrapyd:latest
    ```
    Also ensure that the authentication values match in the `scrapy.cfg` file

    **TODOs:** 
    - Add the environment variables to the docker file when building using Github actions (see next tutorial).
    - Get the password to the scrapyd-client without saving it in the `scrapy.cfg` file
6. Exposing the scrapyd server: ensure that in the `scrapyd/scrapyd.conf` file, that `bind_address= 0.0.0.0` (rebuild the container if necessary at this point) 
7. Deploying: as in the local tutorial, we just need to run `scrapyd-client deploy`, but this time, we have to ensure that in our `scrapy.cfg` file, the project url points to our droplet's public IP address:
    ```
    [settings]
    default = tutorial.settings

    [deploy]
    project = tutorial
    url = http://<droplet_ip_here>:6800/
    ```
8. Schedule a spider: for some reason, the auth settings in `scrapy.cfg` don't get picked up with the `scrapyd-client` when scheduling. It appears to only work for deploying (the fact that it's just a wrapper around `scrapyd-deploy` in this case is telling). Fortunately, it's easy to replace with a basic curl call: 
    ```
    curl -u quotes-deployer:<secret_here> http://<droplet_ip_here>:6800/schedule.json -d project=tutorial -d spider=quotes
    ```

9. Check the job ran, this time navigating to: `http://<droplet_ip_here>:6800/`, authenticating as necessary

# Automatically deploy scrapyd and spiders to droplet on merge to master

1. Set up a Github Action that builds the scrapyd image from the Dockerfile and pushes to Dockerhub

2. Inject environment variables into the Dockerfile. 
    - scrapyd username and password
    - release version and deployment environment (for error logging)

    Testing locally (works...):

    Build
    ```
    docker build --build-arg USERNAME=quotes-deployer --build-arg PASSWORD=<deployer_pw> -t deanrobertcook/quotes-scrapyd:ba1 -f scrapyd/Dockerfile .
    ```

    Run
    ```
    docker run -d \
    -p 6800:6800 \
    -v scrapyd:/scrapyd \
    -v /usr/local/lib/python3.7/dist-packages \
    deanrobertcook/quotes-scrapyd:latest
    ```

    **TODO:**
    - I should probably not pass the password as a build-arg. Instead, store the password as an envvar on the server ahead of time, and reference it by variable name (i.e., close a password variable)

3. Trigger redeploy of scrapyd server on droplet. There are several things to watch for here:
    - Reusing the port: since we keep the port consistent (6800), deployment will fail unless we stop the previous container. Rather than using names, we can look up the old container via the port number, and stop/remove it. See the workflow for how that was done.
    - Memory usage: Should I only stop the containers or remove them? What if we want to look at logs? How much memory do they take up?
    - Pulling changes to the image: the `docker pull` command looks for layers that are different for a given tag and fetches just those. We need to use it before trying to run the container.
    - Deployment speed: where possible, we should make use of caching to ensure that build steps are kept as short as possible. Two candidates are in building the docker images (reusing layers that haven't changed) and in deploying the spiders (caching the python environment for the `scrapyd-deploy` tool, since it will rarely ever change).

4. Set up a Github action that deploys the spiders to the authenticated scrapyd server
    - inject username and password into `scrapy.cfg`
    - install scrapy and scrapyd-client
    - run scrapyd-deploy

5. Run spider and test (see last tutorial)  

