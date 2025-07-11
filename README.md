# ad-crawler
A repository to crawl the bids, advertisers, and ads on websites.

<hr />

If you find this helpful, please cite our paper:
```
@inproceedings{vekaria2024inventory,
  title={The inventory is dark and full of misinformation: Understanding ad inventory pooling in the ad-tech supply chain},
  author={Vekaria, Yash and Nithyanand, Rishab and Shafiq, Zubair},
  booktitle={2024 IEEE Symposium on Security and Privacy (SP)},
  pages={1590--1608},
  year={2024},
  organization={IEEE}
}
```

### Steps to setup Crawler


1. Update Google Chrome to the latest version

2. Clone the repository

3. Install conda (miniconda) for your system from:<br>
   [https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html)

4. Create conda environment and install all the required dependencies in the environment using the .yml file:<br>
   `
   conda env create -f environment.yml
   `<br>
   Commands to activate and deactivate:<br>
   `
   conda activate ad-crawler-env
   `<br>
   `
   conda deactivate
   `

5. Add XVNC and Java Support: <br>
   `
   sudo apt update
   `<br>
   `
   sudo apt install -y tigervnc-standalone-server default-jre wget
   ` <br>

6. Create a directory: `consent-extension` inside the cloned project directory and cd into that directory. Next, clone [Consent-O-Matic](https://github.com/cavi-au/Consent-O-Matic) repository inside `consent-extension`.<br>
   `
   mkdir consent-extension
   `<br>
   `
   cd consent-extension
   `<br>
   `
   git clone https://github.com/cavi-au/Consent-O-Matic.git
   `

7. Set necessary consents by modifying values of variables `D`, `A`, `B`, `E`, `F`, and `X` to either `true` or `false` (default). The meaning of these variables are explained [here](https://github.com/cavi-au/Consent-O-Matic#consent-categories). Set the values of these variables in the dictionary object: `GDPRConfig.defaultValues` present in the following file:<br>
   `
   /consent-extension/Consent-O-Matic/Extension/GDPRConfig.js
   `
   
8. Run the crawler by provinding relevent arguments:<br>
   `
   python3 ad-crawler.py --profile="<profile-name>" --proxyport=<proxy-port> --chromedatadir="<user-profile-dir>"
   `
   Here,
   - `profile-name` is output directory name for current set of crawls. It could be the kind of persona being crawled for instance `Trained-TV` or `Untrained-TV`
   - `proxy-port` is any available port on your system that can be used by browsermobproxy for capturing HAR
   - `user-profile-dir` represent path to Google Chrome's user data directory that stores all the stateful information about the current persona being used like cookies, browsing history, etc. You should first create a blank user data directory and use it to login to the TV account through their website and then save the logged in profile in this user data directory. The directory containing this logged in information can here in future when crawling ads at the end of different stages of experimentation. To figure out the default user data directory of chrome on your system, enter `chrome://version/` in the chrome browser search bar and look for `Profile Path:`.

<hr />

### To crawl inside a docker container

Follow the steps below to perform crawls using a docker:<br>
(The steps 1 & 2 are highlighted for Ubuntu/Linux, but can be performed for other OS as well)

1. Check OS requirements and unistall any previous docker versions (if any):<br> 
   [https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/).

2. Follow the [manual installation method](https://docs.docker.com/engine/install/ubuntu/#install-from-a-package) or any other method from the above page to install docker on your local system.

3. Set globalVar::`DOCKER` to `True` in the `ad-crawler.py` file.

4. Follow steps 1, 2, 5, 6, and 7 from the above normal crawling steps.

5. Build the docker using the command:<br>
   `docker build -t <docker-image> .`<br>
   Example:<br>
   `docker build -t ad-crawler .`

7. Run the docker container:<br>
   ```
   docker run -d -e PYTHONUNBUFFERED=1 -v <ad-crawler-dir>:/root -v <user-profile-dir>:/profile -p <random-unused-port>:<rfbport> --shm-size=10g <docker-image> python3.11 ad-crawler.py -p "<profile-name>" -px <proxy-port> -c "/profile" -mp "/root"
   ```
   Example:<br>
   ```
   docker run -d -e PYTHONUNBUFFERED=1 -v $(pwd):/root -v /home/yvekaria/.config/google-chrome/Test:/profile -p 20000:1212 --shm-size=10g ad-crawler python3.11 ad-crawler.py -p "Test" -px 8022 -c "/home/yvekaria/.config/google-chrome/Test" -mp "/root"
   ```
   Here, `rfbport` is also a random available port whole value should match the value used in `ad-crawler.py`.

9. The flag `-d` in point 6. enables docker container to run in a detached mode from the terminal. To prevent that remove `-d`.

10. To monitor the running docker container use the following commands:<br>
      - To check status: `docker container ls -a | grep <docker-image>`<br>
      - To check logs: `docker container logs -f <container-id>`<br>
      - To delete a docker container: `docker rm -f <container-id>`<br>

<hr />

Please contact `yvekaria@ucdavis.edu` in case of any questions.
