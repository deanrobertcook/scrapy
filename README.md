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
4. Similar to the `scrapyd-docker` tutorial above, we now need to build our image. This time, however, we'll prefix the tag with our Dockerhub info and push the container: 
    ```
    docker build -t deanrobertcook/scrapy-quotes:scrapyd-server -f scrapyd/Dockerfile .
    docker push deanrobertcook/scrapy-quotes:scrapyd-server
    ```
    Then from the droplet, use our run command from before:
    ```
    docker run -d \
    -p 6800:6800 \
    -v data:/var/lib/scrapyd \
    -v /usr/local/lib/python3.7/dist-packages \
    deanrobertcook/scrapy-quotes:scrapyd-server
    ```
5. In this tutorial, we'll use the cdrx/scrapyd-authenticated image as our base

