# ad-crawler
A repository to crawl the bids, advertisers, and ads on websites.


### Steps to setup Crawler

1. Clone the repository

2. Install conda for your system

3. Create conda environment and install all the required dependencies in the environment using the .yml file:
   `
   conda env create -f environment.yml
   `
   
5. Run the crawler by provinding relevent arguments:
   `
   python3 ad-crawler.py --profile="<profile-name>" --proxyport=<proxy-port> --chromedatadir="<user-profile-dir>"
   `
   Here,
   - `profile-name` is output directory name for current set of crawls. It could be the kind of persona being crawled for instance `Trained-TV` or 'Untrained-TV'
   - `proxy-port` is any available port on your system that can be used by browsermobproxy for capturing HAR
   - `user-profile-dir` represent path to Google Chrome's user data directory that stores all the stateful information about the current persona being used like cookies, browsing history, etc. You should first create a blank user data directory and use it to login to the TV account through their website and then save the logged in profile in this user data directory. The directory containing this logged in information can here in future when crawling ads at the end of different stages of experimentation.
   
