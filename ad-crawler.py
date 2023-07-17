from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium import webdriver
import selenium

# from pyvirtualdisplay import Display
import undetected_chromedriver as uc
from browsermobproxy import Server
from time import sleep
import pandas as pd
import traceback
import argparse
import datetime
import zipfile
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
	chrome_options.add_argument("--window-size=1536,864")
	chrome_options.add_argument("--start-maximized")
	# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
	# chrome_options.add_experimental_option('useAutomationExtension', False)
	chrome_options.add_argument("--disable-notifications")
	chrome_options.add_argument("--disable-popup-blocking")
	chrome_options.add_argument("--ignore-certificate-errors")
	extension_dir = os.path.join(os.getcwd(), "consent-extension", "Consent-O-Matic", "Extension")
	chrome_options.add_argument('--load-extension={}'.format(extension_dir))
	return chrome_options


def managePopups(curr_domain, webdriver_):

	try:
		if "forbes.com" in curr_domain:
			webdriver_.find_element(By.XPATH, '//button[@alt="Scroll Down"]').click()
			sleep(2)
		elif "guardian.co" in curr_domain:
			webdriver_.find_element(By.XPATH, '//button[@data-link-name="choice-cards-buttons-banner-blue : close"]').click()
			sleep(2)
		elif "chron.com" in curr_domain:
			webdriver_.find_element(By.XPATH, '//a[@class="bc-close-button"]').click()
			sleep(2)
		elif "dailymail.co.uk" in curr_domain:
			webdriver_.find_element(By.XPATH, '//div[@id="closeButton"]').click()
			sleep(2)
		elif "goo.ne.jp" in curr_domain:
			webdriver_.find_element(By.XPATH, '//button[@class="webpush-title-close"]').click()
			sleep(2)
		elif "latimes.com" in curr_domain:
			ele = webdriver_.find_element(By.XPATH, '//modality-custom-element[@name="metering-bottompanel"]')
			shadow_ele = ele.find_element(By.CSS_SELECTOR, '#shadow-root')
			shadow_ele.find_element(By.XPATH, '//a[@class="met-flyout-close"]').click()
			driver.switch_to.default_content()
			sleep(2)
		elif "marketwatch.com" in curr_domain:
			webdriver_.find_element(By.XPATH, '//button[@class="close-btn"]').click()
			sleep(2)
		elif "nydailynews.com" in curr_domain:
			webdriver_.find_element(By.XPATH, '//button[@id="onesignal-slidedown-cancel-button"]').click()
			sleep(2)
		elif "sfgate.com" in curr_domain:
			webdriver_.find_element(By.XPATH, '//a[@class="fancybox-item fancybox-close"]').click()
			sleep(2)
		elif "slickdeals.net" in curr_domain:
			webdriver_.find_element(By.XPATH, '//a[@class="sd-emailOnlyRegistrationWithLogin_laterLink"]').click()
			sleep(2)
		elif "wunderground.com" in curr_domain:
			webdriver_.find_element(By.XPATH, '//button/i[@class="material-icons"]').click()
			sleep(2)
		elif "weather.com" in curr_domain:
			click_svg_close_js = '''
			const closeIcon = document.querySelector('section#privacy-data-notice svg');
			closeIcon.dispatchEvent(new MouseEvent('click'));
			'''
			webdriver_.execute_script(click_svg_close_js)
			sleep(2)
	except BaseException as e:
		pass

	try:
		if "sfgate.com" in curr_domain:
			webdriver_.find_element(By.XPATH, '//div[@class="exp-ui__sticky__close-btn"]').click()
			sleep(2)
		elif "slickdeals.net" in curr_domain:
			webdriver_.find_element(By.XPATH, '//button[@data-role="close"]').click()
			sleep(2)
	except BaseException as e:
		pass
	return


