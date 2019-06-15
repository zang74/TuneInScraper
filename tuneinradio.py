#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# A simple script to scrape radio streams from tunein.com into an m3u8 file. 
# Note: this only scrapes direct links, any stations that are directed to players other than tunein's will be listed as failed.

# Imports

import time
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Main Function

def main():
	
	
	
	# Find your location of choice from https://tunein.com/radio/regions/
	tuneinurl = 'https://tunein.com/radio/local/'
	
	# Where you're gonna save the final m3u8file
	saveloc = '~/'
  # The final M3U8 file name
	tuneinradiom3u = saveloc + 'tuneinradio.m3u8'

	options = Options()
	options.headless = True
	options.binary_location	= "/usr/bin/chrome" ## use "/usr/bin/chromium" on systems without official chrome
	chromedriverpath = "/usr/bin/chromedriver" ## must be installed first ('sudo apt install chromedriver', etc...)
	
	# Setup webdriver
	driver = webdriver.Chrome(executable_path=chromedriverpath, chrome_options=options)
	driver.set_window_size(1400,8000)
	driver.implicitly_wait(5)
	driver.get(tuneinurl)

	
	# Pause a few seconds to let images URLs populate
	time.sleep(5)
	html = driver.page_source

	# Manage the soup beautifully
	soup = BeautifulSoup(html, "html.parser")
	li = soup.find_all("div", class_="guide-item__guideItemContainer___1-ViC")
	
	
  # Create playlist file	
  m3ufile = open(tuneinradiom3u, 'w+')
	m3ufile.write("#EXTM3U\n\n# ======================\n# TuneIn Radio Playlist\n# ======================\n\n")

	# Create a list for failed streams	
	failurelist = list()

	for link in li:
		testtitle = link.get('data-nexttitle')
		thisnumber = link.get('data-nextguideitem')
		
		titlefind = re.search(r'\<img.+?alt\=\"(.+?)\"',str(link))
		thisimage = re.search(r'\<img.+?src=\"(.+?)\"',str(link))

		if titlefind:
			title = titlefind.group(1)

		else:
			title = testtitle
		if thisimage:
			thisimage = thisimage.group(1)


		headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
					  'AppleWebKit/537.11 (KHTML, like Gecko) '
					  'Chrome/23.0.1271.64 Safari/537.11',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		'Accept-Encoding': 'none',
		'Accept-Language': 'en-US,en;q=0.8',
		'Connection': 'keep-alive',
		'Referrer': tuneinurl}
		thisurl = "http://opml.radiotime.com/Tune.ashx?id=" + thisnumber
		response = requests.get(thisurl, headers=headers)


		# get http response 
		thaturl = str(response.text)
		thaturl.strip()

		# take first URL if multiple are returned 
		url = thaturl.splitlines() 
		finalurl = url[0]

		if "STATUS: 400" in thaturl:
			# it failed, that sucks. Tell user about it
			failurelist.append(title)
		else:
			provider = re.sub('\s+','',testtitle).upper()
			m3ulink = "#EXTINF:-1 tvg-logo=\"" + thisimage +  "\" tvg-id=\"" + title + "\" group-title=\"MyRadio\" radio=\"true\"," + title + "\npipe:///usr/bin/ffmpeg -loglevel fatal -i " + finalurl + " -vn -acodec libmp3lame -metadata service_provider=" + provider + " -metadata service_name=" + provider + " -f mpegts -mpegts_service_type digital_radio pipe:1\n\n"
			m3ufile.write(m3ulink)
			print("Found " + title + ", adding it to playlist!")


	# Close the m3u8 file
	m3ufile.close()
	driver.close()

	# List streams that didn't work
	failurelistjoined = "\n\t".join(failurelist)
	print("\n------------------------------------\n\nFailed URLs/streams: \n\t" + failurelistjoined)


if __name__ == "__main__":
	main()
