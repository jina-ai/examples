""" This example builds on the Minimum Working Example which is available as 
part of the Jina 0.5.5-devel documentation. It introduces a dataset comprising 
articles obtained from the open-access journal International Journal of 
Nanomaterials (IJN), hosted by Hindawi.

Aim: 		Encode articles to a Jina Flow after acquisition.

Approach: 	Obtain a list of hypertext references to articles formatted in
		XML from the Hindawi site and encode bytes to a Flow.

"""

from utilities import html_crawler, xml_crawler

href_list = []

search_root_page = 'https://www.hindawi.com/search/all/nanoparticle/?journal=Journal+of+Nanomaterials'
# Focus search results by stating max_search_pages.
# For example, 2 pages = 20 items i.e. 10 items/page.
max_search_pages = 2
href_returned = html_crawler(search_root_page, max_search_pages)
href_list.extend(href_returned)
print("NO. OF SEARCH ITEMS RETRIEVED: ", len(href_list))

def input_fn():

  """ Input function to serve encoder with the full text of each article. """
  
  for _ in xml_crawler(href_list):
    yield b's'
