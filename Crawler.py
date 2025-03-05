from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchFrameException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


def send_response(done, message=''):
    print(f"{message}")


class Crawl:

    def __init__(self, baseurl, executable_path):
        self.captcha_text = None

        self.base_url = baseurl

        # Create ChromeOptions instance
        chrome_options = Options()
        # Enable headless mode
        chrome_options.add_argument("--headless")
        # Optionally, you can disable GPU acceleration for better compatibility
        chrome_options.add_argument("--disable-gpu")

        # Create a new instance of the Chrome driver with options
        service = Service(executable_path=executable_path)
        # self.driver = webdriver.Chrome(service=service, options=chrome_options)

        # Create a new instance of the Chrome driver
        # service = Service(executable_path=executable_path)
        self.driver = webdriver.Chrome(service=service)

    # %%
    def waiting(self, element='body', timeout=10):
        try:
            wait = WebDriverWait(self.driver, timeout)
            if element == 'body':
                wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            else:
                wait.until(EC.presence_of_element_located((By.ID, element)))
            return True
        except TimeoutException:
            send_response(0, message="CODE:100 : Timed out waiting for page to load")

    # %%
    def set_link(self, link, waiting_element='body', timeout=10):
        if link is None:
            raise ValueError("The link provided is None.")
        # print(f"Original link: {link}")
        if not link.startswith(("http://", "https://")):
            link = "http://" + link
        # print(f"Formatted link: {link}")
        self.driver.get(link)
        self.waiting(waiting_element, timeout)

    # %%
    def find_element(self, identifier_type, identifier_value):
        try:
            if identifier_type == 'id':
                return self.driver.find_element(By.ID, identifier_value)
            elif identifier_type == 'class':
                return self.driver.find_element(By.CLASS_NAME, identifier_value)
            elif identifier_type == 'x_path':
                return self.driver.find_element(By.XPATH, identifier_value)
            elif identifier_type == 'tag_name':
                return self.driver.find_element(By.TAG_NAME, identifier_value)
            elif identifier_type == 'name':
                return self.driver.find_element(By.NAME, identifier_value)
            else:
                print(f"Invalid identifier type: {identifier_type}")
                return None
        except NoSuchElementException:
            send_response(0, message=f"CODE:101 : Element not found using {identifier_type}: {identifier_value}")
            return None

    # %%
    def fill_input(self, identifier_type, identifier_value, input_value, rewrite=True):
        element = self.find_element(identifier_type, identifier_value)

        if element:
            try:
                if rewrite:
                    element.clear()  # Clear any existing text in the input field
                element.send_keys(input_value)
                # print(f"Input element filled successfully with value: {input_value}")
                return True
            except Exception as e:
                send_response(0,
                              message=f"CODE:102 : Error filling input element: {identifier_type} {identifier_value}")
        return False

    # %%
    def click_element(self, identifier_type, identifier_value):
        element = self.find_element(identifier_type, identifier_value)
        if element:
            try:
                element.click()
                # print(f"Element clicked successfully.")
                return True
            except Exception as e:
                send_response(0,
                              message=f"CODE:103 : Error clicking element: {identifier_type} {identifier_value}")
        return False

    # %%
    def switch_to_frame(self, frame_identifier_type, frame_identifier_value):
        try:
            frame_element = self.find_element(frame_identifier_type, frame_identifier_value)
            self.driver.switch_to.frame(frame_element)
            return True
        except NoSuchFrameException as e:
            send_response(0,
                          message=f"CODE:104 : Error switching to iframe: {frame_identifier_type} {frame_identifier_value}")
            return False

    # %%
    def switch_to_default(self):
        try:
            self.driver.switch_to.default_content()
            return True
        except NoSuchFrameException as e:
            send_response(0, message=f"CODE:105 : Error switching to default content")
            return False

    # %%
    def select_option(self, identifier_type, identifier_value, option_value):
        element = self.find_element(identifier_type, identifier_value)

        if element and element.tag_name.lower() == 'select':
            try:
                select_element = Select(element)
                select_element.select_by_value(option_value)
                # Alternatively, you can use select_element.select_by_visible_text("Option Text")
                # or select_element.select_by_index(index)
                # print(f"Option '{option_value}' selected successfully.")
                return True
            except Exception as e:
                send_response(0,
                              message=f"CODE:106 : Error selecting option: {identifier_type} {identifier_value}")
        else:
            send_response(0, message=f"CODE:107 : Element is not a <select> tag.")
        return False

    # %%
    def press_key(self, identifier_type, identifier_value, key):
        element = self.find_element(identifier_type, identifier_value)
        if element:
            try:
                if key == 'return':
                    key = Keys.RETURN

                else:
                    key = getattr(Keys, key.upper())
                element.send_keys(key)
                # print(f"{key} key pressed successfully")
                return True
            except Exception as e:
                send_response(0,
                              message=f"CODE:108 : Error pressing {key} key: {identifier_type} {identifier_value}")
        return False

    # %%
    def get_content(self, identifier_type, identifier_value, content_type='text'):
        element = self.find_element(identifier_type, identifier_value)
        if element:
            try:
                if content_type == 'text':
                    return element.text
                elif content_type == 'html':
                    return element.get_attribute('innerHTML')
                else:
                    send_response(0, message=f"CODE:109 : Invalid content type: {content_type}")
                    return None
            except Exception as e:
                send_response(0,
                              message=f"CODE:110 : Error getting content from element: {identifier_type} {identifier_value}")
                return None
        return None

    def open_new_tab(self):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])

    def switch_to_tab(self, index):
        self.driver.switch_to.window(self.driver.window_handles[index])