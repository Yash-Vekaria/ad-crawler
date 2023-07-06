from selenium.webdriver.common.by import By
from time import sleep
import traceback
import os


from PIL import Image


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
		page_height = int(driver.execute_script("return document.body.scrollHeight"))
		for i in range(1, page_height, 10):
			driver.execute_script("window.scrollTo(0, {});".format(i))
			sleep(0.025)
		sleep(2)
		driver.execute_script("window.scrollTo(0, 0);")
		# Wait for new ads to completely load
		sleep(15)
		return


	def captureFullScreenshot(self, driver, logger):
		'''
		Capture a continuously stitched screenshot of the full webpage being currently visited
		'''

		self.exploreFullPage(driver)

		try:
			total_width = driver.execute_script("return document.body.offsetWidth")
			total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
			viewport_width = driver.execute_script("return document.body.clientWidth")
			viewport_height = driver.execute_script("return window.innerHeight")
			
			rectangles = []
			i = 0
			while i < total_height:
				j = 0
				top_height = i + viewport_height
			
				if top_height > total_height:
					top_height = total_height
			
				while j < total_width:
					top_width = j + viewport_width
			
					if top_width > total_width:
						top_width = total_width
			
					rectangles.append((j, i, top_width,top_height))
			
					j += viewport_width
			
				i += viewport_height
			
			stitched_image = Image.new('RGB', (total_width, total_height))
			previous = None
			part = 0
			
			for rectangle in rectangles:
				if previous is not None:
					driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
					sleep(0.2)
			
				file_name = "part_{0}.png".format(part)
			
				driver.get_screenshot_as_file(file_name)
				screenshot = Image.open(file_name)
			
				if rectangle[1] + viewport_height > total_height:
					offset = (rectangle[0], total_height - viewport_height)
				else:
					offset = (rectangle[0], rectangle[1])
				stitched_image.paste(screenshot, offset)
				del screenshot
				os.remove(file_name)
				part += 1
				previous = rectangle
			
			stitched_image.save(self.ss_output_path)
		except BaseException as e:
			logger.write("\n[ERROR] captureFullScreenshot()::FullPageScreenshotCollector: {}\nException occured while capturing fullpage screenshot for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
		return
