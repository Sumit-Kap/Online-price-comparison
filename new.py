#hy, os path set when running code on server
#import os
#os.environ["PATH"] += os.pathsep + '/root'
from random import randint
import time
import pandas as pd
import json
import requests
import sys
import logging

from pyvirtualdisplay import Display
from imp import reload
#from easyprocess import EasyProcess
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException

import re


delay = 3

# function to write to file
def file_write(data,header):
	data_frame = pd.DataFrame.from_dict(data, orient='index').reset_index()
	data_frame.to_csv('output.csv',columns=header,index=False)
	return True



# function to get the amazon search url
def get_price_amazon(driver,search,data,index):
	f=dict()
	f['ship_price']=''
	f['price']=''
	f['Avail']=''
	f['name']=''
	try:
		driver.get(search)
		driver.implicitly_wait(8)
		price=0
		try:
			try:
				if driver.find_element_by_id('title_feature_div'):
					name=driver.find_element_by_id('title_feature_div').text
			except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
				f['ship_price']='NA'
				f['price']='NA'
				f['Avail']='NA'
				f['name']='NA'
				return f
			try:
				if driver.find_element_by_css_selector('.a-color-price'):
					price=driver.find_element_by_css_selector('.a-color-price')
			except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
				pass
			try:
				if driver.find_element_by_id('priceblock_saleprice'):
					price=driver.find_element_by_id('priceblock_saleprice')
			except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
				try:
					if driver.find_element_by_id('priceblock_ourprice'):
						price=driver.find_element_by_id('priceblock_ourprice')
				except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
					pass
			tp=price.text
			if tp == 'Currently unavailable.':
				f['ship_price'] = 'NA'
				f['price'] = 'NA'
				f['name'] = name
				f['Avail']= 'N'
				return f
			dp=tp.replace(',','')
			f['price']=dp
			try:
				if driver.find_element_by_id('price-shipping-message'):
					sp=driver.find_element_by_id('price-shipping-message').text
					newship=sp.replace('.Details','')
			except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException) as e:
				try:
					if driver.find_element_by_id('ourprice_shippingmessage'):
						sp = driver.find_element_by_id('ourprice_shippingmessage').text
						ph=sp.replace('+','')
						newship=ph.replace('Delivery charge Details','')
						newship=newship.strip()
				except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException) as e:
					pass
			f['ship_price'] = newship
			f['price']=dp
			f['Avail']='Y'
			f['name']=name
			return f
		except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
			if f['price'] == '':
				f['price'] = 'NA'
				f['Avail']='N'
				f['ship_price']='NA'
				f['name']=name
				return f
			else:
				f['Avail']='Y'
				f['ship_price']='NA'
				f['name']=name
				return f
			pass
	except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
		#print 'went into exception'
		if f['price'] == '':
			f['price'] = 'NA'
			f['Avail']='N'
			f['ship_price']='NA'
			f['name']=name
			return f
		else:
			f['Avail']='Y'
			f['ship_price']='NA'
			f['name']=name
			return f
		#return "Error"


# function to get the flipkart search url
def get_price_flipkart(driver,search,data,index):
	d=dict()
	d['price']=''
	d['Avail']=''
	d['ship_price']=''
	d['name']=''
	try:
		driver.get(search)
		tp=0
		try:
			try:
				if driver.find_element_by_class_name('_3eAQiD'):
					name=driver.find_element_by_class_name('_3eAQiD').text
			except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
				d['price']='NA'
				d['Avail']='NA'
				d['ship_price']='NA'
				d['name']='NA'
				return d
			inputElement = driver.find_element_by_class_name("_1vC4OE")
			price = inputElement.text
			tp=price[1:]
			tp=tp.replace(',','')
			if driver.find_element_by_css_selector('._3xgqrA'):
				x='N'
				d['price'] = tp
				d['Avail'] = x
				d['ship_price'] = 'NA'
				d['name'] = name
				return d
		except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
			x='Y'
			pass
		ship_price = driver.find_element_by_class_name('_3X4tVa')
		ship_price.send_keys('110005')
		driver.find_element_by_class_name('_2aK_gu').click()
		time.sleep(7)
		sp=driver.find_element_by_class_name('_3EaKlN').text
		sp=sp.replace('?','')
		#print "shipping price",fh
		#print name
		d['price']=tp
		d['Avail']=x
		d['ship_price']=sp
		d['name']=name
		return d
	except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
		d['price']=tp
		d['Avail']=x
		d['ship_price']='NA'
		d['name']=name
		return d
		pass	

