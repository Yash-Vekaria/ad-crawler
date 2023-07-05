from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium import webdriver
import selenium

# from pyvirtualdisplay import Display
from browsermobproxy import Server
from time import sleep
import pandas as pd
import traceback
import argparse
import sys
import os

sys.path.insert(0, './code/')
from FullPageScreenshotCollector import *
import BidCollector
import AdCollector



ROOT_DIRECTORY = os.getcwd()


def parseArguments():
	# python3 ad-crawler.py --profile="Test" --proxyport=8022 --chromedatadir="/Users/yvekaria/Library/Application Support/Google/Chrome/ProfileTest"
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--profile", type=str, required=True, help="Enter the type of profile being crawled. Valid inputs are ['TV-Blank', 'TV-Trained', 'HB-Checker']")
	parser.add_argument("-px", "--proxyport", type=int, required=True, help="Enter the port on which browsermob-proxy is to be run.")
	parser.add_argument("-c", "--chromedatadir", type=str, required=True, help="Enter the Chrome's data directory path: Open Chrome's latest stable version installed => Type chrome://version => Input 'Profile Path' without")
	args = parser.parse_args()
	return args


def readHeaderBiddingSites():
	global ROOT_DIRECTORY;
	filepath = os.path.join(ROOT_DIRECTORY, "data", "hb_domains.csv")
	df_hb = pd.read_csv(filepath)
	return {str(df_hb.iloc[i]["tranco_domain"]): int(df_hb.iloc[i]["tranco_rank"]) for i in range(len(df_hb)) if bool(df_hb.iloc[i]["hb_status"])}


def getChromeOptionsObject():
	chrome_options = Options()
	# chrome_options.add_argument("--headless")
	chrome_options.add_argument('--no-sandbox')
	chrome_options.add_argument('--disable-dev-shm-usage')
	chrome_options.add_argument("--disable-notifications")
	chrome_options.add_argument("--disable-popup-blocking")
	chrome_options.add_argument('--ignore-ssl-errors=yes')
	chrome_options.add_argument('--ignore-certificate-errors')
	chrome_options.add_argument("--window-size=1280,720")
	chrome_options.add_argument("--start-maximized")
	return chrome_options


def configureProxy(port, profile_dir, logger):
	'''
	Instatiate and start browsermobproxy to collect HAR files and accordingly configure chrome options
	'''
	global ROOT_DIRECTORY;
	try:
		server = Server(os.path.join(ROOT_DIRECTORY, "data", "browsermob-proxy-2.1.4", "bin", "browsermob-proxy"), options={'port': port})
		server.start()
		proxy = server.create_proxy()
	except BaseException as error:
		print("\nAn exception occurred:", traceback.format_exc(), "in configureProxy()")
		logger.write("\n[ERROR] configureProxy():\n" + str(traceback.format_exc()))
		return None, None

	# Instantiate chromedriver options
	chrome_options = getChromeOptionsObject(profile_dir)
	
	# Associate proxy-related settings to the chromedriver
	chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
	chrome_options.add_argument("--ignore-ssl-errors=yes")
	chrome_options.add_argument("--use-littleproxy false")
	chrome_options.add_argument("--proxy=127.0.0.1:%s" % proxy.port)
	chrome_options.add_argument("--user-data-dir=%s" % profile_dir)
	
	return server, chrome_options


