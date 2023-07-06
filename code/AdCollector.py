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


class AdCollector():
	
	def __init__(self, profile, site, tranco_rank, filter_rules, ads_output_path, logger) -> None:
		self.profile = profile
		self.site = site
		self.tranco_rank = tranco_rank
		self.filter_rules = filter_rules
		self.ads_output_path = ads_output_path
		self.ad_url_classifocation = {}
		self.logger = logger
		self.easylist_rules = self.setupEasyList()


	def storeAdResponse(self, url, output_path):
		if url.startswith('//'):
			url = 'http:' + url
			
		headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0'}
		try:
			curr_req = requests.get(url, headers=headers)
			curr_req.connection.close()

			curr_req_pickle = pickle.dumps(curr_req)
			self.write_byte_content(write_addr, curr_req_pickle)
		except Exception as ex:
			self.logger.write("\n[ERROR] storeAdResponse()::AdCollector: {}\nException occured in storing ad response for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
			# print('Exception while getting the ad response', ex) 
			pass

	
	def setupEasyList(self):
		# 'easylist': 'https://easylist.to/easylist/easylist.txt' (accessed on July 03, 2023)
		EASYLIST_DIR = "./data/EasyList"
		filepath = os.path.join(EASYLIST_DIR, "easylist.txt")
		try:
			with open(filepath) as f:
				rules = f.readlines()
				rules = [x.strip() for x in rules]
			f.close()
		except:
			self.logger.write("\n[ERROR] setupEasyList()::AdCollector: {}\nException occured while reading filter_rules for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
			rules = []
		
		rule_dict = {}
		rule_dict['script'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['script', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['script_third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'script', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['image'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['image', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['image_third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'image', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['css'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['stylesheet', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['css_third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'stylesheet', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['xmlhttp'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['xmlhttprequest', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['xmlhttp_third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'xmlhttprequest', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['domain'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['domain', 'subdocument'], skip_unsupported_rules=False)
		return rule_dict


	def matchURL(self, domain_top_level, current_domain, current_url, resource_type):
		rules_dict = self.easylist_rules
		try:
			if domain_top_level == current_domain:
				third_party_check = False
			else:
				third_party_check = True
			if resource_type == 'sub_frame':
				subdocument_check = True
			else:
				subdocument_check = False
			if resource_type == 'script':
				if third_party_check:
					rules = rules_dict['script_third']
					options = {'third-party': True, 'script': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
				else:
					rules = rules_dict['script']
					options = {'script': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			elif resource_type == 'image' or resource_type == 'imageset':
				if third_party_check:
					rules = rules_dict['image_third']
					options = {'third-party': True, 'image': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
				else:
					rules = rules_dict['image']
					options = {'image': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			elif resource_type == 'stylesheet':
				if third_party_check:
					rules = rules_dict['css_third']
					options = {'third-party': True, 'stylesheet': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
				else:
					rules = rules_dict['css']
					options = {'stylesheet': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			elif resource_type == 'xmlhttprequest':
				if third_party_check:
					rules = rules_dict['xmlhttp_third']
					options = {'third-party': True, 'xmlhttprequest': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
				else:
					rules = rules_dict['xmlhttp']
					options = {'xmlhttprequest': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			elif third_party_check:
				rules = rules_dict['third']
				options = {'third-party': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			else:
				rules = rules_dict['domain']
				options = {'domain': domain_top_level, 'subdocument': subdocument_check}
			return rules.should_block(current_url, options)
		except Exception as e:
			self.logger.write("\n[ERROR] matchURL()::AdCollector: {}\nException occured while matching URLs against filterlist: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
			return False


	def labelData(self, script_url):
		'''
		# top_domain = the website being visited
		# script_domain = domain of iframe url
		# script_url = url of iframe
		# resource_type = subframe, image, script
		'''
		if script_url in self.ad_url_classifocation.keys():
			return self.ad_url_classifocation[script_url]
		top_domain = self.site
		data_label = False
		for resource_type in ["sub_frame", "image", "script"]:
			try:
				fld = get_fld(script_url)
			except Exception as e:
				self.ad_url_classifocation[script_url] = False
				return False
			list_label = self.matchURL(top_domain, fld, script_url, resource_type)
			data_label = data_label | list_label
			if data_label == True:
				break
		self.ad_url_classifocation[script_url] = data_label
		print(script_url, data_label)
		return data_label


	def checkIfAdAttributes(self, src_attributes, href_attributes):
		flag = False
		for href_url in href_attributes:
			if self.labelData(href_url):
				flag = True
				return True
		for src_url in src_attributes:
			if self.labelData(src_url):
				flag = True
				return True
		return False


	def checkNestedAdIframes(self, matched_element, driver, index, observed_iframes, list_src=[], list_href=[], stop=0):
		
		iframe_elements = driver.find_elements(By.TAG_NAME, 'iframe')
		for idx, iframe in enumerate(iframe_elements):
			try:
				if not(iframe.is_enabled() and iframe.is_displayed()):
					continue
				if iframe in observed_iframes:
					continue
				observed_iframes.append(iframe)

				src_attributes, href_attributes = self.getMatchedElementAttributes(iframe, "IFRAME", driver)
				for attribute in src_attributes:
					list_src.append(attribute)
				for attribute in href_attributes:
					list_href.append(attribute)
				ad_flag = self.checkIfAdAttributes(src_attributes, href_attributes)
				if not(ad_flag):
					self.captureScreenshot(iframe, os.path.join(self.ads_output_path, str(idx) + "_" + str(stop) + '_nested_iframe.png'))
				
				if stop < 2:
					return self.checkNestedAdIframes(self, iframe, driver, index, observed_iframes, list_src, list_href, stop+1)
				driver.switch_to.parent_frame()
			except Exception as ex:
				driver.switch_to.parent_frame()
				pass
		
		driver.switch_to.default_content()
		src_attributes, href_attributes = "||".join(list_src), "||".join(list_href)
		return src_attributes, href_attributes

		
	def getMatchedElementAttributes(self, matched_element, element_type, driver):
		# Getting "src" and "href" attributes corresponding to the CSS matched element
		list_src, list_href = [], []
		src_attribute = matched_element.get_attribute("src")
		if src_attribute is not None:
			if self.labelData(src_attribute) and element_type == "IFRAME":
				list_src.append(src_attribute)
			elif element_type == "CSS":
				list_src.append(src_attribute)
		'''
		href_attribute = matched_element.get_attribute("href")
		if href_attribute is not None:
			list_href.append(href_attribute)
		'''

		if element_type == "IFRAME":
			driver.switch_to.frame(matched_element)
			soup = BeautifulSoup(driver.page_source, 'html.parser')
		else: # element_type == "CSS"
			soup = BeautifulSoup(matched_element.get_attribute("outerHTML"), 'html.parser')
		all_tags = soup.find_all()
		for tag in all_tags:
			if tag.has_attr('src'):
				if self.labelData(tag['src']) and element_type == "IFRAME":
					list_src.append(tag['src'])
				elif element_type == "CSS":
					list_src.append(tag['src'])
			elif tag.has_attr('href'):
				if self.labelData(tag['href']) and element_type == "IFRAME":
					list_href.append(tag['href'])
				elif element_type == "CSS":
					list_href.append(tag['href'])
		driver.switch_to.default_content()

		if element_type == "IFRAME":
			return list_src, list_href
		else: # element_type == "CSS"
			src_attributes = "||".join(list_src)
			href_attributes = "||".join(list_href)
			return src_attributes, href_attributes


	def captureScreenshot(self, matched_element, output_path):
		matched_element.location_once_scrolled_into_view
		matched_element.screenshot(output_path)


	def collectAds(self, webdriver):
		observed_elements = set()
		iframe_screenshot_logs_src, iframe_screenshot_logs_href = [], []
		css_elem_match_logs_src, css_elem_match_logs_href = [], []	
		
		matching_logic = '''
		{
			let matches = document.querySelectorAll(selector);
			matches.forEach((match) => {
				ads.add(match);
			});
		})
		'''
		js_script = f"let ads = new Set();" \
					f"let selectors = {self.filter_rules};" \
					f"selectors.forEach((selector) => {matching_logic}" \
					f"return Array.from(ads);"

		# ################# CSS MATCHING #################
		matching_css = webdriver.execute_script(js_script)
		for idx, match in enumerate(matching_css):
			try:
				if match in observed_elements:
					continue
				observed_elements.add(match)
				
				'''
				matched_element_location = match.location
				matched_element_x, matched_element_y = matched_element_location["x"], matched_element_location["y"]
				location_string = str(matched_element_x) + "-" + str(matched_element_y)
				rgb = match.value_of_css_property('background-color')
				matched_element_color = Color.from_string(rgb).hex
				print(idx, matched_element_color, match.size, matched_element_location, location_string)
				'''

				self.captureScreenshot(match, os.path.join(self.ads_output_path, str(idx) + '_css.png'))
				src_attributes, href_attributes = self.getMatchedElementAttributes(match, "CSS", webdriver)
				
				css_elem_match_logs_src.append(str(idx) + ',' + str(src_attributes))
				css_elem_match_logs_href.append(str(idx) + ',' + str(href_attributes))
				
				if href_attributes is not None and href_attributes.strip() != "":
					self.storeAdResponse(href_attributes.split('||')[0], os.path.join(self.ads_output_path, str(idx) + '_css_response.pickle'))
				sleep(0.5)

			except Exception as exc:
				self.logger.write("\n[ERROR] collectAds()::AdCollector: {}\nException occured in CSS ad collection for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
				# print('Exception while matching CSS', str(exc))
				pass
		self.logger.write("\nCSS ads collected for domain: {} | {}".format(self.site, self.profile))
		

		# ################# IFRAME MATCHING #################
		iframe_elements = webdriver.find_elements(By.TAG_NAME, 'iframe')
		for idx, iframe in enumerate(iframe_elements):
			try:
				if iframe in observed_elements:
					continue
				observed_elements.add(iframe)

				ad_ss_path = os.path.join(self.ads_output_path, str(idx) + '_iframe.png')
				self.captureScreenshot(iframe, ad_ss_path)
				
				print(iframe)
				src_attributes, href_attributes = self.getMatchedElementAttributes(iframe, "IFRAME", webdriver)
				print(idx, src_attributes, href_attributes)
				# print(iframe)
				# print("Y")
				# ad_flag = self.checkIfAdAttributes(src_attributes, href_attributes)
				# print("A")
				if len(src_attributes) == 0 and len(href_attributes) == 0:
					print("Removing file: iframe-{}".format(idx))
					os.remove(ad_ss_path)
				# 	print("B")
				

				## self.captureScreenshot(iframe, os.path.join(self.ads_output_path, str(idx) + '_iframe.png'))
				# print("C")
				# iframe_screenshot_logs_src.append(str(idx) + ',' + str("||".join(src_attributes)))
				# iframe_screenshot_logs_href.append(str(idx) + ',' + str("||".join(href_attributes)))
				# if href_attributes is not None and len(href_attributes) != 0:
				# 	print("D")
				# 	self.storeAdResponse(href_attributes[0], os.path.join(self.ads_output_path, str(idx) + '_iframe_response.pickle'))
				# print("E")
				# nested_src_attributes, nested_href_attributes = self.checkNestedAdIframes(iframe, webdriver, str(idx), observed_elements)
				# print("F")
				# iframe_screenshot_logs_src.append(str(idx) + ',' + str("||".join(nested_src_attributes)))
				# iframe_screenshot_logs_href.append(str(idx) + ',' + str("||".join(nested_href_attributes)))
				# if nested_href_attributes is not None and len(nested_href_attributes) != 0:
				# 	print("G")
				# 	self.storeAdResponse(nested_href_attributes[0], os.path.join(self.ads_output_path, str(idx) + '_nested_iframe_response.pickle'))

			except Exception as exc:
				# print("PRINTING:", str(exc))
				if ("Cannot take screenshot with 0 width" in str(exc)) or ("Cannot take screenshot with 0 height" in str(exc)):
					continue
				print("2", str(exc))
				print(traceback.format_exc())
				self.logger.write("\n[ERROR] collectAds()::AdCollector: {}\nException occured in IFRAME ad collection for domain: {} | {}".format(str(traceback.format_exc()), self.site, self.profile))
				# print('Excpetion while taking iframe screenshot', ex)
				pass

		print("Succesfully captured " + str(len(css_elem_match_logs_src)) + " CSS-based element screenshots out of " + str(len(matching_css)))
		print("Succesfully captured " + str(len(iframe_screenshot_logs_src)) + " iframe-based screenshots out of " + str(len(matching_css)))
		self.logger.write("\nSuccesfully captured {} CSS-based element screenshots out of {} for domain: {} | {}".format(str(len(css_elem_match_logs_src)), str(len(matching_css)), self.site, self.profile))
		self.logger.write("\nSuccesfully captured {} iframe-based screenshots out of {} for domain: {} | {}".format(str(len(iframe_screenshot_logs_src)), str(len(iframe_elements)), self.site, self.profile))
		# exit()
		# self.write_content(os.path.join(self.ads_output_path,'iframe_screenshot_logs_src.csv'), iframe_screenshot_logs_src)
		# self.write_content(os.path.join(self.ads_output_path,'iframe_screenshot_logs_href.csv'), iframe_screenshot_logs_href)
		# self.write_content(os.path.join(self.ads_output_path,'cssmatch_screenshot_logs_src.csv'), css_elem_match_logs_src)
		# self.write_content(os.path.join(self.ads_output_path,'cssmatch_screenshot_logs_href.csv'), css_elem_match_logs_href)
		return
