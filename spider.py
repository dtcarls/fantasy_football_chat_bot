import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

import settings

driver = webdriver.Firefox()

driver.get("http://games.espn.go.com/ffl/signin")
WebDriverWait(driver,1000).until(expected_conditions.presence_of_all_elements_located((By.XPATH, "(//iframe)")))
driver.switch_to.frame('disneyid-iframe')
time.sleep(2)

driver.find_elements(By.TAG_NAME, 'input')[0].send_keys(settings.username)
driver.find_elements(By.TAG_NAME, 'input')[1].send_keys(settings.password)
driver.find_element(By.TAG_NAME, 'button').click()