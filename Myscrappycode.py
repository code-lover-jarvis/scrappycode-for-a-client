from selenium import webdriver
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
from selenium.webdriver.common.keys import Keys
import json
import pandas as pd
from glob import glob            #to find the filename of csv


filename=glob(r"path to particular csv file/*.csv")[0]

options = Options()
options.headless=True
                                            #to hide the browser, to make it visible, comment the line

usr='some user id'
pwd='corresponding password'
r=list()
rr=list()
retail=list()
discount=list()
skucode=list()

# options.add_experimental_option("excludeSwitches", ["enable-logging"])           #if you have error related to the 'bluetooth adapter failed' which is caused due to version mismatch between the webdriver and chrome
driver = webdriver.Chrome(options=options, executable_path=r'''C:\Users\username\.wdm\drivers\chromedriver\win32\85.0.4183.87\chromedriver.exe''')
driver.get('the url to website that requires login')
print ("Website Opened")
sleep(3)

driver.find_element_by_name('emailOrMobile').send_keys(usr)        #entering id
print ("Id entered")

driver.find_element_by_name('loginPassword').send_keys(pwd)          #entering password
print ("Password entered")

driver.find_element_by_xpath('''//*[@id="root"]/div/div[1]/div[2]/div/div[2]/div/form/div[4]/button''').click()      #clicking login button
sleep(8)

driver.find_element_by_xpath('''//*[@id="allProductsTabs__resale"]/div''').click()          #clicking resale button
sleep(8)



page_source=driver.page_source         #fetching the page to parse and get the edit of each product
soup = BeautifulSoup(page_source, "html.parser")
tgs=soup('div')
for tag in tgs:
    lnk=tag.get('data-link','jjj')
    r.append(lnk)
for i in r:
    if(i !='jjj'):
        nxturl='https://sorry.i-can't-show-the-url/seller/edit-products-resale?ids=' + i[-10::1]
        sleep(8)
        driver.get(nxturl)       #moving forward to each product
        page_source=driver.page_source      # fetching the page to parse and get the variant quantity
        soup = BeautifulSoup(page_source, "html.parser")
        tags=soup('div')
        txt=soup.get_text()
        txt=txt.strip().split(':')
        ret=txt[4]
        ret=re.findall(".([0-9]+)",ret)[0]        #ret is the retail price
        dis=txt[5]
        dis=re.findall(".([0-9]+)",dis)[0]        #dis is the price after discount
        SKUcode=txt[2]
        SKUcode=re.findall("([A-Za-z0-9]+)",SKUcode)[0]
        retail.append(ret)
        discount.append(dis)
        skucode.append(SKUcode)
        for tag in tags:
            lnk=tag.get('products-data','jjj')
            rr.append(lnk)
data={'code':skucode, 'retail':retail, 'discount':discount}
df = pd.DataFrame(data)             #df is the table containing skucode and corresponding retail and discounted price

df1=pd.read_csv(filename)
val=int()
val1=float()
val2=float()
for j in rr:
    if(j != 'jjj'):
        reqrdthngs=j
        js=json.loads(reqrdthngs)

        for variants in (js[0]["productVariants"]):
            k=js[0]["product"]["productName"]
            kk=re.findall("\([Code:]+\s([A-Za-z0-9]+)",k)[0]          #kk is the skucode, variants["productVariantDescription"] is the variant name, variants["productVariantQuantity"] is the  variant quantity
            for i, rows in df1.iterrows():
                if(rows[32]==kk and rows[40]==variants["productVariantDescription"]):
                    val=variants["productVariantQuantity"]
                    df1.at[i,'Stock']=val
                if(rows[32]==kk):
                    val1=df.loc[(df['code']==kk),'discount']
                    val2=df.loc[(df['code']==kk),'retail']
                    df1.at[i,'Sale price']=val1
                    df1.at[i,'Regular price']=val2

df1.to_csv('updated_CSVready_to_import.csv')
print ("Done")
input('Press Enter to quit')
driver.quit()
print("Finished")
