import json
from selenium import webdriver
from drivers.enavi import *
from drivers.estaffing import *

config = json.load(open('config.json', 'r'))

driver = webdriver.Firefox()
driver.maximize_window()

enavi = ENavi(driver, config['e-navi'])
timesheet = enavi.get_timesheet()
enavi_working_hours = enavi.working_hours()

estaffing = EStaffing(driver, config['e-staffing'])
estaffing.transcribe(timesheet)
estaffing_working_hours = estaffing.working_hours()

print('enavi: ' + str(enavi_working_hours))
print('estaffing: ' + str(estaffing_working_hours))
print('completed!')
