from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint

scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)



class Bill:
    def __init__(self, cost, billingperiod):
        self.cost = cost
        self.billingperiod = billingperiod

    def printBill(self):
        print('Cost: ' + self.cost + '\n' + 'Billing Period: ' + self.billingperiod)

browser = webdriver.Chrome()


def main():
    global browser

    #User creds
    fortisUser = ''
    fortisPass = ''

    bcHydUser = ''
    bcHydPass = ''

    sheetTitle = ''
    sheet = client.open(sheetTitle).sheet1

    #login to FortisBC
    browser.get('https://accounts.fortisbc.com/')
    browser.find_element_by_id('loginForm:login_userid').send_keys(fortisUser)
    browser.find_element_by_id('loginForm:login_password').send_keys(fortisPass)
    browser.find_element_by_id('loginForm:login_login_btn').click()

    fortis_amount = browser.find_element_by_xpath('/html/body[1]/div[3]/div/div[2]/form/div[1]/div[1]/div/span[2]').text[1:]
    fortis_lastPayment = browser.find_element_by_xpath('/html/body[1]/div[3]/div/div[2]/form/div[1]/div[3]/div/p/small').text

    fortisBill = Bill(fortis_amount, fortis_lastPayment)

    #login to bchydro
    browser.execute_script("window.open('https://www.bchydro.com/index.html');")
    browser.switch_to.window(browser.window_handles[1])
    browser.find_element_by_id('btnLogin').click()

    browser.find_element_by_id('email').send_keys(bcHydUser)
    browser.find_element_by_id('password').send_keys(bcHydPass)
    browser.find_element_by_id('submit-button').click()


    try:
        accountDropdown = WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div[3]/div[1]/div[2]/div[1]/h1')))
    except TimeoutException:
        print("Account not found.")

    accountDropdown.click()

    try:
        accountLink = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/div[3]/div[1]/div[2]/div[1]/div/table/tbody/tr/td[1]/a')))
    except TimeoutException:
        print("Account not found.")

    accountLink.click()
    #Grab bill amount from BC Hydro
    try:
        billingPeriod = WebDriverWait(browser, 5).until(
            EC.presence_of_element_located((By.ID, 'dval_currentValue')))
    except TimeoutException:
        print("Account not found.")

    billingDays = int(re.search('Cost to date \((.*) days\):', billingPeriod.text).group(1))

    if billingDays >= 30:
        # If the billing days is greater than or = 30 then take the cost to date and divide by billing days and then multiply by 30
        costToDate = int(re.search('\$(.*)\* or', billingPeriod.text).group(1))
        costToDate = (costToDate/billingDays) * 30
    else:
        costToDate = browser.find_element_by_class('bill_amount')

    billingDate = browser.find_element_by_xpath('/html/body/div/div[3]/div[2]/div[1]/div[2]/p[1]').text
    bcHydroBill = Bill(str(costToDate), billingDate)


    #Add bills to google sheets
    #Col2: Billing period Col3: BcHydro bill Col4: Fortisbill
    confirmation = input('BC Hydro Cost: ' + bcHydroBill.cost + '\nFortis Cost: ' + fortisBill.cost + '\n'
                         + 'Please confirm that these bills are correct. (y/n)\n')
    if confirmation == 'y':
        sheet.update_cell(len(sheet.col_values(3)) + 1, 3, bcHydroBill.cost)
        sheet.update_cell(len(sheet.col_values(4)) + 1, 4, fortisBill.cost)
    else:
        print('Oops.')


main()
