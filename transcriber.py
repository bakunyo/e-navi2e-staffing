import json
from selenium import webdriver
from selenium.webdriver.support.ui import Select

config = json.load(open('config.json', 'r'))

driver = webdriver.Firefox()
driver.maximize_window()

# e-navi login
login_url = 'https://www.enavi-ts.net/ts-h-staff/Staff/login.aspx'
company_id = config['e-navi']['companyId']
staff_no = config['e-navi']['staffNo']
password = config['e-navi']['password']
urlDir = config['e-navi']['urlDir']

driver.get(login_url + '?ID=' + company_id)
login_form = driver.find_element_by_id('inputid')
login_form.find_element_by_name('TextStaffNo').send_keys(staff_no)
login_form.find_element_by_name('TextPassword').send_keys(password)
login_form.find_element_by_name('BtnOk').click()

# open monthly page
driver.get('https://web.enavi-ts.net/' + urlDir + '/Staff/month/monthwork.aspx');

timesheet = driver.find_element_by_id('TableTimesheet')
days = timesheet.find_elements_by_tag_name('tr')

columns = { 'date': 1, 'status': 4, 'attend': 6, 'begin': 7, 'end': 8, 'break': 9, 'basic': 10, 'extra': 11 }
enavi_list = []
cells_by_day = [day.find_elements_by_tag_name('td') for day in days]
for day_cells in cells_by_day:
  date = day_cells[columns['date']].text
  if date == '日付': continue

  key = int(date.split('/')[1])
  day = {}
  [day.update({ k: day_cells[v].text}) for k, v in columns.items()]

  if any([day['status'] == s for s in ['承認済', '依頼中']]):
    enavi_list.append({ 'date': key, 'time': day })

# e-staffing
login_url = config['e-staffing']['loginUrl']
company_id = config['e-staffing']['companyId']
user_id = config['e-staffing']['userId']
password = config['e-staffing']['password']

driver.get(login_url)
login_form = driver.find_element_by_name('main_form')
login_form.find_element_by_name('comid_text').send_keys(company_id)
login_form.find_element_by_name('userid_text').send_keys(user_id)
login_form.find_element_by_name('passwd_text').send_keys(password)
login_form.find_element_by_name('Image19').click()

driver.find_element_by_class_name('largeEvtBtn').click() # 勤怠入力

half = { 'early': '1', 'late': '2' } # 1: 上旬, 2: 下旬
shift = { 'work': '1', 'absence': '2' }

# for day in days
half_now = ''
for dic in enavi_list:
  d = dic['date']
  h = 'early' if d < 16 else 'late'

  # 上旬・下旬のページ遷移
  if h != half_now:
    target_form = driver.find_element_by_name('main1_form').find_element_by_xpath(".//td[@align='left']")
    Select(target_form.find_element_by_name('SelectedCardNo')).select_by_value(half[h])
    target_form.find_element_by_tag_name('input').click()
    half_now = h

    # half-monthly
    timesheet = driver.find_element_by_name('main4_form').find_element_by_tag_name('table')
    days = timesheet.find_elements_by_xpath('./tbody/tr')

  day = days[d] if d < 16 else days[d - 15]
  sd = str(d)
  status = day.find_element_by_name('hdnstatus' + sd).get_attribute('value')
  if status != '': continue

  time = dic['time']
  s_hh, s_mm = time['begin'].split(':')
  day.find_element_by_name('starthh_text' + sd).send_keys(s_hh)
  day.find_element_by_name('startmm_text' + sd).send_keys(s_mm)

  e_hh, e_mm = time['end'].split(':')
  day.find_element_by_name('endhh_text' + sd).send_keys(e_hh)
  day.find_element_by_name('endmm_text' + sd).send_keys(e_mm)

  r_hh, r_mm = time['break'].split(':')
  day.find_element_by_name('resthh_text' + sd).send_keys(r_hh)
  day.find_element_by_name('restmm_text' + sd).send_keys(r_mm)

  attend = 'work' if time['attend'] == '出勤' else 'absence'
  Select(day.find_element_by_name('hd_select' + sd)).select_by_value(shift[attend])

  day.find_element_by_class_name('clsDayActBtn').click()
  driver.switch_to_alert().accept()

print('completed!')
