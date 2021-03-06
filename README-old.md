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

