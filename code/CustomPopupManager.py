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
			
			close_cross = webdriver_.find_element(By.XPATH, '//button/img[@alt="Close this offer"]')
			close_cross.click()

			if button_click:
				bc = min(button_click, key=attrgetter('html_len'))
				bc.click()
				pass
			if self.curr_domain == "lrytas.lt": 
				more_options = webdriver_.find_element(By.XPATH, '//button/span[contains(text(),"DAUGIAU P")]') # "DAUGIAU PASIRINKIMŲ"
				more_options.click()
				accept_everything = webdriver_.find_element(By.XPATH, '//button[contains(text(),"PRIIMU VISK")]') # "PRIIMU VISKĄ"
				accept_everything.click()
				save_exit = webdriver_.find_elements(By.XPATH, '//button[contains(text(),"ĮRAŠYTI IR IŠEITI")]') # "ĮRAŠYTI IR IŠEITI"
				save_exit[-1].click()
			elif self.curr_domain == "noticiasaominuto.com":
				close_cross = webdriver_.find_element(By.XPATH, '//span[@class="close"]')
				close_cross.click()
				privacy_policy = webdriver_.find_element(By.XPATH, '//button[contains(text(), "Não")]')
				privacy_policy.click()
				popup = webdriver_.find_element(By.XPATH, '//span[@class="pop-out-close"]')
				popup.click()
			elif self.curr_domain == "mobile01.com":
				close_cross = webdriver_.find_elements(By.XPATH, '//button[@title="Close"]')
				for ele in close_cross:
					ele.click()
				prompt = webdriver_.find_element(By.XPATH, '//button[@title="Close"]')
				prompt.click()
			elif self.curr_domain == "accuweather.com":
				understand = webdriver_.find_element(By.XPATH, '//div[contains(text(), "I Understand")]')
				understand.click()
			elif self.curr_domain in ["accuweather.com", "blic.rs"]:
				understand = webdriver_.find_element(By.XPATH, '//span[contains(text(), "U redu")]') # //div[contains(text(), "X")]
				understand.click()
			elif self.curr_domain == "rtl.fr":
				more_options = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Paramétrer mes choix")]')
				more_options.click()
				sleep(0.5)
				accept_everything = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Accepter tout")]')
				accept_everything.click()
				sleep(0.5)
				save = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Enregistrer")]')
				save.click()
			elif self.curr_domain == "extra.cz":
				more_options = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Podrobné nastavení")]')
				more_options.click()
				sleep(0.5)
				accept_everything = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Povolit vše")]')
				accept_everything.click()
				sleep(0.5)
				save = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Potvrdit moje volby")]')
				save.click()
			elif self.curr_domain == "lesechos.fr":
				save = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Agree and close")]')
				save.click()
			elif self.curr_domain == "thesimsresource.com":
				accept = webdriver_.find_element(By.XPATH, '//div[contains(text(), "I accept")]')
				accept.click()
			elif self.curr_domain == "prosport.ro":
				more_options = webdriver_.find_element(By.XPATH, '//font[contains(text(), "Manage options")]')
				more_options.click()
				accept_everything = webdriver_.find_elements(By.XPATH, '//font[contains(text(), "Accept all")]')
				accept_everything[-1].click()
			elif self.curr_domain == "cas.sk":
				more_options = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Spravovať možnosti")]')
				more_options.click()
				sleep(0.5)
				accept_everything = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Súhlasím so všetkým")]')
				accept_everything.click()
			elif self.curr_domain == "meteored.cl":
				more_options = webdriver_.find_element(By.XPATH, '//button[contains(text(), "Configuración")]')
				more_options.click()
				sleep(0.5)
				accept_everything = webdriver_.find_element(By.XPATH, '//button[contains(text(), "Aceptar todo y guardar")]')
				accept_everything.click()
			elif self.curr_domain == "belfasttelegraph.co.uk":
				accept_everything = webdriver_.find_element(By.XPATH, '//button/span[contains(text(), "Accept")]')
				accept_everything.click()
			elif self.curr_domain == "wyborcza.pl":
				accept_everything = webdriver_.find_element(By.XPATH, '//button[contains(text(), "AKCEPTUJĘ")]')
				accept_everything.click()
				close_cross = webdriver_.find_element(By.XPATH, '//a[@class="close"]')
				close_cross.click()
		except:
			pass
		consent_accept_options = ["Yes, I am an EU/EEA citizen", "Accept All Cookies", "Accept All", "Allow All", "Fine By Me", "Yes, I’m happy", "YES, I AGREE", "Yes, I agree", "Prosseguir", "I Accept", "Got it", "Agree and proceed", "AGREE", "Agree", "Accept", "ACCEPT", "Continue", "OK",
			"LAIN KALI", "Nu, multumesc", "ACCEPT TOATE", "AKCEPTUJĘ", "Tidak", "Confirm My Choices", "Accepter et continuer"]
		for opt in consent_accept_options:
			try:
				elements = webdriver_.find_elements(By.XPATH, '//button[contains(text(), "{}")]'.format(opt))
				for ele in elements:
					ele.click()
			except:
				continue
		return


	def managePopups(self, webdriver_):
		current_site = self.curr_domain
		try:
			if "independent.co.uk" in current_site:
				match = webdriver_.find_element(By.XPATH, '//iframe[@allow="payment"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//button[@class="pn-template__close unbutton"]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "britannica.com" in current_site or "newsweek.com" in current_site:
				match = webdriver_.find_element(By.XPATH, '//iframe[@id="gdpr-consent-notice"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//span[contains(text(), "Accept All")]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "latimes.com" in current_site:
				shadow_access_js = '''return document.querySelector('modality-custom-element').shadowRoot.querySelector('a[class="met-flyout-close"]')'''
				webdriver_.execute_script(shadow_access_js).click()
				sleep(2)
			elif "nypost.com" in current_site:
				match = webdriver_.find_element(By.XPATH, '//iframe[@data-zephr-component="component"]')
				if match:
					webdriver_.switch_to.frame(match)
					webdriver_.find_element(By.XPATH, '//button[@external-event="flyout-close"]').click()
					webdriver_.switch_to.default_content()
				sleep(2)
			elif "sfgate.com" in current_site or "chron.com" in current_site:
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
			elif "guardian.co" in current_site:
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

		if current_site in self.rule_dict.keys():
			for rule in self.rule_dict[current_site]:
				try:
					webdriver_.find_element(By.XPATH, '''{}'''.format(rule)).click()
					sleep(1)
				except:
					continue
			sleep(2)
		return
