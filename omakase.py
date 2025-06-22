from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import traceback
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys
import json
import time
import smtplib
from email.mime.text import MIMEText
from selenium.common.exceptions import WebDriverException
from datetime import datetime

DEFAULT_BROWSER_CONFIG = {"proxy": None, "headless": False}

class webDriver(object):
    config_file = "browser_config.json"

    def __init__(self):
        self.driver = None
        self.config = self.__load_browser_config()
        self.shop_url = self.config.get("shop_url", None)


    def __load_browser_config(self):
        if self.config_file is None:
            return DEFAULT_BROWSER_CONFIG
        with open(self.config_file) as f:
            return json.load(f)


    def set_implicity_wait(self, time):
        self.driver.implicitly_wait(time)

    def not_initialized(self):
        return self.driver is None

    def new_driver(self):
        self.driver = self.get_driver(renew=True)
        self.set_implicity_wait(0)

    def close_driver(self):
        pass
        self.driver.quit()

    def refresh(self):
        self.driver.refresh();

    def get_current_url(self):
        return self.driver.current_url

    def scroll_down(self, step=1):
        self.driver.find_element(By.TAG_NAME, 'body').send_keys([Keys.DOWN] * step)

    def page_down(self, xpath, step=1):
        self.find_element_with_timeout(By.XPATH, xpath).send_keys([Keys.PAGE_DOWN] * step)

    @staticmethod
    def get_url(element):
        try:
            return element.find_element(By.TAG_NAME, "a").get_attribute('href')
        except:
            return None

    @staticmethod
    def try_get_element(element, by, value):
        try:
            return element.find_element(by, value)
        except:
            return None

    def try_get_element_text(self, by, value):
        try:
            return self.driver.find_element(by, value).text
        except:
            return None

    def get_driver(self, renew=False):
        return self.__get_driver(renew)

    def find_elements_with_timeout(self, by, value, timeout=20, stop_on_error=True):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
        except:
            if stop_on_error:
                traceback.print_exc()
                print(f"Cannot find element by {by} {value}")
            return []

    def find_element_with_timeout(self, by, value, timeout=10, stop_on_error=True):
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, value)))
        except Exception as e:
            if stop_on_error:
                traceback.print_exc()
            return None

    def find_btn_with_timeout(self, by, value, timeout=2):
        return WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((by, value)))

    def find_btn_and_click(self, by, value, timeout=2):
        try:
            showmore_link = self.find_btn_with_timeout(by, value, timeout)
            showmore_link.click()
        except ElementClickInterceptedException:
            print("Trying to click on the button again")
            self.driver.execute_script("arguments[0].click()", showmore_link)

    def __get_driver(self, renew=False):
        print("init web driver")
        # Init chromedriver
        chrome_options = Options()
        chrome_options.add_argument(f'user-agent={self.generate_ua()}')
        headless = self.config.get("headless")
        if headless:
            chrome_options.add_argument("--headless")  # turn off GUI
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--lang=ja");
        chrome_options.add_argument("--charset=utf-8")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--disable-browser-side-navigation')
        chrome_options.add_argument("--crash-dumps-dir=/tmp")
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 2,
            'intl.accept_languages': 'ja'
        })
        proxy_cfg = self.config.get("proxy")
        if proxy_cfg is not None:
            proxy_ip = proxy_cfg.get("proxy_ip")
            proxy_port = proxy_cfg.get("port")
            if proxy_ip is not None and proxy_port is not None:
                chrome_options.add_argument(f"--proxy-server=http://{proxy_ip}:{proxy_port}")
        chrome_options.page_load_strategy = 'eager'  # to prevent page from infinitely loading https://www.selenium.dev/documentation/webdriver/drivers/options/#pageloadstrategy
        driver = Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)
        return driver

    def find_element_by_xpaths(self, xpaths):
        for xpath in xpaths:
            try:
                return self.find_elements_with_timeout(By.XPATH, xpath, timeout=1)
            except:
                continue
        return None

    @staticmethod
    def generate_ua():
        from fake_useragent import UserAgent
        return UserAgent(platforms='desktop').random

    def get_current_url(self):
        return self.driver.current_url

    def reset_driver(self):
        self.driver.quit()
        self.driver = self.get_driver(renew=True)

    def click(self, url):
        try:
            self.driver.get(url)
        except Exception as e:
            traceback.print_exc()
            self.reset_driver()
            self.driver.get(url)

    def send_mail(self, title, text):
        sender_email = self.config["sender_email"]
        to_mail = self.config["to_email"]
        msg = MIMEText(text)
        msg["Subject"] = title
        msg["From"] = sender_email
        msg["To"] = to_mail
        key = self.config.get("key")
        smtp_server = "smtp.gmail.com"  # e.g., smtp.gmail.com
        port = 587  # or 465 for SSL/TLS
        try:
            with smtplib.SMTP(smtp_server, port) as server:
                server.starttls()  # Use STARTTLS for encryption (if using port 587)
                server.login(sender_email, key)  # Replace with your email and password
                server.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def login(self):
        user_name = self.config.get("user_name",None)
        password = self.config.get("password", None)
        login_url = "https://omakase.in/users/sign_in"
        self.driver.get(login_url)
        time.sleep(1)
        xpaths = '//*[@id="user_email"]'
        user_name_box = self.find_element_with_timeout(By.XPATH, xpaths, timeout=1, stop_on_error=True)
        user_name_box.send_keys(user_name)
        password_box = self.find_element_with_timeout(By.XPATH, '//*[@id="user_password"]', timeout=1, stop_on_error=True)
        password_box.send_keys(password)
        xpath = '//*[@id="new_user"]/input[2]'
        self.find_element_with_timeout(By.XPATH, xpath, timeout=1, stop_on_error=True).submit()
        time.sleep(2)

    def get_hotel_name(self):
        url = self.shop_url
        self.driver.get(url)
        class_name = 'p-r_title'
        element = self.find_element_with_timeout(By.CLASS_NAME, class_name, timeout=3, stop_on_error=True)
        if element:
            return element.text
        return None

    def check_if_available(self, hotel_name):
        url = self.shop_url
        time_stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Checking availability for {hotel_name} at {time_stamp}")
        self.driver.get(url)
        class_name = 'p-r_reserve_action_reserve'
        element = self.find_element_with_timeout(By.CLASS_NAME, class_name, timeout=3, stop_on_error=True)
        text = element.text if element else None
        if text is not None and text == "このお店を予約する":
            element.click()
            return True
        return False


if __name__ == '__main__':
    wd = webDriver()
    wd.new_driver()
    wd.login()
    hotel_name = wd.get_hotel_name()
    print(f"Hotel name: {hotel_name}")
    start_title = f"Start checking availability for {hotel_name} at \n {wd.shop_url}"
    start_message = f"Start checking availability for {hotel_name} at \n {wd.shop_url}"
    wd.send_mail(start_title, start_message)
    last_mail_sent_time = None
    notify_interval = 10
    check_interval = 5
    max_notify_count = 5
    notify_count = 0
    title = f"Reservation for {hotel_name} is available!"
    text = f"Reservation for {hotel_name} is available!\n CLick here to book: {wd.shop_url}!"
    while True:
        time.sleep(check_interval)
        if wd.check_if_available(hotel_name):
            if last_mail_sent_time is None or (datetime.now() - last_mail_sent_time).seconds > notify_interval:
                if notify_count < max_notify_count:
                    print(f"{notify_count}\n{text}")
                    wd.send_mail(title, text)
                    last_mail_sent_time = datetime.now()
                    notify_count += 1
        else:
            last_mail_sent_time = None
            notify_count = 0
    #wd.close_driver()