def exploreFullPage(webdriver_):
	'''
	Scroll to bottom and back up to the top for all ads to load and become viewable
	'''
	try:
		page_height = int(webdriver_.execute_script("return document.body.scrollHeight"))
		for i in range(1, page_height, 10):
			try:
				webdriver_.execute_script("window.scrollTo(0, {});".format(i))
				sleep(0.025)
			except:
				continue
		sleep(2)
		webdriver_.execute_script("window.scrollTo(0, 0);")
	except:
		pass
	# Wait for new ads to completely load
	sleep(10)
	return


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
	

	# Reading Top 104 Header Bidding supported websites
	# hb_dict stores mapping of hb_domain to hb_rank (tranco_rank)
	hb_dict = readHeaderBiddingSites()

	for idx, (hb_domain, hb_rank) in enumerate(hb_dict.items()):
		
		start_time = time.time()
		print("\n\nStarting to crawl:", idx, hb_domain, hb_rank)

		experimental_path = os.path.join(ROOT_DIRECTORY, "output", profile, hb_domain)
		if not(os.path.exists(experimental_path)):
			os.makedirs(experimental_path)


		# Log issues and crawl progress in this file
		logger = open(os.path.join(experimental_path, str(hb_domain)+"_logs.txt"), "w")
		ct = datetime.datetime.now()
		logger.write("\n\nCrawl Start Time: {} [TS:{}] [{}]".format(ct, ct.timestamp(), hb_domain))
		print("Error logging started ...")


		# Start the proxy server to facilitate capturing HAR file
		server, proxy, chrome_options = configureProxy(proxy_port, chrome_profile_dir)
		if server is None:
			logger.write("Server issue while its initialization.")
			continue
		logger.write("\nBrowsermob-proxy successfully configured for domain: {} | {}!".format(hb_domain, profile))
		print("\nBrowsermob-proxy successfully configured for domain: {} | {}!!".format(hb_domain, profile))


		# Start the chromedriver instance
		try:
			# driver = uc.Chrome(service=Service(ChromeDriverManager().install()), version_main=114, options=chrome_options) #executable_path=‘chromedriver’
			driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
		except BaseException as error:
			# print("\nAn exception occurred:", traceback.format_exc(), "while initializing the webdriver for domain:", hb_domain)
			server.stop()
			logger.write("\n[ERROR] main()::Webdriver-Intitialization: {} for domain: {} | {}".format(str(traceback.format_exc()), hb_domain, profile))
			continue
		logger.write("\nChromedriver successfully loaded!")
		print("\nChromedriver successfully loaded!")


		# Start capturing HAR
		har_filepath = os.path.join(experimental_path, str(hb_domain)+"_har.json")
		try:
			proxy.new_har(har_filepath, options={'captureHeaders': True,'captureContent':True})
		except BaseException as error:
			logger.write("\n[ERROR] main()::HarCaptureStart: {}\n for domain: {} | {}".format(str(traceback.format_exc()), hb_domain, profile))
			pass
		print("Starting HAR Capture")


		# Visit the current domain
		website = "http://" + str(hb_domain)
		try:
			print("Website:", website)
			driver.get(website)
		except BaseException as e:
			logger.write("\n[ERROR] main()::ad-crawler: {}\nException occurred while getting the domain: {} | {}.".format(str(traceback.format_exc()), hb_domain, profile))
			try:
				driver.quit()
				server.stop()
			except:
				print("\n[ERROR] main()::Webdriver-Intitialization: {}".format(str(traceback.format_exc())))
				logger.write("\n[ERROR] main()::Webdriver-Intitialization: {} for domain: {} | {}".format(str(traceback.format_exc()), hb_domain, profile))
				continue
			print("\nChromedriver successfully loaded!")
			continue
		# Wait for page to completely load
		sleep(30)
		print("Visiting and loading webpage ...")


		managePopups(hb_domain, driver)


		exploreFullPage(driver)


		managePopups(hb_domain, driver)

		
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
		print("DOM saved")


		# Perform bid collection
		bid_file_path = os.path.join(experimental_path, str(hb_domain)+"_bids.json")
		bid_object = BidCollector(profile, hb_domain, hb_rank, bid_file_path)
		bid_object.collectBids(driver, logger)
		print("Bid data collected")
		
		
		# Take fullpage screenshot of the webpage
		screenshot_output_path = os.path.join(experimental_path, str(hb_domain)+"_ss-before.png")
		ss_object = FullPageScreenshotCollector(profile, hb_domain, hb_rank, screenshot_output_path)
		status = ss_object.captureFullScreenshot(driver, logger)
		if status:
			logger.write("\nFull page screnshot successfully captured.")
		else:
			logger.write("\n[ERROR] main()::FullPageScreenshotCollector: {}\nIssue in capturing full page screenshot for {} | {}.".format(str(traceback.format_exc()), hb_domain, profile))
		# Move to the top and wait for dynamically updated ads to completely load
		driver.execute_script("window.scrollTo(0, 0);")
		sleep(10)
		print("Fullpage screenshot of the webpage captured")

		
		# Collect ads on the website
		print("Starting to collect ads ...")
		ad_path = os.path.join(experimental_path, "ads")
		if not(os.path.exists(ad_path)):
			os.makedirs(ad_path)

		ad_object = AdCollector(profile, hb_domain, hb_rank, rules, ad_path, logger)
		ad_object.collectAds(driver)
		print("Ad collection complete!")


		# Take fullpage screenshot of the webpage
		screenshot_output_path = os.path.join(experimental_path, str(hb_domain)+"_ss-after.png")
		ss_object = FullPageScreenshotCollector(profile, hb_domain, hb_rank, screenshot_output_path)
		status = ss_object.captureFullScreenshot(driver, logger)
		if status:
			logger.write("\nFull page screnshot successfully captured.")
		else:
			logger.write("\n[ERROR] main()::FullPageScreenshotCollector: {}\nIssue in capturing full page screenshot for {} | {}.".format(str(traceback.format_exc()), hb_domain, profile))
		# Move to the top and wait for dynamically updated ads to completely load
		driver.execute_script("window.scrollTo(0, 0);")
		print("Fullpage screenshot of the webpage captured")


		# Complete HAR Collection and save .har file
		try:
			with open(har_filepath, 'w') as fhar:
				json.dump(proxy.har, fhar, indent=4)
			fhar.close()
			logger.write("\nHAR dump saved for domain: {} | {}".format(hb_domain, profile))
		except BaseException as error:
			logger.write("\n[ERROR] main()::HarWriter: {}\nException occured while dumping the HAR for domain: {} | {}".format(str(traceback.format_exc()), hb_domain, profile))
			pass
		print("Network traffic saved")


		end_time = time.time()
		total_time = end_time - start_time
		print("Total time to crawl domain: {} is {}".format(hb_domain, total_time))
		logger.write("\nTotal time to crawl domain: {} is {}\n".format(hb_domain, total_time))


		server.stop()
		driver.quit()

		# End



if __name__ == "__main__":

	args = parseArguments()
	main(args)

