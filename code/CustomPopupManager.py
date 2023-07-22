from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from operator import attrgetter
from time import sleep
import re



class CustomPopupManager():

	def __init__(self, site, rule_dict) -> None:
		self.curr_domain = site
		self.rule_dict = rule_dict


	def acceptMissedConsents(self, webdriver_):
		try:
			missed = webdriver_.find_elements(By.XPATH, './/*[not(self::script) and self::button]')
			button_click = []
			for ele in missed:
				try:
					ele.str_html = ele.get_attribute('innerHTML').replace('\n', '').replace('\t', '')
					if (re.match(r'(?:.*)(?:acept|accept|accet|got|agree|ok|cookie_accept|accept_cookie|SUTINKU|keep|close|cerrar)(?:.*)', ele.str_html, re.IGNORECASE) or 
						re.match(r'(?:.*)(?:\ acept|\ accept|\ accet|\ got|\ agree|\ ok|\ cookie_accept|\ accept_cookie|\ SUTINKU)(?:.*)', ele.str_html, re.IGNORECASE)) and len(ele.text) < 16:
						ele.html_len = len(ele.get_attribute("innerHTML"))
						if ele.is_displayed():
							button_click.append(ele)
				except:
					continue
			if button_click:
				bc = min(button_click, key=attrgetter('html_len'))
				bc.click()
				pass
		except:
			pass
		consent_accept_options = ["Yes, I am an EU/EEA citizen", "Accept All Cookies", "Accept All", "Allow All", "Fine By Me", "Yes, I’m happy", "YES, I AGREE", "Yes, I agree", "Prosseguir", "I Accept", "Got it", "Agree and proceed", "AGREE", "Agree", "Accept", "ACCEPT", "Continue", "OK"]
		for opt in consent_accept_options:
			try:
				elements = webdriver_.find_elements(By.XPATH, '//button[contains(text(), "{}")]'.format(opt))
				for ele in elements:
					ele.click()
			except:
				continue
		return


	def managePopups(self, webdriver_):
		try:
			if "independent.co.uk" in self.curr_domain:
				match = webdriver_.find_element(By.XPATH, '//iframe[@allow="payment"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//button[@class="pn-template__close unbutton"]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "britannica.com" in self.curr_domain or "newsweek.com" in self.curr_domain:
				match = webdriver_.find_element(By.XPATH, '//iframe[@id="gdpr-consent-notice"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//span[contains(text(), "Accept All")]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "latimes.com" in self.curr_domain:
				shadow_access_js = '''return document.querySelector('modality-custom-element').shadowRoot.querySelector('a[class="met-flyout-close"]')'''
				webdriver_.execute_script(shadow_access_js).click()
				sleep(2)
			elif "nypost.com" in self.curr_domain:
				match = webdriver_.find_element(By.XPATH, '//iframe[@data-zephr-component="component"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//button[@external-event="flyout-close"]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "sfgate.com" in self.curr_domain or "chron.com" in self.curr_domain:
				try:
					webdriver_.find_element(By.XPATH, '//button[@data-group="editorial"]').click()
				except:
					pass
				try:
					webdriver_.find_element(By.XPATH, '//button[@data-group="business"]').click()
				except:
					pass
				try:
					webdriver_.find_element(By.XPATH, '//button[@id="continue"]').click()
					sleep(2)
				except:
					pass
				webdriver_.find_element(By.XPATH, '//a[@class="fancybox-item fancybox-close"]').click()
				sleep(2)
			elif "guardian.co" in self.curr_domain:
				match = webdriver_.find_element(By.XPATH, '//iframe[@title="SP Consent Message"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//div[@class="message-component message-row gu-content"]/button[@title="Close"]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
		except BaseException as e:
			webdriver_.switch_to.default_content()
			pass
		
		try:
			webdriver_.switch_to.default_content()
		except:
			pass

		if self.curr_domain in self.rule_dict.keys():
			for rule in self.rule_dict[self.curr_domain]:
				try:
					webdriver_.find_element(By.XPATH, '''{}'''.format(rule)).click()
					sleep(1)
				except:
					continue
			sleep(2)
		return
