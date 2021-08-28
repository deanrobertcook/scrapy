# Create a docker image with scrapyd and get a spider running on it

```
git co scrapyd-docker
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


