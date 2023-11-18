import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from fuzzywuzzy import fuzz
import requests
from bs4 import BeautifulSoup
import pandas as pd


def find_matching_products(daraz_product_name, daraz_product_price, pbo_product_name, pbo_product_price, low, match_name, mdp, mpp, threshold=88):
    n = len(daraz_product_name)
    m = len(pbo_product_name)
    for i in range(n):
        for j in range(m):
            similarity_score = fuzz.ratio(daraz_product_name[i], pbo_product_name[j])
            if similarity_score >= threshold:
                match_name.append(daraz_product_name[i])
                mdp.append(daraz_product_price[i])
                mpp.append(pbo_product_price[j])
                if daraz_product_price[i]>pbo_product_price[j]:
                    low.append("Pickaboo")
                elif daraz_product_price[i]<pbo_product_price[j]:
                    low.append("Daraz")
                else:
                    low.append("Daraz/Pickaboo")


#Set up the WebDriver
url = "https://www.daraz.com.bd/smartphones/?spm=a2a0e.home.cate_6.1.735212f7HQ2j9M"  #daraz web
path = "/usr/bin/chromedriver"
s = Service(path)
options = webdriver.ChromeOptions()
options.add_experimental_option("detach",True)
driver = webdriver.Chrome(service=s, options=options)
driver.get(url)
time.sleep(5)

daraz_product_price = []
daraz_product_name = []

# Define the number of pages you want to scrape (14 in your case)
num_pages_to_scrape = 9

for page_num in range(1, num_pages_to_scrape):
    if page_num == 1:
        url = "https://www.daraz.com.bd/smartphones/?spm=a2a0e.home.cate_6.1.735212f7HQ2j9M"
    else:
        url = "https://www.daraz.com.bd/smartphones/?spm=a2a0e.home.cate_6.1.735212f7HQ2j9M&page="+str(page_num)
    driver.get(url)
    time.sleep(10)
    name = driver.find_elements(By.CLASS_NAME, "title--wFj93")
    price = driver.find_elements(By.CLASS_NAME, "price--NVB62")

    for i in name:
        daraz_product_name.append(i.text.upper())
    for i in price:
        daraz_product_price.append(i.text)

#df = pd.DataFrame({"Product_Name" : daraz_product_name, "Product_Price" : daraz_product_price})
#df.to_csv("Daraz.csv")
print(daraz_product_price)
print(daraz_product_name)
print(len(daraz_product_name), len(daraz_product_price))
time.sleep(2)

url = "https://www.pickaboo.com/product/smartphone/"
driver.get(url)
time.sleep(10)
got = driver.find_elements(By.CLASS_NAME, "product-one__single__inner__content")
pbo_product_name = []
pbo_product_price = []

for k in range(8):
    final = []
    for i in got:
        p = i.text
        n = len(p)
        point = 0
        temp = []
        for j in range(n):
            if p[j] == '\n':
                temp.append(p[point:j])
                point = j+1
            elif j == n-1:
                temp.append(p[point:j+1])
        final.append(temp)

    n = len(final)
    for i in range(n):
        if final[i][1]!="Out of stock":
            pbo_product_name.append(final[i][0].upper())
            sen = final[i][1]
            if sen.count('৳') == 2:
                place = sen.find('৳',1)
                pbo_product_price.append(sen[0:place])
            else:
                pbo_product_price.append(sen)

    if k<=7:
        button = driver.find_element(By.XPATH,'//button[@aria-label = "Go to next page"]')
        driver.execute_script("arguments[0].click();", button)
        time.sleep(5)
        got = driver.find_elements(By.CLASS_NAME, "product-one__single__inner__content")

#df2 = pd.DataFrame({"Product_Name" : pbo_product_name, "Product_Price" : pbo_product_price})
#df2.to_csv("Pickaboo.csv")
low =[]
match_name = []
mdp = []
mpp = []
find_matching_products(daraz_product_name, daraz_product_price, pbo_product_name, pbo_product_price, low, match_name, mdp, mpp)
df = pd.DataFrame({"Product_Name": match_name, "Daraz_Price": mdp, "Pickaboo_Price": mpp, "Target_Shop": low})
df.to_csv("Best_Deal.csv")