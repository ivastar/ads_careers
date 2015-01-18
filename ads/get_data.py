import urllib
import json
import yaml
import glob
import numpy as np
import astropy
import astropy.io.ascii

def pull_data(year=2003):
	
	"""
	Querries ADS for PHD theses form a given year.
	Allows for <600 dissertations. 
	"""

	sets = [0,201,401,601]
	for set in sets:
		url = 'http://adslabs.org/adsabs/api/search/?q=bibstem:PhDT&filter=year:{0}&filter=database:astronomy&rows=200&start={1}&dev_key=qsFHHv4pR6VMULMq'.format(year,set)
		response = urllib.urlopen(url)
		data = response.read()
		data_meta =  yaml.load(data)['meta']
		if data_meta['count']:
			print 'Writing ads_{0}_{1}.dat'.format(year,set)
			out_file = open('/Users/selene/Documents/Career_study/ads_careers/data/ads_{0}_{1}.dat'.format(year,set),'w')
			out_file.write(data)
			out_file.close()		
		
def get_data():
	
	years = np.arange(1990, 2011, 1)
	for year in years:
		pull_data(year=year)
		
	#pull_data(year=2003)	
	#pull_data(year=2004)	
	#pull_data(year=2005)	
	#os.system('rm ads_2003_401.dat')

def unique_institutions():

	files = glob.glob('/Users/selene/Documents/Career_study/ads_careers/data/ads_[12]*.dat')
	
	full_affils = np.empty(1, dtype=object)
	
	for file in files:
		print file
		data = open(file,'r')
		data_j = yaml.load(data.readline())
		affils = np.empty(len(data_j["results"]["docs"]), dtype=object)
		for i in range(len(data_j["results"]["docs"])):
			if data_j["results"]["docs"][i]["aff"] != ['-']:
				affils[i] =  json.dumps(data_j["results"]["docs"][i]["aff"])[2:-2]
		full_affils = np.concatenate((full_affils, affils), axis=0)
	unique = np.unique(full_affils)
	print "There are {} unique institutions.".format(len(unique))
	out_file = open('../data/unique_institutions.dat','w')
	for uni in unique:
		out_file.write("{}\n".format(uni))
	out_file.close
	
def read_usa_institutions():
		
	us_institutions =[]
	
	us_institutions = np.array([line.strip() for line in open('/Users/selene/Documents/Career_study/ads_careers/data/unique_institutions_usa.dat')], dtype=object)
	
	return us_institutions

def parse_output(year=2002):
			
	files = glob.glob('../data/ads_{}*.dat'.format(year))

	out_file = open('../ads_graduates_{}.dat'.format(year),'w')
	names_file = open('../ads_names.dat'.format(year),'a')
	
	us_institutions = read_usa_institutions()
	
	jj = 0

	for file in files:
		print file
		data = open(file,'r')
		data_j = yaml.load(data.readline())
		for i in range(len(data_j["results"]["docs"])):
			if json.dumps(data_j["results"]["docs"][i]["aff"])[2:-2] in us_institutions:
				names_file.write("{}\n".format(data_j["results"]["docs"][i]["author"][0].split()[1].encode('ascii','replace'))) #, data_j["results"]["docs"][i]["aff"][0], data_j["results"]["docs"][i]["title"]
				out_file.write("{}. {}\n{}\n{}\n".format(jj+1, data_j["results"]["docs"][i]["author"][0].encode('ascii','replace'), data_j["results"]["docs"][i]["aff"][0], data_j["results"]["docs"][i]["title"]))
				jj+=1
				if 'keyword' in data_j["results"]["docs"][i].keys():
					out_file.write("{}\n\n".format(data_j["results"]["docs"][i]["keyword"]))
				else:
					out_file.write("\n")
				#print jj, ';', data_j["results"]["docs"][i]["author"][0], ';', data_j["results"]["docs"][i]["title"]
	
	out_file.close()
	names_file.close()
	print "Output file is {}".format(out_file.name)		

def get_missing_affil(bibcode=''):

	"""
	For a given bibcode, return publication institution
	"""

	import requests, bs4

	affil = ''
	response = requests.get('http://adsabs.harvard.edu/abs/{}'.format(bibcode))
	soup = bs4.BeautifulSoup(response.text)
	for line in soup.find_all('meta'):
		if (line.has_key('name') and line['name'].startswith('dc.source')):
			affil = line['content']

	if affil:
		if affil.lower().replace('.','').startswith('phd thesis,'):
			try:
				return affil.split('esis,')[1].strip()
			except:
				return affil
		else:
			return affil
	else:
		return 'None'


def check_missing_affil(year=2002):

	"""
	Go through the PhD entries for a given year.
	Find ones without affiliation.
	Grab the ADS HTML page for that bibcode.
	Get publication institution from there.
	"""

	files = glob.glob('/Users/selene/Documents/Career_study/ads_careers/data/ads_{}*.dat'.format(year))
	out_file = open('/Users/selene/Documents/Career_study/ads_careers/data/missing_affil.dat','a')

	for file in files:
		data = open(file,'r')
		data_j = yaml.load(data.readline())

		for i in range(len(data_j["results"]["docs"])):
			if data_j["results"]["docs"][i]["aff"] == ['-']:
				#print 'Checking {}.'.format(data_j["results"]["docs"][i]['bibcode'])
				affil = get_missing_affil(bibcode=data_j["results"]["docs"][i]['bibcode'])
				out_file.write(affil.encode("utf-8")+'\n')


