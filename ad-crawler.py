from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium import webdriver
import threading
import selenium

# import undetected_chromedriver as uc
from browsermobproxy import Server
from time import sleep
import pandas as pd
import traceback
import argparse
import datetime
import zipfile
import psutil
import codecs
import time
import sys
import os

sys.path.insert(0, './code/')
from FullPageScreenshotCollector import *
from CustomPopupManager import *
from BidCollector import *
from AdCollector import *

DOCKER = True
if DOCKER:
	from pyvirtualdisplay import Display
	disp = Display(backend="xvnc", size=(1920,1080), rfbport=1212) # 1212 has to be a random port number
	disp.start()

ROOT_DIRECTORY = os.getcwd()



def parseArguments():
	global ROOT_DIRECTORY;
	# Example: python3 ad-crawler.py --profile="Test" --proxyport=8022 --chromedatadir="/home/yvekaria/.config/google-chrome/ProfileTest"
	parser = argparse.ArgumentParser()
	parser.add_argument("-p", "--profile", type=str, required=True, help="Enter the type of profile being crawled. Valid inputs are ['TV-Blank', 'TV-Trained', 'HB-Checker']")
	parser.add_argument("-px", "--proxyport", type=int, required=True, help="Enter the port on which browsermob-proxy is to be run.")
	parser.add_argument("-c", "--chromedatadir", type=str, required=True, help="Enter the Chrome's data directory path: Open Chrome's latest stable version installed => Type chrome://version => Input 'Profile Path' without")
	if DOCKER:
		# Example docker run -d -e PYTHONUNBUFFERED=1 -v $(pwd):/root -v /home/yvekaria/.config/google-chrome/Test:/profile -p 20000:1212 --shm-size=10g ad-crawler python3.11 ad-crawler.py -p "Test" -px 8022 -c "/home/yvekaria/.config/google-chrome/Test" -mp "/root"
		parser.add_argument("-mp", "--mountpath", type=str, required=False, help="Mounted path from docker run command")
	args = parser.parse_args()
	return args



# Function to open the URL and set a flag when done
def open_url(url, driver, done_flag):
	print(time.time(), "Started")
	try:
		driver.get(url)
	except Exception as e:
		print(f"Error loading {url}: {e}")
	finally:
		done_flag.set()



def handle_popups(cpm_obj, driver, pop_flag):
	try:
		cpm_obj.managePopups(driver)
	except Exception as e:
		print(f"Error handling popups: {e}")
	finally:
		pop_flag.set()



def handle_consent(cpm_obj, driver, consent_flag):
	try:
		cpm_obj.acceptMissedConsents(driver)
	except Exception as e:
		print(f"Error handling popups: {e}")
	finally:
		consent_flag.set()
	


def readHeaderBiddingSites():
	global ROOT_DIRECTORY;
	filepath = os.path.join(ROOT_DIRECTORY, "data", "hb_domains.csv")
	df_hb = pd.read_csv(filepath)
	return {str(df_hb.iloc[i]["tranco_domain"]): int(df_hb.iloc[i]["tranco_rank"]) for i in range(len(df_hb)) if bool(df_hb.iloc[i]["hb_status"])}


def getChromeOptionsObject():
	global ROOT_DIRECTORY;
	chrome_options = Options()
	chrome_options.binary_location = "/usr/bin/google-chrome-stable" 
	# chrome_options.add_argument("--headless")
	# chrome_options.add_argument("--disable-gpu")
	# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
	# chrome_options.add_experimental_option('useAutomationExtension', False)
	chrome_options.add_argument("--no-sandbox")
	chrome_options.add_argument("--disable-dev-shm-usage")
	chrome_options.add_argument("--remote-debugging-port=9222")
	chrome_options.add_argument("--window-size=1536,864")
	chrome_options.add_argument("--start-maximized")
	chrome_options.add_argument("--disable-infobars")
	chrome_options.add_argument("--disable-notifications")
	chrome_options.add_argument("--disable-popup-blocking")
	chrome_options.add_argument("--ignore-certificate-errors")
	extension_dir = os.path.join(ROOT_DIRECTORY, "consent-extension", "Consent-O-Matic", "Extension")
	chrome_options.add_argument('--load-extension={}'.format(extension_dir))
	return chrome_options


