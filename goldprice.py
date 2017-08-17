import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
import time

link = "http://goldprice.org/spot-gold.html"
driver = webdriver.PhantomJS()

def multiselect_set_selections(driver, element_id, labels):
    el = driver.find_element_by_id(element_id)
    for option in el.find_elements_by_tag_name('option'):
        if option.text in labels:
            option.click()
            
while(True):
    driver.get(link)
    driver.set_window_size(1120, 550)
    multiselect_set_selections(driver,'gpxtickerLeft_curr', 'SGD     Singapore Dollar')
    multiselect_set_selections(driver,'gpxtickerLeft_wgt-au', 'g')
    
    soup = BS(driver.page_source,'html.parser')

    container = soup.find('div',{'class':'panel-pane pane-block pane-gpx-tickers-gpx-tickers-block'})

    #print(container)

    gpxtickerLeft_price = container.find('span',{'id':'gpxtickerLeft_price'})

    #print(gpxtickerLeft_price)

    sgdPrice = gpxtickerLeft_price.next_element

    print("sgdPrice : " + str(sgdPrice))
    
    time.sleep(5)
