"""
Scripts that querry ADS for the list of dissertations each year as well as scripts that parse the institutions.
"""

import urllib
import json
import yaml
import glob
import numpy as np
import astropy
import astropy.io.ascii
import os
import requests, bs4
#ADS_KEY = os.getenv('ADS_KEY')
ADS_TOKEN = os.getenv('ADS_TOKEN')

def pull_data(year=2003, out_dir='../data/', root='ads', database='astronomy'):
	
	"""
	Querries ADS for PHD theses form a given year.
	"""

	if not os.path.exists(out_dir):
		os.system('mkdir {}'.format(out_dir))

	r = requests.get('https://api.adsabs.harvard.edu/v1/search/query',
		params = {'q':'bibstem:"PhDT"',
		'fl':'bibcode,pubdate,database,aff,author,citation_count,pub,year,title,identifier,id',
		'sort':'pubdate desc',
		'rows':'10000',
		'fq':'year:{},database:"astronomy"'.format(year)},
		headers={'Authorization':'Bearer:{}'.format(ADS_TOKEN)}
		)

	if r.json()['response']['numFound'] == 0:
		print('No results found.')
		return 
	else:
		print('Writing {0}{1}_{2}.dat'.format(out_dir, root, year))
		out_file = open('{0}{1}_{2}.dat'.format(out_dir, root, year),'w')
		data = r.text
		out_file.write(data)
		out_file.close()		
		
def get_data(year_start=1970, year_end=2018):

	"""
	Gets data for all dissertations from 1970 to 2014
	"""

	years = np.arange(year_start, year_end+1, 1)
	for year in years:
		pull_data(year=year)
		

def unique_institutions(dir='../data/', out_file='unique_institutions.dat'):

	"""
	Takes all dissertation data in the ads_careers/data directories 
	and otputs a list of unique institutions to ../data/unique_institutions.dat
	The user can then parse by hand the US and non-US institutions.
	Since there is no uniform format for institution names, this is a bit of a mess and cannot be automated.
	I parsed out the US institutions by hand and saved them to ../data/unique_institutions_usa.dat
	"""

	files = glob.glob(dir+'ads_[12]*.dat')
	
	full_affils = np.empty(1, dtype=object)
	
	for file in files:
		print(file)
		data = open(file,'r')
		data_j = yaml.load(data.readline())
		affils = np.empty(len(data_j["response"]["docs"]), dtype=object)
		for i in range(len(data_j["response"]["docs"])):
			if data_j["response"]["docs"][i]["aff"] != ['-']:
				affils[i] =  json.dumps(data_j["response"]["docs"][i]["aff"])[2:-2]
		full_affils = np.concatenate((full_affils, affils), axis=0)

	# remove None
	index = full_affils != np.array(None)
	full_affils = full_affils[index]

	unique = np.unique(full_affils)
	print("There are {} unique institutions.".format(len(unique)))
	
	out_file = open(dir+out_file,'w')
	for uni in unique:
		out_file.write("{}\n".format(uni))
	out_file.close
	
def read_usa_institutions():

	"""	
	Reads in the list of US institutions and returns a numpy string array for further use.
	"""
		
	us_institutions =[]
	
	us_institutions = np.array([line.strip() for line in open('../data/unique_institutions_usa.dat')], dtype=object)
	
	return us_institutions


def read_top_10_usa_institutions():

	"""	
	Reads in the list of the top 10 US institutions and returns a numpy string array for further use.
	This is a subset of ../data/unique_institutions_usa.dat consisting of all the different possible
	names of the top 10 US institutions. 
	"""
		
	top_10_us_institutions =[]
	
	top_10_us_institutions = np.array([line.strip() for line in open('../data/top10_unique_institutions_usa.dat')], dtype=object)
	
	return top_10_us_institutions


