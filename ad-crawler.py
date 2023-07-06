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
import datetime
import codecs
import time
import sys
import os

sys.path.insert(0, './code/')
from FullPageScreenshotCollector import *
from BidCollector import *
from AdCollector import *



ROOT_DIRECTORY = os.getcwd()


def parseArguments():
	# python3 ad-crawler.py --profile="Test" --proxyport=8022 --chromedatadir="/home/yvekaria/.config/google-chrome/ProfileTest"
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
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument("--disable-notifications")
	chrome_options.add_argument("--disable-popup-blocking")
	chrome_options.add_argument("--ignore-ssl-errors=yes")
	chrome_options.add_argument("--ignore-certificate-errors")
	# chrome_options.add_argument("--window-size=1920,1080") #1400,600
	chrome_options.add_argument("--window-size=1536,864")
	chrome_options.add_argument("--start-maximized")
	return chrome_options


def configureProxy(port, profile_dir):
	'''
	Instatiate and start browsermobproxy to collect HAR files and accordingly configure chrome options
	Killing open ports:
		- lsof -i:<port>
		- kill -9 <PID>
	'''
	global ROOT_DIRECTORY;
	try:
		server = Server(os.path.join(ROOT_DIRECTORY, "data", "browsermob-proxy-2.1.4", "bin", "browsermob-proxy"), options={'port': port})
		server.start()
		proxy = server.create_proxy()
	except BaseException as error:
		print("\nAn exception occurred:", traceback.format_exc(), "in configureProxy()")
		# logger.write("\n[ERROR] configureProxy():\n" + str(traceback.format_exc()))
		return None, None, None

	# Instantiate chromedriver options
	chrome_options = getChromeOptionsObject()
	
	# Associate proxy-related settings to the chromedriver
	chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
	chrome_options.add_argument("--ignore-ssl-errors=yes")
	chrome_options.add_argument("--use-littleproxy false")
	chrome_options.add_argument("--proxy=127.0.0.1:%s" % port)
	chrome_options.add_argument("--user-data-dir=%s" % profile_dir)
	
	return server, proxy, chrome_options


def main(args):

	global ROOT_DIRECTORY;

	profile = args.profile
	proxy_port = args.proxyport
	chrome_profile_dir = args.chromedatadir.replace("Default", profile)
	

	# Reading Top 105 Header Bidding supported websites
	# hb_dict stores mapping of hb_domain to hb_rank (tranco_rank)
	hb_dict = readHeaderBiddingSites()

	# Start the proxy server to facilitate capturing HAR file
	server, proxy, chrome_options = configureProxy(proxy_port, chrome_profile_dir)
	if server is None:
		print("Server issue while its initialization.")
		exit()
	print("\nBrowsermob-proxy successfully configured for {} | {}!".format(hb_domain, profile))


	# Start the chromedriver instance
	try:
		driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
	except BaseException as error:
		# print("\nAn exception occurred:", traceback.format_exc(), "while initializing the webdriver for domain:", hb_domain)
		print("\n[ERROR] main()::Webdriver-Intitialization: {}".format(str(traceback.format_exc())))
		exit()
	print("\nChromedriver successfully loaded!")


	for idx, (hb_domain, hb_rank) in enumerate(hb_dict.items()):
		start_time = time.time()
		print(idx, hb_domain, hb_rank)

		experimental_path = os.path.join(ROOT_DIRECTORY, "output", profile, hb_domain)
		if not(os.path.exists(experimental_path)):
			os.makedirs(experimental_path)

		
		# Log issues and crawl progress in this file
		logger = open(os.path.join(experimental_path, str(hb_domain)+"_logs.txt"), "w")
		ct = datetime.datetime.now()
		logger.write("\n\nCrawl Start Time: {} [TS:{}] [{}]".format(ct, ct.timestamp(), hb_domain))


		# Start capturing HAR
		har_filepath = os.path.join(experimental_path, str(hb_domain)+"_har.json")
		try:
			proxy.new_har(har_filepath, options={'captureHeaders': True,'captureContent':True})
		except BaseException as error:
			logger.write("\n[ERROR] main()::HarCaptureStart: {}\n for domain: {} | {}".format(str(traceback.format_exc()), hb_domain, profile))
			pass

		
		# Visit the current domain
		website = "http://" + str(hb_domain)
		try:
			driver.get(website)
		except BaseException as e:
			logger.write("\n[ERROR] main()::ad-crawler: {}\nException occurred while getting the domain: {} | {}.".format(str(traceback.format_exc()), hb_domain, profile))
			server.stop()
			driver.close()
			continue
		# Wait for page to completely load
		sleep(15)
		
		'''
		# Take fullpage screenshot of the webpage
		screenshot_output_path = os.path.join(experimental_path, str(hb_domain)+"_ss.png")
		ss_object = FullPageScreenshotCollector(profile, hb_domain, hb_rank, screenshot_output_path)
		status = ss_object.captureFullScreenshot(driver, logger)
		if status:
			logger.write("\nFull page screnshot successfully captured.")
		else:
			logger.write("\n[ERROR] main()::FullPageScreenshotCollector: {}\nIssue in capturing full page screenshot for {} | {}.".format(str(traceback.format_exc()), hb_domain, profile))
		# Move to the top and wait for dynamically updated ads to completely load
		driver.execute_script("window.scrollTo(0, 0);")
		sleep(5)

		
		# Perform bid collection
		bid_file_path = os.path.join(experimental_path, str(hb_domain)+"_bids.json")
		bid_object = BidCollector(profile, hb_domain, hb_rank, bid_file_path)
		bid_object.collectBids(driver, logger)
		'''
		
		# Read filterlist rules
		f = open(os.path.join(ROOT_DIRECTORY, "data", "EasyList", "easylist.txt"), "r")
		rules = f.read().split("\n")
		f.close()
		rules = [rule[2:] for rule in rules[18:] if rule.startswith("##")]


		# Save DOM of the webpage
		dom_filepath = os.path.join(experimental_path, str(hb_domain)+"_DOM.html")
		fdom = codecs.open(dom_filepath, "w", "utf−8")
		fdom.write(driver.page_source)
		fdom.close()

		
		# Collect ads on the website
		ad_path = os.path.join(experimental_path, "ads")
		if not(os.path.exists(ad_path)):
			os.makedirs(ad_path)

		ad_object = AdCollector(profile, hb_domain, hb_rank, rules, ad_path, logger)
		ad_object.collectAds(driver)


		# Complete HAR Collection and save .har file
		try:
			with open(har_filepath, 'w') as fhar:
				json.dump(proxy.har, fhar, indent=4)
			fhar.close()
			logger.write("\nHAR dump saved for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
		except BaseException as error:
			logger.write("\n[ERROR] main()::HarWriter: {}\nException occured while dumping the HAR for domain: {} | {}".format(str(traceback.format_exc()), hb_domain, profile))
			pass


		end_time = time.time()
		total_time = end_time - start_time
		print("Total time to crawl domain: {} is {}".format(hb_domain, total_time))
		logger.write("\nTotal time to crawl domain: {} is {}\n".format(hb_domain, total_time))

		# End

	server.stop()



if __name__ == "__main__":

	args = parseArguments()
	main(args)

