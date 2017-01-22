#!/bin/python
import re
import sys 
import json
import time
import signal
import requests
import argparse
from pprint import pprint
from bs4 import BeautifulSoup
from selenium import webdriver

#Terminal colors
W = '\033[37m'  # gray
R = '\033[31m'  # red
G = '\033[32m'  # green
B = '\033[34m'  # blue
P = '\033[35m'  # purple
C = '\033[36m'  # cyan
T = '\033[93m'  # tan

#Set soup for parsing HTML response
def set_soup(html):
	return BeautifulSoup(html,"html.parser" )

#Load Json
def get_blns():
        with open('blns.json') as data_file:
                data = json.load(data_file)
	return data

#Load json
def get_b64blns():
        with open('blns.base64.json') as b64_file:
                b64 = json.load(b64_file)
	return b64

#Parse out those args because running this all at once may not be desired
def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-b", "--blns", help="Check URLS against the BLNS\n", action="store_true")
	parser.add_argument("-c", "--check", help="Check URLS against the Base64 BLNS\n", action="store_true")
	parser.add_argument("-bf", "--badfof", help="Check URLs for 404 Text Injection\n", action = "store_true")
	parser.add_argument("-u", "--url", type=str, help="URL we want to fuzz\n")
	return parser.parse_args()

#Run various naughty strings against the URL and look for anomalous behavior
def blns(driver, og_url, data):
	print W + '[-]' + B + 'Checking BLNS against URL, this can take a while\n'
	for i in range(0, len(data)):
		new_url = og_url + data[i]
		print W + '[*]' + P + 'Checking :' + new_url
		driver.get(new_url)
		time.sleep(3)

#Run various B64 strings against the URL and look for anomalous behavior
def b64_blns(driver, og_url, b64):
	print W + '[-]' + B + 'Checking BLNS B64 against URL, this can take a while\n'
	for i in range(0, len(b64)):
		new_url = og_url + b64[i]
		print W + '[*]' + B + 'Checking :' + new_url
		driver.get(new_url)
		time.sleep(3)

#Checks if the 404 page is vulnerable to text injection
def check_bnf(driver, og_url):
	print W + '[-]' + B + 'Checking for 404 page vulnerable to text injection \n'
	bnf = '/test/%2f../It%20has%20been%20changed%20by%20a%20new%20one%20https://www.Attacker.com%20so%20go%20to%20the%20new%20one%20since%20this%20one'
	new_url = og_url + bnf
	print W + '[*]' + T + 'Checking :' + new_url
	
	
	response = requests.get(new_url)
	html = str(response.text)
	soup = set_soup(html)
	
	if soup(text=re.compile('Attacker.com')):
		print W + '[*]' + R + 'Positive result, displaying vulnerable page \n'
		time.sleep(3)
		driver.get(new_url)
		time.sleep(10)
	else:
		print W + '[*]' + C + 'Not vulnerable \n'
		time.sleep(10)
	
	return driver

def signal_handler(signal, frame ):
	print W + '[-]' + B + 'Stopping webdriver \n'
	driver.close()
	exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main(args):
			
	if len(sys.argv) <  2:
		print W + '[-]' + R + 'Please provide args. -h for help. \n'
		exit(0)

	og_url = args.url

	print og_url
	driver = webdriver.Firefox()

	#Prevents malformed URL error in selenium
	if og_url[:4] != 'http':
		og_url = 'http://'+ og_url

	def signal_handler(signal, frame):
		print W + '[-]' + B + 'Stopping webdriver\n'
		driver.close()
		exit(0)
        signal.signal(signal.SIGINT, signal_handler)
	
	data = get_blns()
	b64 = get_b64blns()
	
	if args.badfof:
		check_bnf(driver, og_url)
	if args.blns:
		blns(driver, og_url, data)
	if args.check:
		b64_blns(driver, og_url, b64)
	
	driver.quit()
	
if __name__ == '__main__':
	args = parse_args()
	main(args)	