def get_missing_affil(bibcode=''):

	"""
	For a given bibcode, return publication institution listed on the ADS HTML page.
	For some dissertations there is no institution in the querry result, but there 
	is one on the HTML page. This is especially a problem for 1996 for some reason.
	"""

	import requests, bs4

	affil = ''
	response = requests.get('http://adsabs.harvard.edu/abs/{}'.format(bibcode))
	soup = bs4.BeautifulSoup(response.text, features="lxml")
	for line in soup.find_all('meta'):
		if (line.has_attr('name') and line['name'].startswith('dc.source')):
			affil = line['content']

	if affil:
		return bibcode+' | '+affil
	else:
		return bibcode+' | None'


def check_missing_affils(files=[], out_file = 'missing_affil.dat', out_dir='../data/'):

	"""
	Go through the PhD entries, find ones without affiliation, grab the ADS HTML page for that bibcode, 
	get publication institution from there.
	Just does it for all the files in the data directory.
	"""

	import time

	if not files:
		files = glob.glob('../data/ads_*.dat')
	
	out_file = open(out_dir+out_file,'w')

	for file in files:
		data = open(file,'r')
		data_j = yaml.load(data.readline())

		for i in range(len(data_j["response"]["docs"])):
			if (data_j["response"]["docs"][i]["aff"] == ['-']) or (data_j["response"]["docs"][i]["aff"] == ['--']):
				#print 'Checking {}.'.format(data_j["response"]["docs"][i]['bibcode'])
				affil = get_missing_affil(bibcode=data_j["response"]["docs"][i]['bibcode'])
				time.sleep(1+np.random.uniform(size=1)[0])
				out_file.write('{}\n'.format(affil.encode("utf-8")))
				print(affil)

	out_file.close()

def read_missing_usa_bib(dir='../data/'):

	"""	
	Reads in the list of US institutions and returns a numpy string array for further use.
	"""
		
	us_bib =[]
	
	us_bib = np.array([line.split('|')[0].strip() for line in open(dir+'missing_affil_usa.dat')], dtype=object)
	
	return us_bib

def parse_output(year=2002, dir='../data/', verbose=True):

	"""
	One way to parse the results: outputs a list of first names and a formatted list of dissertations for ease of reading. 
	"""
			
	in_file = glob.glob(dir+'ads_{}.dat'.format(year))

	out_file = open(dir+'ads_{}_formatted.dat'.format(year),'w')
	parse_file = open(dir+'ads_{}_parse.dat'.format(year),'w')
	names_file = open(dir+'ads_first_names.dat'.format(year),'a')

	us_institutions = read_usa_institutions()
	
	jj = 0

	print(in_file)
	data = open(in_file[0],'r')
	data_j = yaml.load(data.readline())
	for i in range(len(data_j["response"]["docs"])):
		if (data_j["response"]["docs"][i]["aff"][0] in us_institutions):
			try:
				tmp_name = data_j["response"]["docs"][i]["author"][0].split(',')[1].split()
				if (tmp_name[0][-1] == '.') and (len(tmp_name) > 1):
					names_file.write("{}\n".format(tmp_name[1]))
				else:
					names_file.write("{}\n".format(tmp_name[0]))
			except:
				print(data_j["response"]["docs"][i]["author"][0])
				names_file.write("{}\n".format(data_j["response"]["docs"][i]["author"][0]))


			out_file.write("{}. {}\n{}\n{}\n{}\n\n".format(jj+1, data_j["response"]["docs"][i]["author"][0], data_j["response"]["docs"][i]["aff"][0], data_j["response"]["docs"][i]["title"],data_j["response"]["docs"][i]["bibcode"]))

			parse_file.write("{} | {} | {} | {} |\n".format(jj+1, data_j["response"]["docs"][i]["author"][0], data_j["response"]["docs"][i]["aff"][0], year))

			jj+=1

			if verbose:
				print(jj, ';', data_j["response"]["docs"][i]["author"][0])#, ';', data_j["results"]["docs"][i]["title"]
	
	out_file.close()
	parse_file.close()
	names_file.close()
	print("Output file is {}".format(out_file.name))


