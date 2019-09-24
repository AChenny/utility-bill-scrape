from selenium import webdriver
from selenium.webdriver.common.keys import Keys


browser = webdriver.Chrome()

def main ():
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
    # fortis_format = fortis_amount.text[1:]
    print(fortis_amount)




main()