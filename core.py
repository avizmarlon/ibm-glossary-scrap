import requests
import urllib
import os
import tkinter
from lxml import etree
from tkinter.filedialog import askdirectory, askopenfilename

# changes CLI encoding to utf-8
# os.system("chcp 65001")

URL = "http://www-01.ibm.com/software/globalization/terminology/"
letter_set = list('abcdefghijklmnopqrstuvwxz')
letter_set.append('glossary_')

# we iterate through each letter, because the link to each letter category
# in the glossary page is the base URL + the letter, eg.:
# /terminology/a.html
# /terminology/b.html
# /terminology/c.html
# /terminology/d.html
# and so on...
glossary = {}

for letter in letter_set:
	text_data = []
	letter_category_URL = URL + letter + ".html"
	while True:
		print("[*] Connecting to %s" % (letter_category_URL))
		try:
			request = urllib.request.Request(letter_category_URL)
			data = urllib.request.urlopen(request)
			print("[*] Connected.\n")
			break
		except:
			print("[*] Failed. Trying again.\n")
			continue

	# lxml parsing and scraping
	print("[*] Parsing HTML data...")
	try:
		parser = etree.HTMLParser()
		tree = etree.parse(data, parser)
		print("[*] Success.\n")
	except:
		print("[*] Fail. Exiting...\n")
		exit()

	# "word" and "definition" scraping
	glossary_data = ['word', 'definition']
	print("[*] Creating xpath root structure...")
	try:
		# ibm designed the page node structure for letter "b" slightly different, so we make
		# a specific 
		if letter == "b":
			root = tree.xpath('//div[@id="ibm-content-main"]/div/div[1]')	
		else:
			root = tree.xpath('//div[@id="ibm-content-main"]/div/div[2]')
		print("[*] Success.\n")
	except:
		print("[*] Fail. Exiting...\n")
		exit()

	# only consider <p> and <ol> tags
	valid_tags = ['p', 'ol']
	for element in root[0].iter():
		if element.tag not in valid_tags:
			continue

		# we create these children nodes structure to check the
		# nested tags inside each <p> and <ol> tags
		# because the information we want are in tags that have specific subtags
		# eg.: the "word" is always in the <strong> tag that is nested in a <p> tag
		print("[*] Creating element children nodes structure for %s..." % (element))
		try:
			children_nodes_object = element.getchildren()
			children_nodes_names = list(children.tag for children in children_nodes_object)
			print("[*] Success.\n")
		except:
			print("[*] Fail. Exiting...\n")
			exit()

		if 'strong' in children_nodes_names:			
			# this gets the "word" from the <strong> tag
			word_index = children_nodes_names.index('strong')
			word_object = children_nodes_object[word_index]
			word_text = word_object.xpath(".//text()")
			word = ''.join(word_text)
			glossary_data[0] = word
			print("[*] Acquired glossary WORD data.")

			# this is used when the definition is in the <span> tag
			if 'span' in children_nodes_names:				
				# definition
				span_index = children_nodes_names.index('span')
				span_object =  children_nodes_object[span_index]
				span_text = span_object.xpath(".//text()")
				definition = ''.join(span_text)
				if len(definition) > 0:
					glossary_data[1] = definition
					print("[*] Acquired glossary DEFINITION data.")
					glossary[word] = definition
					print("[*] Created glossary entry.\n")

					# print("[***] Scraped Data [***]")
					# print("# %s" % (word))
					# print(definition)
					# print('\n')
			
		# this is used when the definition is in the <ol> tag that comes in
		# the iteration after a <p> tag
		# in this case the "word" was defined in the previous iteration
		elif element.tag == "ol":
			element_text = element.xpath('.//text()')
			element_text.pop(-1) # removes \n at the end of the text

			# this fixes bad formatting when the string comes with \n\t and/or \n
			if "\n\t" not in element_text:
				if element_text[0] != "\n":
					element_text.insert(0, '\n')
				c = 0
				i = 1
				for item in element_text:
					if item == "\n":
						element_text[c] = ("%d. " % (i)) if i == 1 else (" %d. " % (i))
						i += 1	
					c += 1	
			elif "\n\t" in element_text:
				c = 0
				i = 1
				for item in element_text:
					if item == "\n\t":
						element_text[c] = ("%d. " % (i)) if i == 1 else (" %d. " % (i))
						i += 1
					c += 1

			definition = ''.join(element_text)
			glossary_data[1] = definition
			print("[*] Acquired glossary DEFINITION data.")
			glossary[word] = definition
			print("[*] Created glossary entry.\n")

			# print("[***] Scraped Data [***]")
			# print("# %s" % (word))
			# print(definition)
			# print('\n')


# CREATE TXT FILE WITH SCRAPED DATA
tkinter_root = tkinter.Tk().withdraw() # hides tkinter main window
filename = input("Give the glossary txt file a name (same rules as your OS's).\n/>")
if not filename.endswith(".txt"):
	filename += ".txt"
directory = askdirectory(title="Choose the folder to save the new file") +"/"

# print("[***] Scraped Data [***]")
for word, definition in sorted(glossary.items()):
	fhandle = open(directory+filename, 'a', encoding="utf-8")
	fhandle.write(word + "\t" + definition + "\n\n")
	# print("# %s" % (word))
	# print(definition)
	# print('\n')
fhandle.close()
