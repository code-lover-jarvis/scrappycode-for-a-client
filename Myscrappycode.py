from selenium import webdriver
from time import sleep
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from datetime import datetime
import re
import csv
import pickle
from selenium.webdriver.common.keys import Keys
import json
import pandas as pd
from glob import glob            #to find the filename of csv
starttime = datetime.now()

filename=glob(r"C:\Users\path to the csv file\*.csv")[0]

options = Options()
# options.headless=True
                                            #to hide the browser, to make it visible, comment the line

r=list()
btn=[1,2,3]
retail=list()
discount=list()
skucode=list()
fskucode=list()
sk = dict()
pgnum = 1

baseurl="https://***.***/***/****/all-products/resale"

usr = '*********'
pwd = '************'

df1=pd.read_csv(filename)
# options.add_experimental_option("excludeSwitches", ["enable-logging"])     #if you have error related to the 'bluetooth adapter failed' which is caused due to version mismatch between the webdriver and browser
driver = webdriver.Firefox(executable_path=r'''C:\Program Files (x86)\Mozilla Maintenance Service\geckodriver.exe''')
driver.get('https://***.*******.***')
print ("Website Opened")
sleep(3)
try:
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)
except:
    driver.find_element_by_name('emailOrMobile').send_keys(usr)        #entering id
    print ("Id entered")

    driver.find_element_by_name('loginPassword').send_keys(pwd)          #entering password
    print ("Password entered")

    driver.find_element_by_xpath('''/html/body/div/div/div[1]/div[1]/div/div[1]/div/form/div[4]/button''').click()      #clicking login button
    sleep(8)
driver.get(baseurl)
sleep(3)
pgchoice = input("Do you want to scrap from beginning?...(y/n)")
if(pgchoice == 'n'):
    pgnum = int(input("Enter the page no."))
    for b in range(pgnum):
        driver.find_element_by_xpath('''//*[@id="sellerAllProductsResale"]/div[8]/button[2]''').click()
        sleep(3)
        baseurl=driver.current_url
else:
    pass

while(btn):
    print("page number =", pgnum)
    page_source=driver.page_source         #fetching the page to parse and get the edit of each product
    soup = BeautifulSoup(page_source, "html.parser")
    tgs=soup('div')
    tgs1=soup('button')
    r.clear()
    btn.clear()
    retail.clear()
    discount.clear()
    skucode.clear()
    for tag in tgs:
        lnk=tag.get('data-link','jjj')
        r.append(lnk)
    for tag in tgs1:
        bttn=tag.get('disabled','jjj')
        btn.append(bttn)
    r = list(filter(lambda a: a != 'jjj', r))
    for i in range(0, len(r), 5):
        constcode='https://***.*******.***/****/edit-products-resale?ids='
        driver.get(constcode + r[i][-10::1])
        try:
            driver.execute_script("window.open('{}', 'secondtab');".format(constcode + r[i+1][-10::1]))
        except:
            pass
        try:
            driver.execute_script("window.open('{}', 'thirdtab');".format(constcode + r[i+2][-10::1]))
        except:
            pass
        try:
            driver.execute_script("window.open('{}', 'fourthtab');".format(constcode + r[i+3][-10::1]))
        except:
            pass
        try:
            driver.execute_script("window.open('{}', 'fifthtab');".format(constcode + r[i+4][-10::1]))
        except:
            pass
        for m in range(5):
            sleep(3)
            driver.switch_to.window(driver.window_handles[m])
            sleep(2)
            page_source=driver.page_source      # fetching the page to parse and get the variant quantity
            soup = BeautifulSoup(page_source, "html.parser")
            tags=soup('div')
            txt=soup.get_text()
            txt=txt.strip().split(':')
            ret=txt[4]
            try:
                ret=re.findall(".([0-9]+)",ret)[0]        #ret is the retail price
            except:
                print("Trying Again...")
                sleep(2)
                page_source=driver.page_source      # fetching the page to parse and get the variant quantity
                soup = BeautifulSoup(page_source, "html.parser")
                tags=soup('div')
                txt=soup.get_text()
                txt=txt.strip().split(':')
                ret=txt[4]
                try:
                    ret=re.findall(".([0-9]+)",ret)[0]
                except:
                    SKUcode=txt[2]
                    SKUcode=re.findall("([A-Za-z0-9]+)",SKUcode)[0]
                    print("There is no Retail Price for product with SKUCode {}".format(SKUcode))
                    fskucode.append(SKUcode)
                    print("Skipping this product...")
                    continue
            dis=txt[5]
            dis=re.findall(".([0-9]+)",dis)[0]        #dis is the price after discount
            SKUcode=txt[2]
            SKUcode=re.findall("([A-Za-z0-9]+)",SKUcode)[0]
            sk[SKUcode] = (ret, dis)
            for tag in tags:
                lnk=tag.get('products-data','jjj')
                if(lnk != 'jjj'):
                    js=json.loads(lnk)

                    for variants in (js[0]["productVariants"]):
                        k=js[0]["product"]["productName"]
                        kk=re.findall("\([Code:]+\s([A-Za-z0-9]+)",k)[0]          #kk is the skucode, variants["productVariantDescription"] is the variant name, variants["productVariantQuantity"] is the  variant quantity
                        print(variants["productVariantDescription"],'has quantity',variants["productVariantQuantity"], 'of product with SKUCode', kk)
                        try:
                            jstlttr=re.findall("([0-9A-Za-z]+)",variants["productVariantDescription"])[0]
                        except:
                            jstlttr=variants["productVariantDescription"]
                        if(jstlttr=='2XL'):
                            jstlttr='XXL'
                            print(kk, "and", jstlttr)
                        for i, rows in df1.iterrows():
                            if(rows[32]==kk):
                                (val2, val1) = sk[kk]
                                print(val1, val2)
                                df1.at[i,'Sale price']=val1
                                df1.at[i,'Regular price']=val2
                                print("second success")
                            if(rows[32]==kk and rows[40]==jstlttr):
                                val=variants["productVariantQuantity"]
                                df1.at[i,'Stock']=val
                                print("success")

            print("page number =", pgnum)
            print("Changing window...")
            if(m == 4):
                driver.switch_to.window(driver.window_handles[0])
                break
    if(btn[-1]==''):
        break
    else:
        pgnum += 1
        driver.switch_to.window(driver.window_handles[0])
        driver.get(baseurl)
        driver.find_element_by_xpath('''//*[@id="sellerAllProductsResale"]/div[8]/button[2]''').click()
        sleep(5)
        baseurl=driver.current_url

df1.to_csv('updated_CSVready_to_import.csv', index = False, quoting = csv.QUOTE_NONNUMERIC)
print("Failed to update the details of product with following SKUCodes...")
print(fskucode)
print ("Done")
input('Press Enter to quit')
driver.quit()
print("Finished...", datetime.now() - starttime)