def main(args):

	global ROOT_DIRECTORY;

	profile = args.profile
	proxy_port = args.proxyport
	chrome_profile_dir = args.chromedatadir.replace("Default", profile)
	experimental_path = os.path.join(ROOT_DIRECTORY, "output", profile)
	if not(os.path.exists(experimental_path)):
		os.makedirs(experimental_path)

	# Log issues and crawl progress in this file
	logger = open(os.path.join(experimental_path, "logs.txt"), "w")

	# Reading Top 105 Header Bidding supported websites
	# hb_dict stores mapping of hb_domain to hb_rank (tranco_rank)
	hb_dict = readHeaderBiddingSites()

	for idx, (hb_domain, hb_rank) in enumerate(hb_dict.items()):
		print(idx, hb_domain, hb_rank)

		server, chrome_options = configureProxy(proxy_port, chrome_profile_dir, logger)
		if server is None:
			continue
		logger.write("\nBrowsermob-proxy successfully configured for {} | {}!".format(hb_domain, profile))

		
		# Start the chromedriver instance
		try:
			driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
		except BaseException as error:
			server.stop()
			# print("\nAn exception occurred:", traceback.format_exc(), "while initializing the webdriver for domain:", hb_domain)
			logger.write("\n[ERROR] main()::Webdriver-Intitialization: {}\n for domain: {} | {}".format(str(traceback.format_exc()), hb_domain, profile))
			continue
		logger.write("\nChromedriver successfully loaded for {} | {}!".format(hb_domain, profile))

		
		# Visit the current domain
		website = "http://" + str(hb_domain)
		try:
			driver.get(website)
		except BaseException as e:
			logger.write("\n[ERROR] main()::ad-crawler: {}\nException occurred while getting the domain: {} | {}.".format(str(traceback.format_exc()), hb_domain, profile))
			server.stop()
			driver.quit()
			continue
		# Wait for page to completely load
		sleep(15)
		
		# Take fullpage screenshot of the webpage
		screenshot_output_path = os.path.join(experimental_path, "ss|{}.png".format(hb_domain.replace(".","_")))
		ss_object = FullPageScreenshotCollector(profile, hb_domain, hb_rank, screenshot_output_path)
		status = ss_object.captureFullScreenshot(webdriver, logger)
		if status:
			logger.write("\nFull page screnshot successfully captured.")
		else:
			logger.write("\n[ERROR] main()::FullPageScreenshotCollector: {}\nIssue in capturing full page screenshot for {} | {}.".format(str(traceback.format_exc()), hb_domain, profile))
		# Wait for dynamically updated ads to completely load
		sleep(5)

		
		# Perform bid collection
		bid_file_dir = os.path.join(experimental_path, "bids")
		if not(os.path.exists(bid_file_dir)):
			os.makedirs(bid_file_dir)
		bid_file_path = os.path.join(bid_file_dir, str(hb_domain)+"-bids.json")
		bid_object = BidCollector(profile, hb_domain, hb_rank, bid_file_path)
		bid_object.collectBids(webdriver, logger)

		
		# Read filterlist rules
		f = open(os.path.join(ROOT_DIRECTORY, "data", "EasyList", "easylist.txt"), "r")
		rules = f.read().split("\n")
		f.close()
		rules = [rule[2:] for rule in rules[18:] if rule.startswith("##")]

		
		# Collect ads on the website
		ad_dir = os.path.join(experimental_path, "ads")
		if not(os.path.exists(ad_dir)):
			os.makedirs(ad_dir)
		ad_path = os.path.join(ad_dir, str(hb_domain))
		if not(os.path.exists(ad_path)):
			os.makedirs(ad_path)

		ad_object = AdCollector(profile, hb_domain, hb_rank, rules, ad_path, logger)
		ad_object.collectAds(webdriver)


		# Clicking ?
		# logger.write("\n[ERROR] collectBids()::BidCollector: {}\nException occured in bid collection for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))

		
		# Complete HAR Collection and save .har file
		har_file_dir = os.path.join(experimental_path, "har")
		if not(os.path.exists(har_file_dir)):
			os.makedirs(har_file_dir)
		har_filepath = os.path.join(har_file_dir, str(hb_domain)+"-har.json")
		try:
			with open(har_filepath, 'w') as fhar:
				json.dump(proxy.har, fhar, indent=4)
			fhar.close()
			logger.write("\nHAR dump saved for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
		except BaseException as error:
			logger.write("\n[ERROR] main()::ad-crawler: {}\nException occured while dumping the HAR for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
			pass

		# End



if __name__ == "__main__":

	args = parseArguments()
	main(args)

