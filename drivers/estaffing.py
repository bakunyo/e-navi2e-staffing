from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EStaffing:
  def __init__(self, driver, config):
    self.driver = driver
    self.login_url = config['loginUrl']
    self.company_id = config['companyId']
    self.user_id = config['userId']
    self.password = config['password']
    self.half = { 'early': '1', 'late': '2' } # 1: 上旬, 2: 下旬
    self.shift = { 'work': '1', 'absence': '2' } # 1: 出勤, 2: 年休
    self.half_now = ''
    self.working_hours_basic = { 'early': '', 'late': '' }
    self.working_hours_extra = { 'early': '', 'late': '' }

  def transcribe(self, enavi_timesheet):
    self.__login()
    self.__move_to_monthly_page()

    for dic in enavi_timesheet:
      d = dic['date']
      h = 'early' if d < 16 else 'late'

      # 上旬・下旬のページ遷移
      if h != self.half_now:
        self.__move_to_half_page(h)
        self.__set_working_hours()

      days = self.__get_days() # half of month

      day = days[d] if self.half_now == 'early' else days[d - 15]
      day_str = str(d)

      # 既に申請済ならパス
      status = day.find_element_by_name('hdnstatus' + day_str).get_attribute('value')
      if status != '': continue

      self.__request_approval(day, day_str, dic['time'])
      self.__set_working_hours()

  def working_hours(self):
    basic = self.__calc_hours(self.working_hours_basic)
    extra = self.__calc_hours(self.working_hours_extra)

    return { 'basic': basic, 'extra': extra }

  def __login(self):
    self.driver.get(self.login_url)
    login_form = self.driver.find_element_by_name('main_form')
    login_form.find_element_by_name('comid_text').send_keys(self.company_id)
    login_form.find_element_by_name('userid_text').send_keys(self.user_id)
    login_form.find_element_by_name('passwd_text').send_keys(self.password)
    login_form.find_element_by_name('Image19').click()

  def __move_to_monthly_page(self):
    self.driver.find_element_by_class_name('largeEvtBtn').click()

  def __get_days(self):
    table = self.driver.find_element_by_name('main4_form').find_element_by_tag_name('table')
    return table.find_elements_by_xpath('./tbody/tr')

  def __move_to_half_page(self, half):
    target_form = self.driver.find_element_by_name('main1_form').find_element_by_xpath(".//td[@align='left']")
    Select(target_form.find_element_by_name('SelectedCardNo')).select_by_value(self.half[half])
    target_form.find_element_by_tag_name('input').click()
    self.half_now = half

  def __request_approval(self, day, day_str, time):
    if time['attend'] == '出勤':
      # 開始時刻
      s_hh, s_mm = time['begin'].split(':')
      day.find_element_by_name('starthh_text' + day_str).send_keys(s_hh)
      day.find_element_by_name('startmm_text' + day_str).send_keys(s_mm)

      # 終了時刻
      e_hh, e_mm = time['end'].split(':')
      day.find_element_by_name('endhh_text' + day_str).send_keys(e_hh)
      day.find_element_by_name('endmm_text' + day_str).send_keys(e_mm)

      # 休憩時間
      r_hh, r_mm = time['break'].split(':')
      day.find_element_by_name('resthh_text' + day_str).send_keys(r_hh)
      day.find_element_by_name('restmm_text' + day_str).send_keys(r_mm)

    # 区分
    attend = 'work' if time['attend'] == '出勤' else 'absence'
    Select(day.find_element_by_name('hd_select' + day_str)).select_by_value(self.shift[attend])

    # 申請
    day.find_element_by_class_name('clsDayActBtn').click()
    self.driver.switch_to_alert().accept()

  def __set_working_hours(self):
    main2_form = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.NAME, 'main2_form')))
    tr = main2_form.find_element_by_xpath('p/table[1]/tbody/tr[2]')
    basic = tr.find_element_by_xpath('td[5]').text
    extra = tr.find_element_by_xpath('td[6]').text

    if basic != '_': self.working_hours_basic[self.half_now] = basic
    if extra != '_': self.working_hours_extra[self.half_now] = extra

  def __calc_hours(self, hours):
    hour = 0
    minute = 0
    for _k, v in hours.items():
      if v == '': continue

      _h, _m = [int(s) for s in v.split('_')]
      hour += _h
      m_sum = minute + _m
      hour += m_sum // 60
      minute = m_sum % 60

    return ':'.join(['{0:02d}'.format(s) for s in [hour, minute]])
