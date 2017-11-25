# uncomment pyvirtual display, os path set when running code on server
import os
os.environ["PATH"] += os.pathsep + '/root'
from random import randint
import time
import pandas as pd
import json
import requests


#from pyvirtualdisplay import Display
#from easyprocess import EasyProcess
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import re

delay = 3 # seconds
# try:
#     WebDriverWait(browser, delay).until(EC.presence_of_element_located(browser.find_element_by_id('IdOfMyElement')))
#     print "Page is ready!"
# except TimeoutException:
#     print "Loading took too much time!"

# function to write to file
def file_write(data,header):
	with open('scraped_data_paytm.txt', 'w') as f:
		f.write(json.dumps(data))
	data_frame = pd.DataFrame.from_dict(data, orient='index').reset_index()
	data_frame.to_csv('scraped_data_paytm.csv',columns=header,index=False)
	time.sleep(10)
	return True

# function to clean the special characters from shopclues search terms
def clean(search):
	search = search.replace('+',' ')
	search = search.replace('-',' ')
	search = search.replace('/',' ')
	search = search.replace('\\',' ')
	search = search.replace('(',' ')
	search = search.replace(')',' ')
	search = re.sub(' +',' ',search)
	#print search
	return search


# function to get the amazon search url
def get_price_amazon(driver,search,data,index):
	f=dict()
	try:
		driver.get(search)
		driver.implicitly_wait(20)
		price=0
		try:
			if driver.find_element_by_id('priceblock_ourprice'):
				price=driver.find_element_by_id('priceblock_ourprice')
				tp=price.text
				dp=tp.replace(',','')
				f['price']=dp
				f['Avail']='Y'
				return f
		except NoSuchElementException:
			f['price']=''
			f['Avail']='N'
			return f
			pass
	except NoSuchElementException:
		#print 'went into exception'
		f['price']=''
		f['Avail']='N'
		return f
		pass
		#return "Error"

def checkProduct_Flipkart(driver,data):
    if driver.find_element_by_css_selector('RIBRtX'):
	    data[index]['Flipkart Availability']='Y'
	    return True
    else:
	data[index]['Flipkart Availability']='N'
	return False

# function to get the flipkart search url
def get_price_flipkart(driver,search,data,index):
	d=dict()
	try:
		driver.get(search)
		tp=0
		try:
			if driver.find_element_by_css_selector('._3xgqrA'):
				x='N'
		except NoSuchElementException:
			x='Y'
			pass
		inputElement = driver.find_element_by_class_name("_1vC4OE")
		price = inputElement.text
		tp=price[1:]
		tp=tp.replace(',','')
		d['price']=tp
		d['Avail']=x
		return d
	except NoSuchElementException:
		d['price']=tp
		d['Avail']=x
		return d
		pass	
def checkProduct_SD(driver,data):
	if driver.find_element_by_xpath("//meta[@itemprop='availability']"):
		data[index]['Snapdeal Availability']='Y'
	else:
		data[index]['Snapdeal Availability']='N'
		return False

# function to get the snapdeal search url
def get_url_snapdeal(driver,search,data):
	try:
		driver.get('https://www.snapdeal.com/')
		inputElement = driver.find_element_by_id("inputValEnter")
		inputElement.send_keys(search)
		inputElement.send_keys(Keys.ENTER)
		avail=checkProduct_SD(driver,data)
		if avail == False:
			return
		#links = driver.find_elements_by_css_selector('a.dp-widget-link.noUdLine.hashAdded')
		price = driver.find_elements_by_css_selector('payBlkBig')
		
		#print price.text
		#for link in links:
			#print link.get_attribute("href")
			#snapdeal = link.get_attribute("href")
			#break
		#return snapdeal
		data[index]['Snapdeal Selling Price']=price.text
	except Exception as e:
		print e
		#return "Error"

def checkProduct_Paytm(driver,data):
	if driver.find_element_by_css_selector('_12d4'):
		data[index]['Paytm Availability']='Y'
		return True
	else:
		data[index]['Paytm Availability']='N'
		return False
		
# function to get the paytm search url
def get_url_paytm(driver,search,data):
	driver.get('https://paytm.com/')
	paytm = 'Error'
	time.sleep(2)
	inputElement = driver.find_element_by_css_selector("input[type^=search]")
	print inputElement
	inputElement.send_keys(search)
	time.sleep(7)
	inputElement.send_keys(Keys.ENTER)
	time.sleep(2)
	avail=checkProduct_Paytm(driver,data)
	if avail == False:
		return
	links = driver.find_elements_by_class_name('_8vVO')
	price = driver.find_elements_by_css_selector('_1d5g')
	data[index]['Paytm Selling Price']=price.text
	#return paytm



def get_url(driver,search,data,index):
	search = clean(search)
	get_url_amazon(driver,search,data,index)
	#get_url_flipkart(driver,search,data,index)
	#get_url_snapdeal(driver,search,data,index)
	#get_url_paytm(driver,search,data,index)
	#return True
	#return {'flipkart':url_flipkart,'snapdeal':url_snapdeal}

def main():
	# get name of product
	driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
	df = pd.read_csv('competitor.csv')
	header=["FlipKart Title","FlipKart Assured","FlipKart Selling Price","FlipKart Total Discount","Amazon Title","Amazon Fullfilled","Amazon Selling price","Amazon Total Discount","Paytm Title","Paytm Selling Price","Paytm Total Discount","SD Title","SD Gold","SD Selling Price","SD discount","Amazon SP","Flipkart SP","Snapdeal SP","Paytm SP","Amazon Availability","Flipkart Availability","Snapdeal Availability","Paytm Availability"]
	data=dict()
	i=0
	for index,row in df.iterrows():
		data[index]=dict()
		if type(row.amazon_url) != float:
			request = requests.get(row.amazon_url)
			if request.status_code == 200:
				h=get_price_amazon(driver,row.amazon_url,data,index)
				data[index]['Amazon Selling Price']=h['price'].strip()
				data[index]['Amazon Availability']=h['Avail'].strip()
		if type(row.flipkart_url) != float:
			request = requests.get(row.flipkart_url)
			if request.status_code == 200:
				p = get_price_flipkart(driver,row.flipkart_url,data,index)
				data[index]['Flipkart Selling Price']=p['price'].strip()
				data[index]['Flipkart Availability']=p['Avail'].strip()
		file_write(data,header)
		"""with open('scrapped_am_flip.txt','w') as f:
			f.write(json.dumps(data))
		data_frame = pd.DataFrame.from_dict(data,orient='index').reset_index()
    	data_frame.to_csv(New22.csv,columns=header) """

if __name__ == "__main__":
	main()
