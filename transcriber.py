import json
from selenium import webdriver
from drivers.enavi import *
from drivers.estaffing import *

config = json.load(open('config.json', 'r'))

driver = webdriver.Firefox()
driver.maximize_window()

timesheet = ENavi(driver, config['e-navi']).get_timesheet()
EStaffing(driver, config['e-staffing']).transcribe(timesheet)

print('completed!')