# function to get the snapdeal search url
def get_price_snapdeal(driver,search):
	m=dict()
	m['name']=''
	m['price']=''
	m['avail']=''
	m['ship_price']=''
	try:
		driver.get(search)
		try:
			if driver.find_element_by_css_selector('.pdp-e-i-head'):
				name = driver.find_element_by_css_selector('.pdp-e-i-head').text
		except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
			m['name']='NA'
			m['price']='NA'
			m['avail']='NA'
			m['ship_price']='NA'
			return m
		price = driver.find_element_by_css_selector('.payBlkBig').text
		nprice=price.replace(',','')
		try:
			if driver.find_element_by_css_selector('.sold-out-err'):
				avail='N'
				m['name']=name
				m['price']=nprice
				m['avail']=avail
				return m
		except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
			avail='Y'
			pass
		time.sleep(4)
		try:
			if driver.find_element_by_id('pincode-check'):
				pincode=driver.find_element_by_id('pincode-check')
				pincode.send_keys('110005')
				time.sleep(5)
				driver.find_element_by_id('pincode-check-bttn').click()
				time.sleep(5)
				try:
					sp=driver.find_element_by_css_selector('.availCharges').text
				except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
					pass
				try:
					sp=driver.find_element_by_css_selector('.avail-free').text
				except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
					pass
				#print 'shipping',sp
			m['name']=name
			m['price']=nprice
			m['avail']=avail
			m['ship_price'] = sp
			return m
		except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
			m['name']=name
			m['price']=nprice
			m['avail']=avail
			m['ship_price']='NA'
			return m
			pass
		time.sleep(5)
		#print sp
	except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
		#print sp
		m['name']=name
		m['price']=nprice
		m['avail']=avail
		m['ship_price']='NA'
		return m
		pass
		#return "Error"

		
# function to get the paytm search url
def get_price_paytm(driver,search):
	q=dict()
	q['name']=''
	q['price']=''
	q['avail']=''
	q['ship']=''
	try:
		driver.get(search)
		paytm = 'Error'
		try:
			if driver.find_element_by_css_selector('.NZJI'):
				name=driver.find_element_by_css_selector('.NZJI').text
		except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
			q['name']='NA'
			q['price']='NA'
			q['avail']='NA'
			q['ship']='NA'
			return q
		price = driver.find_element_by_css_selector('._1y_y').text
		tprice = price[8:]
		tprice=tprice.replace(',','')
		avail='Y'
		time.sleep(6)
		if driver.find_element_by_css_selector('.pyBu'):
			avail='N'
			q['name']=name
			q['price']=tprice
			q['avail']=avail
			q['ship']='NA'
			return q
			#print avail
	except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
		avail='Y'
		pass
	time.sleep(5)
	try:
		"""if driver.find_element_by_css_selector('._2P1M'):
			print 'hello'
			ship=driver.find_element_by_css_selector('._2P1M')
			ship.send_keys('110005')
			print 'hello'
			ship_button=driver.find_element_by_css_selector('.WU4d').click()
			print 'hello' """
		time.sleep(6)
		try:
			if driver.find_element_by_css_selector('._2sEn'):
				ship_price = driver.find_element_by_css_selector('._2sEn').text
				q['name']=name
				q['price']=tprice
				q['avail']=avail
				q['ship']=ship_price
				return q
		except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
			q['name']=name
			q['price']=tprice
			q['avail']=avail
			q['ship']=ship_price
			return q
		except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
			q['name']=name
			q['price']=tprice
			q['avail']=avail
			q['ship']=sp
			return q
	except (NoSuchElementException,StaleElementReferenceException,ElementNotVisibleException,TimeoutException,ElementNotSelectableException) as e:
		q['name']=name
		q['price']=tprice
		q['avail']=avail
		q['ship']='NA'
		return q
		pass


