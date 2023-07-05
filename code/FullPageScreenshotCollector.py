from selenium.webdriver.support.color import Color
from selenium.webdriver.common.by import By
from adblockparser import AdblockRules
from bs4 import BeautifulSoup
from tld import get_fld
from time import sleep
import traceback
import json
import time
import os


class FullPageScreenshotCollector():
	
	def __init__(self, profile, site, tranco_rank, ss_output_path) -> None:
		self.profile = profile
		self.site = site
		self.tranco_rank = tranco_rank
		self.ss_output_path = ss_output_path


	def exploreFullPage(self, driver):
		'''
		Scroll to bottom and back up to the top for all ads to load and become viewable
		'''
		page_height = int(webdriver.execute_script("return document.body.scrollHeight"))
		for i in range(1, page_height, 10):
			webdriver.execute_script("window.scrollTo(0, {});".format(i))
			sleep(0.025)
		sleep(2)
		webdriver.execute_script("window.scrollTo(0, 0);")
		# Wait for new ads to completely load
		sleep(15)
		return


	def captureFullScreenshot(self, driver):
		'''
		Capture a continuously stitched screenshot of the full webpage being currently visited
		'''

		self.exploreFullPage(driver)

		js = "window.document.styleSheets[0].insertRule(" + "'::-webkit-scrollbar {display: none;}', " + \
				"window.document.styleSheets[0].cssRules.length);"
		try:
			driver.execute_script(js)
			vp_total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
			vp_height = driver.execute_script("return window.innerHeight")
			vp_width = driver.execute_script("return window.innerWidth")
			scale = driver.execute_script("return window.devicePixelRatio")
		except (JavascriptException, WebDriverException) as e:
			error_str = "\nAn Exception Occurred: " + str(e) + " while capturing fullpage sreenshot."
			fe.write(error_str)
			S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
			driver.set_window_size(S('Width'),S('Height')) # May need manual adjustment                                                                                                                
			driver.find_element(By.TAG_NAME, 'body').screenshot(file)
			return False
		
		rectangles_vp = []

		vp = 0
		count, maximum_scrolls = 0, 0
		while vp < vp_total_height:
			count += 1
			if count == maximum_scrolls:
				break
			vp_top_height = vp + vp_height

			if vp_top_height > vp_total_height:
				vp = vp_total_height - vp_height
				vp_top_height = vp_total_height

			rectangles_vp.append((0, vp, 0, vp_top_height))
			vp = vp + vp_height

		stitched_image = Image.new('RGB', (int(vp_width * scale), int(vp_total_height * scale)))

		count = 0
		for i, rect_vp in enumerate(rectangles_vp):
			count += 1
			if count == maximum_scrolls:
				break
			try:
				driver.execute_script("window.scrollTo({0}, {1})".format(0, rect_vp[1]))
				sleep(10)

				tmpfile = "part_{0}.png".format(i)
				driver.get_screenshot_as_file(tmpfile)
				screenshot = Image.open(tmpfile)

				if (i + 1) * vp_height > vp_total_height:
					offset = (0, int((vp_total_height - vp_height) * scale))
				else:
					offset = (0, int(i * vp_height * scale - math.floor(i / 2.0)))

				stitched_image.paste(screenshot, offset)

				del screenshot
				os.remove(tmpfile)
			except:
				continue

		stitched_image.save(file)
		del stitched_image
		return True

