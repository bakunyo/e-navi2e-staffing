class ENavi:
  def __init__(self, driver, config):
    self.driver = driver
    self.staff_no = config['staffNo']
    self.password = config['password']
    self.columns = { 'date': 1, 'status': 4, 'attend': 6, 'begin': 7, 'end': 8, 'break': 9, 'basic': 10, 'extra': 11 }
    self.login_url = 'https://www.enavi-ts.net/ts-h-staff/Staff/login.aspx?ID=' + config['companyId']
    self.monthly_url = 'https://web.enavi-ts.net/' + config['urlDir'] + '/Staff/month/monthwork.aspx'

  def get_timesheet(self):
    self.__login()
    self.__move_monthly_page()

    enavi_list = []

    for day_cells in self.__cells_by_day():
      date = day_cells[self.columns['date']].text
      if date == '日付': continue

      key = int(date.split('/')[1])
      day = self.__day_info(day_cells)

      if any([day['status'] == s for s in ['承認済', '依頼中']]):
        enavi_list.append({ 'date': key, 'time': day })

    return enavi_list

  def working_hours(self):
    basic = self.driver.find_element_by_id('LblTimes01').text
    extra = self.driver.find_element_by_id('LblTimes02').text
    late_evening = self.driver.find_element_by_id('LblTimes03').text

    return { 'basic': basic, 'extra': extra, 'late_evening': late_evening }

  def __login(self):
    self.driver.get(self.login_url)

    login_form = self.driver.find_element_by_id('inputid')
    login_form.find_element_by_name('TextStaffNo').send_keys(self.staff_no)
    login_form.find_element_by_name('TextPassword').send_keys(self.password)
    login_form.find_element_by_name('BtnOk').click()

  def __move_monthly_page(self):
    self.driver.get(self.monthly_url)

  def __days(self):
    timesheet = self.driver.find_element_by_id('TableTimesheet')
    return timesheet.find_elements_by_tag_name('tr')

  def __cells_by_day(self):
    return [day.find_elements_by_tag_name('td') for day in self.__days()]

  def __day_info(self, day_cells):
    day = {}
    [day.update({ k: day_cells[v].text}) for k, v in self.columns.items()]
    return day

