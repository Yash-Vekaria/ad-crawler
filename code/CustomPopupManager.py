from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from time import sleep
import re



class CustomPopupManager():

	def __init__(self, site) -> None:
		self.curr_domain = site


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
				return
		except:
			return


	def managePopups(self, webdriver_):
		try:
			if "forbes.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@alt="Scroll Down"]').click()
				sleep(2)
			elif "accuweather.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//div[@class="banner-button policy-accept"]').click()
				sleep(2)
			elif "investing.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//i[@class="popupCloseIcon largeBannerCloser"]').click()
				sleep(2)
			elif "newsweek.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//*[contains(text(), "Accept All")]').click()
				sleep(2)
			elif "chicagotribune.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//a[@class="met-flyout-close met-visually-hidden"]').click()
				sleep(2)
			elif "nbcnews.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@id="cx_button_close"]').click()
				sleep(2)
			elif "marketwatch.com" in self.curr_domain:
				try:
					webdriver_.find_element(By.XPATH, '//button[@class="close-btn"]').click()
				except:
					pass
				webdriver_.find_element(By.XPATH, '//label[@class="icon--close"]').click()
				sleep(2)
			elif "metro.co.uk" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//div[@id="closeButtn"]').click()
				sleep(2)
			elif "merriam-webster.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//*[contains(text(), "Accept All")]').click()
				sleep(2)
			elif "people.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//div[@class="jumpstart-js-wrapper "]/div/div[@aria-label="Close sticky player"]').click()
				sleep(2)
			elif "globo.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@class="cookie-banner-lgpd_accept-button"]').click()
				sleep(2)
			elif "guardian.co" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@data-link-name="choice-cards-buttons-banner-blue : close"]').click()
				sleep(2)
			elif "usatoday.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@aria-label="Close Special Offer"]').click()
				sleep(2)
			elif "chron.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//a[@class="bc-close-button"]').click()
				sleep(2)
			elif "dailymail.co.uk" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//div[@id="closeButton"]').click()
				sleep(2)
			elif "goo.ne.jp" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@class="webpush-title-close"]').click()
				sleep(2)
			elif "latimes.com" in self.curr_domain:
				shadow_access_js = '''return document.querySelector('modality-custom-element').shadowRoot.querySelector('a[class="met-flyout-close"]')'''
				webdriver_.execute_script(shadow_access_js).click()
				sleep(2)
			elif "marketwatch.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@class="close-btn"]').click()
				sleep(2)
			elif "nydailynews.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@id="onesignal-slidedown-cancel-button"]').click()
				sleep(2)
			elif "sfgate.com" in self.curr_domain:
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
			elif "slickdeals.net" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//a[@class="sd-emailOnlyRegistrationWithLogin_laterLink"]').click()
				sleep(2)
			elif "wunderground.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button/i[@class="material-icons"]').click()
				sleep(2)
			elif "tripadvisor.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@id="close-pc-btn-handler"]').click()
				sleep(2)
			elif "britannica.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//a[@class="fancybox-item fancybox-close"]').click()
				sleep(2)
			elif "independent.co.uk" in self.curr_domain:
				match = webdriver_.find_element(By.XPATH, '//iframe[@allow="payment"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//button[@class="pn-template__close unbutton"]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "nypost.com" in self.curr_domain:
				match = webdriver_.find_element(By.XPATH, '//iframe[@data-zephr-component="component"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//button[@external-event="flyout-close"]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "huffpost.com" in self.curr_domain or "huffingtonpost.com" in self.curr_domain:
				try:
					webdriver_.find_element(By.XPATH, '//*[contains(text(), "I Accept")]').click()
				except:
					pass
				webdriver_.find_element(By.XPATH, '//button[@aria-label="Close Menu"]').click()
				sleep(2)
			elif "weather.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//section[@id="privacy-data-notice"]//*[name()="svg"][@name="close"]').click()
				sleep(2)
		except BaseException as e:
			webdriver_.switch_to.default_content()
			pass

		try:
			if "sfgate.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//div[@class="exp-ui__sticky__close-btn"]').click()
				sleep(2)
			elif "slickdeals.net" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@data-role="close"]').click()
				sleep(2)
			elif "latimes.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[@data-element="search-button"]').click()
				sleep(2)
			elif "guardian.co" in self.curr_domain:
				match = webdriver_.find_element(By.XPATH, '//iframe[@title="SP Consent Message"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//div[@class="message-component message-row gu-content"]/button[@title="Close"]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "weather.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//button[data-testid="ctaButton"]').click()
				sleep(2)
			elif "huffpost.com" in self.curr_domain or "huffingtonpost.com" in self.curr_domain:
				webdriver_.find_element(By.XPATH, '//cnx[@class="cnx-icon-button cnx-button-closebutton cnx-ui-btn-hoverable cnx-mod-hover-s"]').click()
				sleep(2)
		except BaseException as e:
			webdriver_.switch_to.default_content()
			pass
		return