def exploreFullPage(webdriver_):
	'''
	Scroll to bottom and back up to the top for all ads to load and become viewable
	'''
	try:
		page_height = int(webdriver_.execute_script("return document.body.scrollHeight"))
		for i in range(1, page_height, 10):
			try:
				webdriver_.execute_script("window.scrollTo(0, {});".format(i))
				sleep(0.05)
			except:
				continue
		sleep(2)
		webdriver_.execute_script("window.scrollTo(0, 0);")
	except:
		pass
	# Wait for new ads to completely load
	sleep(6)
	return


def configureProxy(port, profile_name, profile_dir):
	'''
	Instatiate and start browsermobproxy to collect HAR files and accordingly configure chrome options
	Killing open ports:
		- lsof -i:<port>
		- kill -9 <PID>
	'''
	global ROOT_DIRECTORY;
	
	try:
		print("Total browsermobproxy instances currently running:", os.system("ps -aux | grep browsermob | wc -l"))
		os.system("ps -eo etimes,pid,args --sort=-start_time | grep browsermob | awk '{print $2}' | sudo xargs kill")
		print("Total browsermobproxy instances currently running:", os.system("ps -aux | grep browsermob | wc -l"))
		print("Killed all the zombie instances of browsermobproxy from previous visit!")
		for proc in psutil.process_iter():
			if proc.name() == "browsermob-proxy":
				proc.kill()
	except:
		pass
	try:
		from signal import SIGTERM # or SIGKILL
		for proc in process_iter():
			for conns in proc.connections(kind='inet'):
				if conns.laddr.port == 8022:
					proc.send_signal(SIGTERM)
	except:
		pass
	
	try:
		proxy.close()
	except:
		pass
	try:
		server.close()
	except:
		pass
	try:
		server = Server(os.path.join(ROOT_DIRECTORY, "data", "browsermob-proxy-2.1.4", "bin", "browsermob-proxy"), options={'port': port})
		server.start()
		sleep(10)
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
	# chrome_options.add_argument("--profile-directory=%s" % profile_name)
	
	return server, proxy, chrome_options


def killBrowermobproxyInstances():
	for process in psutil.process_iter():
		try:
			process_info = process.as_dict(attrs=['name', 'cmdline'])
			if process_info.get('name') in ('java', 'java.exe'):
				for cmd_info in process_info.get('cmdline'):
					if cmd_info == '-Dapp.name=browsermob-proxy':
						process.kill()
		except psutil.NoSuchProcess:
			pass
	return


