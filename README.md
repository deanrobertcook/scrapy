# Create a docker image with scrapyd and get a spider running on it

```
git checkout scrapyd-docker
```

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
```
git checkout scrapyd-digital-ocean
```
1. Sign up for and create a droplet on digital ocean. Droplets come with Docker preinstalled
2. Create an access token on Dockerhub - save it as a [secret](https://docs.github.com/en/actions/reference/encrypted-secrets). **Note**: the token is not stored on dockerhub, store it somewhere safe. On the free Dockerhub plan, you can also only have one.
3. On the droplet, log into your dockerhub registry using: `docker login -u <dockerhub_username>` and provide the token when prompted
4. Similar to the `scrapyd-docker` tutorial above, we now need to build our image. This time, however, we'll prefix the tag with our Dockerhub info and push the container. Note, that in this tutorial, I've changed the scrapyd Dockerfile to enable HTTP basic auth, based off the [scrapyd-authenticated image](https://github.com/cdrx/scrapyd-authenticated/blob/master/Dockerfile)
    ```
    docker build -t deanrobertcook/scrapy-quotes:scrapyd-server -f scrapyd/Dockerfile .
    docker push deanrobertcook/scrapy-quotes:scrapyd-server
    ```
5. Create another secret in the repository which will be used to authenticate deploy requests from the scrapyd-client (we'll use this in the upcoming Github action). Then, on the droplet, use our run command from before, this time passing in the password we created
    ```
    docker run -d \
    -p 6800:6800 \
    -v scrapyd:/scrapyd \
    -v /usr/local/lib/python3.7/dist-packages \
    -e USERNAME=quotes-deployer -e PASSWORD=<secret_goes_here> \
    deanrobertcook/scrapy-quotes:scrapyd-server
    ```
    Also ensure that the authentication values match in the `scrapy.cfg` file

    **TODOs:** 
    - Add the environment variables to the docker file when building using Github actions (see next tutorial).
    - Get the password to the scrapyd-client without saving it in the `scrapy.cfg` file
6. Exposing the scrapyd server: 

