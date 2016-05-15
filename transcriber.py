import json
from IPython import embed
from selenium import webdriver

config = json.load(open('config.json', 'r'))

driver = webdriver.Firefox()
driver.maximize_window()

# e-navi login
login_url = 'https://www.enavi-ts.net/ts-h-staff/Staff/login.aspx'
company_id = config['e-navi']['companyId']
staff_no = config['e-navi']['staffNo']
password = config['e-navi']['password']

driver.get(login_url + '?ID=' + company_id)
login_form = driver.find_element_by_id('inputid')
login_form.find_element_by_name('TextStaffNo').send_keys(staff_no)
login_form.find_element_by_name('TextPassword').send_keys(password)
login_form.find_element_by_name('BtnOk').click()

# open monthly page
driver.get('https://web.enavi-ts.net/cs-staff-rks/Staff/month/monthwork.aspx');

timesheet = driver.find_element_by_id('TableTimesheet')
days = timesheet.find_elements_by_tag_name('tr')