def lookup_fa_pubs(year = 2002):
			
	files = glob.glob('../ads_{}*.dat'.format(year))

	out_file_au = open('../ads_fa_publications_{}_authors.dat'.format(year),'w')
	out_file = open('../ads_fa_publications_{}.dat'.format(year),'w')
	out_file.write('year n_pubs\n')
	
	us_institutions = read_usa_institutions()
	
	jj = 0

	for file in files:
		print file
		data = open(file,'r')
		data_j = yaml.load(data.readline())
		for i in range(len(data_j["results"]["docs"])):
			if json.dumps(data_j["results"]["docs"][i]["aff"])[2:-2] in us_institutions:
				author = data_j["results"]["docs"][i]["author"][0].replace(',','').split(' ')
				url = 'http://adslabs.org/adsabs/api/search/?q=first_author:%22{0},+{1}%22&filter=database:astronomy&filter=property:refereed&filter=year:[{2} TO 2014]&rows=200&sort=DATE+desc&dev_key=qsFHHv4pR6VMULMq'.format(author[0].encode('ascii','ignore'), author[1].encode('ascii','ignore'), year)
				response = urllib.urlopen(url)
				data_search =  yaml.load(response.read())

				if data_search["meta"]["count"] >= 1:
					first_author = data_search["results"]["docs"][0]["author"][0]#.replace(',','').split(' ')
					# printing: year of last fo pub, number of entries, first author, author
					out_file_au.write("{}\t{}\t{}\t{}\n".format(data_search["results"]["docs"][0]["year"], data_search["meta"]["count"], first_author.encode('ascii','ignore'), author))
					out_file.write("{}\t{}\n".format(data_search["results"]["docs"][0]["year"], data_search["meta"]["count"]))
					#print "{}\t{}\t{}\t{}\t".format(data_search["results"]["docs"][0]["year"], data_search["meta"]["count"], first_author.encode('ascii','ignore'), author)

def lookup_all_pubs(year = 2002):
			
	import fnmatch

	files = glob.glob('ads_{}*.dat'.format(year))

	out_file = open('ads_last_publications_{}_authors.dat'.format(year),'w')
	out_file_help = open('ads_last_pub_help.dat','a')
	
	us_institutions = read_usa_institutions()
	gender_names = read_name_genders()
	
	jj = 0

	for file in files:
		print file
		data = open(file,'r')
		data_j = yaml.load(data.readline())
		for i in range(len(data_j["results"]["docs"])):
			gg = 0
			if json.dumps(data_j["results"]["docs"][i]["aff"])[2:-2] in us_institutions:
				author = data_j["results"]["docs"][i]["author"][0].replace(',','').split(' ')
				url = 'http://adslabs.org/adsabs/api/search/?q=author:%22{0},+{1}%22&filter=database:astronomy&filter=property:refereed&filter=year:[{2} TO 2015]&rows=1&sort=DATE+desc&dev_key=qsFHHv4pR6VMULMq'.format(author[0].encode('ascii','ignore'), author[1].encode('ascii','ignore'), year)
				response = urllib.urlopen(url)
				data_search =  yaml.load(response.read())

				url_first = 'http://adslabs.org/adsabs/api/search/?q=first_author:%22{0},+{1}%22&filter=database:astronomy&filter=property:refereed&filter=year:[{2} TO 2015]&rows=1&sort=DATE+desc&dev_key=qsFHHv4pR6VMULMq'.format(author[0].encode('ascii','ignore'), author[1].encode('ascii','ignore'), year)
				response_first = urllib.urlopen(url_first)
				data_search_first =  yaml.load(response_first.read())
				if data_search_first["meta"]["hits"] ==0:
					fa_year = year
				else:
					fa_year = data_search_first["results"]["docs"][0]['year'] 

				if author[1].encode('ascii','ignore') in gender_names.keys():
					gg =  gender_names[author[1].encode('ascii','ignore')]
				else:
					gg = 3

				if (data_search["meta"]["hits"] >= 1):
					authors = list(data_search["results"]["docs"][0]["author"])
					affils = list(data_search["results"]["docs"][0]["aff"])
					if fnmatch.filter(authors,'{}*'.format(author[0].encode('ascii','ignore'))):
						nn = authors.index(fnmatch.filter(authors,'{}*'.format(author[0].encode('ascii','ignore')))[0])
						out_file.write("{}|{}|{}|{}|{}|{}|{}|{}|{}\n".format(data_search["results"]["docs"][0]["year"], data_search["meta"]["hits"], nn, len(authors), fa_year, data_search_first["meta"]["hits"], author[0].encode('ascii','ignore'), author[1].encode('ascii','ignore'), affils[nn].encode('ascii','ignore')))
					else: 
						out_file_help.write('HELP: {} | {} | {}\n'.format(year, author, authors))
						jj+= 1
				else:
					out_file_help.write('HELP: {} | {}\n'.format(year, author))

	print "Total failures: {}".format(jj)