def main():
	# get name of product
	df = pd.read_csv('input.csv')
	header=["Shopclues_PID","FlipKart Title","FlipKart Assured","FlipKart Selling Price","FlipKart Total Discount","Amazon Title","Amazon Fullfilled","Amazon Selling price","Amazon Total Discount","Paytm Title","Paytm Selling Price","Paytm Total Discount","SD Title","SD Gold","SD Selling Price","SD discount","Amazon SP","Flipkart SP","Snapdeal SP","Paytm SP","Amazon Availability","Flipkart Availability","Snapdeal Availability","Paytm Availability"]
	data=dict()
	i=0
	
	for index,row in df.iterrows():
		try:
			display = Display(visible=0, size=(800, 800))
			display.start()
			chrome_options = webdriver.ChromeOptions()
			chrome_options.add_argument('--no-sandbox')
			driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver",chrome_options=chrome_options)
			data[index]=dict()
			data[index]['Shopclues_PID']=row.PID
			Amazon=row.Amazon
			Am_url=Amazon.strip()
			Flipkart=row.Flipkart
			Flip_url=Flipkart.strip()
			Snapdeal=row.Snapdeal
			Snap_url=Snapdeal.strip()
			Paytm=row.Paytm
			Paytm_url=Paytm.strip()
			if Am_url != 'N/A':
				#print(row.Amazon)
				h=get_price_amazon(driver,row.Amazon,data,index)
				print(h)
				data[index]['Amazon Selling price']=h['price']
				data[index]['Amazon Availability']=h['Avail']
				data[index]['Amazon SP']=h['ship_price']
				data[index]['Amazon Title']=h['name']
			else:
				data[index]['Amazon Selling Price']='NA'
				data[index]['Amazon Availability']='NA'
				data[index]['Amazon SP']='NA'
				data[index]['Amazon Title']='NA'
			if Flip_url != 'N/A':
				#print(row.Flipkart)
				p = get_price_flipkart(driver,row.Flipkart,data,index)
				print(p)
				data[index]['FlipKart Selling Price']=p['price']
				data[index]['Flipkart Availability']=p['Avail']
				data[index]['FlipKart Title']=p['name']
				data[index]['Flipkart SP']=p['ship_price']
			else:
				data[index]['Flipkart Selling Price']='NA'
				data[index]['Flipkart Availability']='NA'
				data[index]['Flipkart Title']='NA'
				data[index]['Flipkart SP']='NA'
			if Snap_url != 'N/A':
				#print row.Snapdeal
				g = get_price_snapdeal(driver,row.Snapdeal)
				print(g)
				#print g
				data[index]['SD Title']=g['name']
				data[index]['SD Selling Price']=g['price']
				data[index]['Snapdeal Availability']=g['avail'] 
				data[index]['Snapdeal SP']=g['ship_price']
			else:
				data[index]['SD Title']='NA'
				data[index]['SD Selling Price']='NA'
				data[index]['Snapdeal Availability']='NA'
				data[index]['Snapdeal SP']='NA'   
			if Paytm_url != 'N/A':
				#print row.Paytm
				r=get_price_paytm(driver,row.Paytm)
				data[index]['Paytm Selling Price'] = r['price']
				data[index]['Paytm Availability'] = r['avail']
				data[index]['Paytm Title'] = r['name']
				data[index]['Paytm SP'] = r['ship'] 
			else:
				data[index]['Paytm Selling Price'] = 'NA'
				data[index]['Paytm Availability'] = 'NA'
				data[index]['Paytm Title'] = 'NA'
				data[index]['Paytm Title']='NA'
			file_write(data,header)
			driver.close()
			driver.quit()
			#driver.Dispose()
			display.stop()
		except Exception as e:
			logging.exception("message")

if __name__ == "__main__":
	main()


