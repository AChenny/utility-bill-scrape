from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re


browser = webdriver.Chrome()


def main():
    global browser

    #login to FortisBC
    browser.get('https://accounts.fortisbc.com/')
    fortis_user = browser.find_element_by_id('loginForm:login_userid')
    fortis_password = browser.find_element_by_id('loginForm:login_password')
    fortis_loginBtn = browser.find_element_by_id('loginForm:login_login_btn')

    #Input user and password
    fortis_user.send_keys("")
    fortis_password.send_keys("")

    fortis_loginBtn.click()

    fortis_amount = browser.find_element_by_xpath('/html/body[1]/div[3]/div/div[2]/form/div[1]/div[1]/div/span[2]').text[1:]

    #login to bchydro
    browser.execute_script("window.open('https://www.bchydro.com/index.html');")
    browser.switch_to.window(browser.window_handles[1])
    browser.find_element_by_id('btnLogin').click()

    browser.find_element_by_id('email').send_keys('')
    browser.find_element_by_id('password').send_keys('')
    browser.find_element_by_id('submit-button').click()
    # time.sleep(5)
    # browser.find_element_by_xpath('/html/body/div/div[3]/div[1]/div[2]/div[1]/h1').click()

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

    print(billingPeriod.text)

    billingDays = int(re.search('Cost to date \((.*) days\):', billingPeriod.text).group(1))

    if (billingDays >= 30):
        # If the billing days is greater than or = 30 then take the cost to date and divide by billing days and then multiply by 30
        costToDate = int(re.search('\$(.*)\* or', billingPeriod.text).group(1))
        costToDate = (costToDate/billingDays) * 30
    else:
        costToDate = browser.find_element_by_class('bill_amount')

    print(costToDate)




main()
