# Tutorial for Victoria

## How to enter the Docker Container

### 1. Using Shell Scripts (Not Recommended)

```bash
bash ./docker_run -d cpu -v latest
```

### 2. Using VSCode DevContainers (Recommended)

 1. Navigate to the Search Bar at the top of the VSCode Window.
 2. Type the following line, or just wait for the correct suggestion from the autocomplete system.

    ```bash
    > Dev Containers: Reopen in Container
    ```

 3. That's it! This process opens up another instance of VSCode that is running inside your Container. How crazy is that. All the files and folder you see are visible inside your container. You can open up a brand new terminal inside this virtual OS and do anything you want.


## How to run a basic mesa example

Make sure you are inside the Docker Container and run:

```bash
mesa runserver src/mesa-examples-main/examples/virus_on_network/
 ```