def main(args):

	global ROOT_DIRECTORY, DOCKER;

	profile = args.profile
	proxy_port = args.proxyport
	chrome_profile_dir = args.chromedatadir.replace("Default", profile)
	if DOCKER:
		ROOT_DIRECTORY = args.mountpath
	

	# Reading Top 104 Header Bidding supported websites
	# hb_dict stores mapping of hb_domain to hb_rank (tranco_rank)
	hb_dict = readHeaderBiddingSites()

	for iteration in [1, 2, 3]:
		for idx, (hb_domain, hb_rank) in enumerate(hb_dict.items()):
	
			start_time = time.time()
			print("\n\nStarting to crawl:", iteration, idx, hb_domain, hb_rank)
	
			experimental_path = os.path.join(ROOT_DIRECTORY, "output", profile, str(hb_domain)+"_"+str(iteration))
			if not(os.path.exists(experimental_path)):
				os.makedirs(experimental_path)
	
	
			# Log issues and crawl progress in this file
			logger = open(os.path.join(experimental_path, str(hb_domain)+"_"+str(iteration)+"_logs.txt"), "w")
			ct = datetime.datetime.now()
			logger.write("\n\nCrawl {} Start Time: {} [TS:{}] [{}]".format(iteration, ct, ct.timestamp(), hb_domain))
			print("Error logging started ...")
	
	
			# Start the proxy server to facilitate capturing HAR file
			current_time = time.time()
			server, proxy, chrome_options = configureProxy(proxy_port, profile, chrome_profile_dir)
			if server is None:
				try:
					proxy.close()
				except:
					pass
				try:
					server.close()
				except:
					pass
				logger.write("Server issue while its initialization.")
				continue
			logger.write("\nBrowsermob-proxy successfully configured for domain: {} | {}! [Time: {}]".format(hb_domain, profile, time.time()-current_time))
			print("\nBrowsermob-proxy successfully configured for domain: {} | {}!!".format(hb_domain, profile))
			
	
			# Start the chromedriver instance
			current_time = time.time()
			try:
				# driver = uc.Chrome(service=Service(ChromeDriverManager().install()), version_main=114, options=chrome_options) #executable_path=‘chromedriver’
				driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
			except BaseException as error:
				continue
				proxy.close()
				server.stop()
				killBrowermobproxyInstances()
				logger.write("\n[ERROR] main()::Webdriver-Intitialization: {} for domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
				continue
			logger.write("\nChromedriver successfully loaded! [Time: {}]".format(time.time()-current_time))
			print("\nChromedriver successfully loaded!")
	
	
			# Start capturing HAR
			current_time = time.time()
			har_filepath = os.path.join(experimental_path, str(hb_domain)+"_"+str(iteration)+"_har.json")
			try:
				proxy.new_har(har_filepath, options={'captureHeaders': True,'captureContent':True})
			except BaseException as error:
				logger.write("\n[ERROR] main()::HarCaptureStart: {}\n for domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
				pass
			logger.write("\nHAR capture started! [Time: {}]".format(time.time()-current_time))
			print("Starting HAR Capture")
	
	
			# Visit the current domain
			current_time = time.time()
			website = "http://" + str(hb_domain)
			try:
				print("Website:", website)
				# driver.get(website)
				
				# Threading to open the URL and wait for a maximum of timeout seconds
				done_flag = threading.Event()
				thread = threading.Thread(target=open_url, args=(website, driver, done_flag))
				thread.start()

				# Timeout for each URL (in seconds) before moving to next URL
				timeout = 120
				
				# Wait for the thread to finish or until the timeout is reached
				thread.join(timeout)
				
				# If the thread is still running (URL not loaded within timeout), stop it and proceed
				if not done_flag.is_set():
					print(time.time(), "Timed out while trying to load")
					logger.write("\n[TIMEOUT] main()::ad-crawler: {}\nTimeout of 120secs occurred while getting the domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
					raise BaseException("Raising BaseException while getting URL due to timeout issue")
				else:
					print(f"Successfully loaded: {website}")
					logger.write("\nSuccessfully got the webpage ... [Time: {}]".format(time.time()-current_time))
					pass
			except BaseException as e:
				logger.write("\n[ERROR] main()::ad-crawler: {}\nException occurred while getting the domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
				try:
					driver.quit()
					proxy.close()
					server.stop()
					killBrowermobproxyInstances()
				except:
					print("\n[ERROR] main()::Webdriver-Intitialization: {}".format(str(traceback.format_exc())))
					logger.write("\n[ERROR] main()::Webdriver-Intitialization: {} for domain: {} in Iteration: {}| {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
					continue
				continue
			print("\nChromedriver successfully loaded website!")
			# Wait for page to completely load
			sleep(10)
			print("Visiting and loading webpage ...")
			logger.write("\nVisiting and loading webpage ... [Time: {}]".format(time.time()-current_time))
	
	
			# Read custom popup handling rules
			current_time = time.time()
			f = open(os.path.join(ROOT_DIRECTORY, "data", "custom-popup-xpaths.txt"), "r")
			prules = f.read().split("\n")
			f.close()
			prule_dict = {prule.split(" | ")[0]: list(prule.split(" | ")[1:]) for prule in prules}
	
	
			cpm = CustomPopupManager(hb_domain, prule_dict)
			pop_flag = threading.Event()
			thread = threading.Thread(target=handle_popups, args=(cpm, driver, pop_flag))
			thread.start()
			timeout = 150
			thread.join(timeout)
			# If the thread is still running, stop it and proceed
			if not pop_flag.is_set():
				print(time.time(), "Timed out while trying to give consent!")
				logger.write("\n[TIMEOUT] main()::ad-crawler: {}\nTimeout of 200secs occurred while handling consent in managePopups() for the domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
			else:
				print("Successfully completed managePopups()")
				logger.write("\nSuccessfully completed managePopups() ... [Time: {}]".format(time.time()-current_time))
				pass
			# cpm.managePopups(driver)
	
	
			consent_flag = threading.Event()
			thread = threading.Thread(target=handle_consent, args=(cpm, driver, consent_flag))
			thread.start()
			timeout = 150
			thread.join(timeout)
			# If the thread is still running, stop it and proceed
			if not consent_flag.is_set():
				print(time.time(), "Timed out while trying to give consent!")
				logger.write("\n[TIMEOUT] main()::ad-crawler: {}\nTimeout of 200secs occurred while handling consent in acceptMissedConsents() for the domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
			else:
				print("Successfully completed acceptMissedConsents()")
				logger.write("\nSuccessfully completed acceptMissedConsents() ... [Time: {}]".format(time.time()-current_time))
				pass
			# cpm.acceptMissedConsents(driver)
			
			logger.write("\nPopup-Consent-1 handled!")
			exploreFullPage(driver)
			logger.write("\nWebpage explored fully.")
			
			consent_flag = threading.Event()
			thread = threading.Thread(target=handle_consent, args=(cpm, driver, consent_flag))
			thread.start()
			timeout = 150
			thread.join(timeout)
			# If the thread is still running, stop it and proceed
			if not consent_flag.is_set():
				print(time.time(), "Timed out while trying to give consent!")
				logger.write("\n[TIMEOUT] main()::ad-crawler: {}\nTimeout of 200secs occurred while handling consent in acceptMissedConsents() for the domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
			else:
				print("Successfully completed acceptMissedConsents()")
				logger.write("\nSuccessfully completed acceptMissedConsents() ... [Time: {}]".format(time.time()-current_time))
				pass
			# cpm.acceptMissedConsents(driver)
	
	
			pop_flag = threading.Event()
			thread = threading.Thread(target=handle_popups, args=(cpm, driver, pop_flag))
			thread.start()
			timeout = 120
			thread.join(timeout)
			# If the thread is still running, stop it and proceed
			if not pop_flag.is_set():
				print(time.time(), "Timed out while trying to give consent!")
				logger.write("\n[TIMEOUT] main()::ad-crawler: {}\nTimeout of 200secs occurred while handling consent in managePopups() for the domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
			else:
				print("Successfully completed managePopups()")
				logger.write("\nSuccessfully completed managePopups() ... [Time: {}]".format(time.time()-current_time))
				pass
			# cpm.managePopups(driver)
			logger.write("\nPopup-Consent-2 handled! [Time: {}]".format(time.time()-current_time))
	
			
			# Read filterlist rules
			'''
			f = open(os.path.join(ROOT_DIRECTORY, "data", "EasyList", "easylist.txt"), "r")
			rules = f.read().split("\n")
			f.close()
			rules = [rule[2:] for rule in rules[18:] if rule.startswith("##")]
   			'''
	
	
			# Save DOM of the webpage
			current_time = time.time()
			try:
				dom_filepath = os.path.join(experimental_path, str(hb_domain)+"_"+str(iteration)+"_DOM.html")
				fdom = codecs.open(dom_filepath, "w", "utf−8")
				fdom.write(driver.page_source)
				fdom.close()
				logger.write("\nDOM saved. [Time: {}]".format(time.time()-current_time))
				print("DOM saved")
			except BaseException as e:
				print("\n[ERROR] DOM-Capture: {}".format(str(traceback.format_exc())))
				logger.write("\n[ERROR] main()::DOM-Capture: {} for domain: {} in iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
				pass
	
	
			# Perform bid collection
			bid_file_path = os.path.join(experimental_path, str(hb_domain)+"_"+str(iteration)+"_bids.json")
			bid_object = BidCollector(profile, hb_domain, hb_rank, bid_file_path)
			bid_object.collectBids(driver, logger)
			print("Bid data collected")
			
			
			# Take fullpage screenshot of the webpage
			current_time = time.time()
			screenshot_output_path = os.path.join(experimental_path, str(hb_domain)+"_"+str(iteration)+"_ss-before.png")
			ss_object = FullPageScreenshotCollector(profile, hb_domain, hb_rank, screenshot_output_path)
			ss_object.captureFullScreenshot(driver, logger)
			logger.write("\nFull page screnshot successfully captured. [Time: {}]".format(time.time()-current_time))
			try:
				driver.execute_script("window.scrollTo(0, 0);")
			except:
				pass
			sleep(10)
			print("Fullpage screenshot of the webpage captured")
	
			
			# Collect ads on the website
			'''
			print("Starting to collect ads ...")
			ad_path = os.path.join(experimental_path, "ads")
			if not(os.path.exists(ad_path)):
				os.makedirs(ad_path)
	
			EASYLIST_DIR = os.path.join(ROOT_DIRECTORY, "data", "EasyList")
			ad_object = AdCollector(profile, iteration, hb_domain, hb_rank, rules, ad_path, EASYLIST_DIR, logger)
			ad_object.collectAds(driver)
			print("Ad collection complete!")
	
	
			# Take fullpage screenshot of the webpage
			current_time = time.time()
			screenshot_output_path = os.path.join(experimental_path, str(hb_domain)+"_"+str(iteration)+"_ss-after.png")
			ss_object = FullPageScreenshotCollector(profile, hb_domain, hb_rank, screenshot_output_path)
			ss_object.captureFullScreenshot(driver, logger)
			logger.write("\nFull page screnshot successfully captured. [Time: {}]".format(time.time()-current_time))
			# Move to the top and wait for dynamically updated ads to completely load
			try:
				driver.execute_script("window.scrollTo(0, 0);")
			except:
				pass
			print("Fullpage screenshot of the webpage captured")
   			'''
	
	
			# Complete HAR Collection and save .har file
			current_time = time.time()
			try:
				with open(har_filepath, 'w') as fhar:
					json.dump(proxy.har, fhar, indent=4)
				fhar.close()
				logger.write("\nHAR dump saved for domain: {} in Iteration: {} | {} [Time: {}]".format(hb_domain, iteration, profile, time.time()-current_time))
			except BaseException as error:
				logger.write("\n[ERROR] main()::HarWriter: {}\nException occured while dumping the HAR for domain: {} in Iteration: {} | {} [Time: {}]".format(str(traceback.format_exc()), hb_domain, iteration, profile, time.time()-current_time))
				pass
			print("Network traffic saved")
	
	
			end_time = time.time()
			total_time = end_time - start_time
			print("Total time to crawl domain: {} in Iteration: {} is {}".format(hb_domain, iteration, total_time))
			logger.write("\nTotal time to crawl domain: {} in Iteration: {} is {}\n".format(hb_domain, iteration, total_time))
	
	
			proxy.close()
			server.stop()
			driver.quit()
			killBrowermobproxyInstances()
	
			# End



if __name__ == "__main__":

	args = parseArguments()
	main(args)

