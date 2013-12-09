from bs4 import BeautifulSoup
import urllib2
import urllib
import re
import os
import urlparse
import sys
import json
import urlparse
from Queue import Queue
import re
import json
visited_set = set()
discovered_set = set() #url that is in the container or visited
def test():
	url= "http://www.mrporter.com/product/397991"
	try:
		htmlData = urllib2.urlopen(url).read()
	except:
		exit(-1)
	soup = BeautifulSoup(htmlData)
	parse_product_info(url,soup)
	exit(0)
def main():

	url = sys.argv[1]
	
	site_hostname = urlparse.urlparse(url).hostname
	
	container = Queue()
	container.put(url)
	while(not container.empty()):
		url = container.get()
		visited_set.add(url)
		print url
		try:
			htmlData = urllib2.urlopen(url).read()
		except:
			continue
		soup = BeautifulSoup(htmlData)
		links = soup.find_all('a')
		for link in links:
			if link.has_key('href'):
				link_url = urlparse.urljoin(url, link['href'])
				
				if link_url not in visited_set and link_url not in discovered_set and samehost(link_url, site_hostname):
						
					discovered_set.add(link_url)
					container.put(link_url)
		
		parse_product_info(url,soup)
	
def samehost(url, site_hostname):
	
	return (site_hostname==urlparse.urlparse(url).hostname)

def parse_analyticsPageData(product_data,analyticsPageData):
	pattern_template = "%s: \"(.*)\""
	keys = ["department","pageClass","title","category"]
	for key in keys:
		pattern = pattern_template % key
		
		match = re.search(pattern,analyticsPageData)
		if match != None:
			product_data[key] = match.group(1)
	print product_data
def parse_product_info(url,soup):
	
	product_url_pattern = "http://www.\\mrporter.\\com/product/([0-9]*)"
	match = re.match(product_url_pattern, url)
	if match == None:
		return None

	
	product_data = dict()
	product_data["product_code"] = match.group(1)
	analyticsPageData = soup.find("script").text
	parse_analyticsPageData(product_data, analyticsPageData)
	product_detail = soup.find(id="product-details")
	
	product_data["product_name"] = product_detail.h4.string
	product_data["price_value"] = product_detail.find("span",{"class":"price-value"}).string.strip()


	product_info = soup.find(id="product-more-info")
	product_contents = product_info.find_all("div",{"class":"productContentPiece"})
	product_data['editor_notes'] = product_contents[0].text.strip()
	
	product_data["detail_care"] = ""
	detail_care_list= product_contents[2].find_all("li")
	for list_item in detail_care_list:
		product_data["detail_care"] += list_item.text+"\n"
	product_data["pair_item"] = [product_data["product_code"]]
	
	pair_product_links = product_contents[0].find_all("a",{"class":"product-item"})
	for pair_product_link in pair_product_links:
		pair_proudct_code = pair_product_link['href'].split('/')[-1]
		product_data["pair_item"].append(pair_proudct_code)
	product_data["pair_item"].sort()


	product_carousel = soup.find(id="product-carousel")
	list_item = product_carousel.find_all("li")
	product_img_url = get_xxl_img_url(list_item[0].img['src'])
	product_data["product_img_url"] = urlparse.urljoin(url, product_img_url)
	pairing_img_url = list_item[len(list_item)-1].img['src']
	product_data["pairing_img_url"] = urlparse.urljoin(url, pairing_img_url)


	color_div = soup.find(id="colour-text")
	if color_div!=None:
		product_data["color"] = color_div.span.text
	product_data["clothing_category"] = soup.find(id="product-links-list").find_all("a")[1].string.strip()
	os.system("wget %s -O images/%s.jpg"%(product_data["product_img_url"],product_data["product_code"]))
	file = open("metadata/"+product_data["product_code"]+".txt","w")
	file.write(json.dumps(product_data))
	file.close()

def get_xxl_img_url(imgurl):
	pattern = "(.*)_(.*)\.jpg"
	match  = re.match(pattern, imgurl)
	if match == None:
		return None
	return match.group(1)+"_xxl.jpg"

main()
#http://cache.mrporter.com/images/products/395797/395797_mrp_bk_xxl.jpg
#http://cache.mrporter.com/images/products/395797/395797_mrp_bk_xl.jpg
#http://cache.mrporter.com/images/products/395797/395797_mrp_bk_xs.jpg
#http://cache.mrporter.com/images/products/395797/395797_mrp_bk_s.jpg