from urllib.request import urlopen
from bs4 import BeautifulSoup
import progressbar
import re
#import os
#import csv
#import sys
import codecs


def souper(url, parser = 'html.parser'):

  """ Function retrieves content of each URL address an returns a BeautifulSoup
    object.

  """
  
  page_content = urlopen(url).read().decode('utf-8')
  soup_content = BeautifulSoup(page_content, parser)
  return soup_content


def html_crawler(srp, mpages = 0):

  """ This function goes through all the pages retrieved from a search of the
  Hindawi IJN ournal for articles about nanoparticles, constructs the links
  to each article's XML format and returns that list.
  
  srp: 		Root page of the search.
  max_pages: 	Default 5. Controls the numberof search items to consider.

  Note that Hindawi search results have maximum 10 items per page.

  """
  page = 1
  urls = []
  href_list = []
  urls.append(srp)
  
  # Firstly, get the total no. of items returned by search
  first_page = souper(urls[0])
  numba_of_sr = str(list(first_page.findAll('h1')).pop())
  int_sr = int(list(re.findall(r'\d{3,9}', numba_of_sr)).pop())
  if mpages > 0:
    # Limit focus to stated no. of search pages
    max_pages = mpages
  else:
    # Return all search pages!
    max_pages = int_sr//10
  
  while(page <= max_pages):
    the_page = souper(urls[0])
    found = the_page.findAll('a', {'href':re.compile('/journals/jnm/*')})

    for link in found:
      str_href = str(link.get('href')).rstrip('/')
      # Keep out PDF and .ris files
      if ".pdf" in str_href or ".ris" in str_href:
        pass
      else:
        # After filtering unwanted formats...
        href = "http://downloads.hindawi.com" + str_href + ".xml"
        href_list.append(href)
    page = page + 1
    next_page = srp.replace("?","page/{}/?".format(page))
    urls = []
    urls.append(next_page)

  # Take out duplicates and return list of XML links
  href_list = list(set(href_list))
  return href_list


def xml_crawler(xml_urls):
  """ Function extracts the content of each XML link (article) and returns a
  generator object.
  
  xml_urls:	List of XML links
  
  """
  bar = progressbar.ProgressBar()
  for url in bar(xml_urls):
      if ".xml" in url:
        try:
          soup = souper(url,'html5lib') # lxml
          yield str(soup)
        except:
          yield "EXCEPTION"
