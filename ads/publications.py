"""
Scripts to querry publication records.
"""

import os
import requests
import astropy
from astropy.io import ascii
import numpy as np
import time
import glob

ADS_TOKEN = os.getenv('ADS_TOKEN')

def querry_pubs(name='', phd_year=2030, key='first_author'):

	"""
	Queries ADS for this author's publications.

	key = 'first_author'
	
	or

	key = 'author'

	Returns:
	- a dictionary with number of peer reviewed publications per year.
	- number of publications pre-phd (including PhD year)
	- number of publications post-phd
	- year of last publication
	"""

	years = np.arange(phd_year-5,2019,1)

	numFound = 0
	attempts = 0

	if name == 'Detch, J. Lewis, Jr.':
		name = 'Detch, J.'
	if name == 'Massa, Jose Luiz Lunas De Mello':
		name = 'Massa, J.'
	if name == 'Abdel-Monem, M. S. E. D.':
		name = 'Abdel-Monem, M.'
	if name == 'Al-Shukri, Ali Mohammad S. A.':
		name = 'Al-Shukri, A.'
	if name == 'van Putten, Maurice H. P. M.':
		name = 'van Putten, M.'
	if name == 'Wijesundera, Hapu Arachchige R. V. W.':
		name = 'Wijesundera, H.'
	if name == 'Orta Ortiz de Zarate, Jose Alejandro':
		name = 'Orta Ortiz de Zarate, J.'
	if name == "Drouet D'Aubigny, Christian Yann Pierre":
		name = "Drouet D'Aubigny, C."
	if name == 'Guimaraes, Antonio Candido De Camargo, Jr.':
		name = 'Guimaraes, A.'
	if name == 'Vega, Michael Francis Ian G., II':
		name = 'Vega, Michael'
	if name == 'Morris, Clifford Dean, Jr.':
		name = 'Morris, Clifford D.'
	if name == 'Ward, George Haskell, Jr.':
		name = 'Ward, George H.'

	while numFound == 0:
		r = requests.get('https://api.adsabs.harvard.edu/v1/search/query',
			params = {'q':'author:("{}")'.format(name),
			'fl':'bibcode,author,year,id',
			'sort':'pubdate desc',
			'rows':'10000',
			'fq':'year:[{} TO 2018],database:"astronomy",property:refereed'.format(phd_year-5)},
			headers={'Authorization':'Bearer:{}'.format(ADS_TOKEN)}
			)
		attempts+=1
		if 'error' in r.json().keys():
			pubs_per_year = dict((year,0) for year in years)
			return pubs_per_year, 0, 0, phd_year, pubs_per_year, 0, 0, phd_year
		#print(r.json()['responseHeader'])
		numFound = r.json()['response']['numFound']	
		if attempts > 1:
			print('{}: attempt {}'.format(name, attempts))
			time.sleep(np.random.randint(0,high=5, size=1)[0])

	last_name = name.split(',')[0]
	fa = []
	for doc in r.json()['response']['docs']:
		if doc['author'][0].startswith(last_name):
			fa.append(doc)


	### STATS FOR ALL PAPERS
	### number of publications per year
	pubs_per_year = {}
	all_years = []
	for i in range(len(r.json()['response']['docs'])):
		all_years.append(int(r.json()['response']['docs'][i]['year']))
	pubs_per_year = dict((year,all_years.count(year)) for year in years)

	### publications pre PhD
	total_pre = 0
	for year in np.arange(phd_year-5, phd_year+1):
		total_pre += pubs_per_year[year]

	### publications post PhD
	total_post = 0
	for year in np.arange(phd_year+1, 2018):
		total_post += pubs_per_year[year]

	### year of last publication
	last_pub_year = int(r.json()['response']['docs'][0]['year'])

	### STATS FOR FIRST AUTHOR PAPERS
	fa_pubs_per_year = {}
	all_years = []
	for i in range(len(fa)):
		all_years.append(int(fa[i]['year']))
	fa_pubs_per_year = dict((year,all_years.count(year)) for year in years)

	### publications pre PhD
	fa_total_pre = 0
	for year in np.arange(phd_year-5, phd_year+1):
		fa_total_pre += fa_pubs_per_year[year]

	### publications post PhD
	fa_total_post = 0
	for year in np.arange(phd_year+1, 2018):
		fa_total_post += fa_pubs_per_year[year]

	### year of last publication
	fa_last_pub_year = int(fa[0]['year'])


	return pubs_per_year, total_pre, total_post, last_pub_year, fa_pubs_per_year, fa_total_pre, fa_total_post, fa_last_pub_year


def lookup_pubs(phd_year = 2000):

	import ads.gender
			
	file = '../data/ads_{}_parse.dat'.format(phd_year)
	#file = '../data/test.dat'
	in_file = ascii.read(file, delimiter='|', names=['n','name','university','yy','foo'])
	print(file)

	out_file = open('../data/ads_{}_pub_stats.dat'.format(phd_year),'w')
	fa_labels = ''
	all_labels = ''
	for year in np.arange(phd_year-5, 2017,1):
		fa_labels += ' fa_{} |'.format(year)
		all_labels += ' all_{} |'.format(year)

	out_file.write('n | name | university | phd_year | gender | fa_n_pubs_pre_phd | fa_n_pubs_prost_phd | fa_year_last | all_n_pubs_pre_phd | all_n_pubs_prost_phd | all_year_last | {} {} foo\n'.format(fa_labels, all_labels))
	
	gender_names = ads.gender.read_name_genders()

	for i in range(len(in_file)):

		if (i % 10) == 0:
			print(in_file[i]['n'], in_file[i]['name'], in_file[i]['university'])

		### get gender of author
		try:
			tmp_name = in_file[i]['name'].split(',')[1].split()
		except:
			tmp_name = in_file[i]['name']
		if (len(tmp_name[0]) == 2) and (tmp_name[0][-1] == '.') and (len(tmp_name) > 1) and (tmp_name[1][0] != '-'):
			f_name = tmp_name[1]
			f_name = f_name.replace('.','').replace('(','').replace(')','')
			if f_name.startswith('-'):
				f_name = f_name[1:]
			try:
				gender = gender_names[f_name]
			except:
				gender = None
		elif (len(tmp_name[0]) == 2) and (tmp_name[0][-1] == '.') and (len(tmp_name) == 1):
			gender = None
		else:
			f_name = tmp_name[0]
			f_name = f_name.replace('.','').replace('(','').replace(')','')
			if f_name.startswith('-'):
				f_name = name[1:]
			try:
				gender = gender_names[f_name]
			except:
				gender = None

		### get publications stats

		out_file.write("{} | {} | {} | {} | {} | ".format(in_file[i]['n'], in_file[i]['name'], in_file[i]['university'], in_file[i]['yy'], gender))

		all_pubs_per_year, all_total_pre, all_total_post, all_last_pub_year, fa_pubs_per_year, fa_total_pre, fa_total_post, fa_last_pub_year = querry_pubs(name=in_file[i]['name'], phd_year = phd_year, key='first_author')

		out_file.write("{} | {} | {} | ".format(fa_total_pre, fa_total_post, fa_last_pub_year))

		out_file.write("{} | {} | {} | ".format(all_total_pre, all_total_post, all_last_pub_year))

		for year in np.arange(phd_year-5, 2017,1):
			out_file.write('{} | '.format(fa_pubs_per_year[year]))

		for year in np.arange(phd_year-5, 2017,1):
			out_file.write(' {} |'.format(all_pubs_per_year[year]))

		out_file.write('\n')

	out_file.close()


def outliers(year_start=1970, year_end=2016, save_output=True, recent_activity_years=5):

	from astropy.table import Table

	stats_file_fa = open('publication_statistics_fa.dat','w')
	stats_file_fa.write('year n min max mean median std n_outliers f_n f_min f_max f_mean f_median f_std m_n m_min m_max m_mean m_median m_std\n')
	stats_file_all = open('publication_statistics_all.dat','w')
	stats_file_all.write('year n min max mean median std n_outliers f_n f_min f_max f_mean f_median f_std m_n m_min m_max m_mean m_median m_std\n')
	outliers_file = open('publication_outliers.dat','w')

	for year in np.arange(year_start, year_end,1):

		print('Calculating stats for {}'.format(year))

		data = ascii.read('../data/ads_{}_pub_stats.dat'.format(year))
		#years = np.arange(year-5, 2017,1)
		#fa_colnames = data.colnames[-2*len(years)-1:len(years)*-1-1]
		#all_colnames = data.colnames[len(years)*-1-1:-1]

		data = data[2017-data['fa_year_last'] <= recent_activity_years]

		#fa_table = Table(data.columns[-2*len(years)-1:len(years)*-1-1]).to_pandas()
		#all_table = Table(data.columns[len(years)*-1-1:-1]).to_pandas()
		#fa_all = fa_table.sum(axis=1)

		fa_all = np.array(data['fa_n_pubs_pre_phd']+data['fa_n_pubs_prost_phd'])
		fa_women = fa_all[data['gender'] == 'female']
		fa_men = fa_all[data['gender'] == 'male']

		max = fa_all.mean()+3*fa_all.std()
		fa_out = np.where(fa_all > max)

		all_all = np.array(data['all_n_pubs_pre_phd']+data['all_n_pubs_prost_phd'])
		all_women = all_all[data['gender'] == 'female']
		all_men = all_all[data['gender'] == 'male']

		max = all_all.mean()+3*all_all.std()
		all_out = np.where(all_all > max)



		stats_file_fa.write('{}\t{}\t{}\t{}\t{:5.2f}\t{}\t{:5.2f}\t{}\t'.format(year, len(fa_all), fa_all.min(), fa_all.max(), fa_all.mean(), np.median(fa_all), fa_all.std(),len(fa_out[0])))
		if len(fa_women) > 0:
			stats_file_fa.write('{}\t{}\t{}\t{:5.2f}\t{}\t{:5.2f}\t'.format(len(fa_women), fa_women.min(), fa_women.max(), fa_women.mean(), np.median(fa_women), fa_women.std()))
		else:
			stats_file_fa.write('{}\t{}\t{}\t{:5.2f}\t{}\t{}\t'.format(len(fa_women), np.nan, np.nan, np.nan, np.nan, np.nan))

		stats_file_fa.write('{}\t{}\t{}\t{:5.2f}\t{}\t{:5.2f}\n'.format(len(fa_men), fa_men.min(), fa_men.max(), fa_men.mean(), np.median(fa_men), fa_men.std()))

		stats_file_all.write('{}\t{}\t{}\t{}\t{:5.2f}\t{}\t{:5.2f}\t{}\t'.format(year, len(all_all), all_all.min(), all_all.max(), all_all.mean(), np.median(all_all), all_all.std(),len(all_out[0])))
		if len(fa_women) > 0:
			stats_file_all.write('{}\t{}\t{}\t{:5.2f}\t{}\t{:5.2f}\t'.format(len(all_women), all_women.min(), all_women.max(), all_women.mean(), np.median(all_women), all_women.std()))
		else:
			stats_file_all.write('{}\t{}\t{}\t{:5.2f}\t{}\t{}\t'.format(len(all_women), np.nan, np.nan, np.nan, np.nan, np.nan))

		stats_file_all.write('{}\t{}\t{}\t{:5.2f}\t{}\t{:5.2f}\n'.format(len(all_men), all_men.min(), all_men.max(), all_men.mean(), np.median(all_men), all_men.std()))

		for ii in fa_out[0]:
			outliers_file.write('{}\t{}\t{}\n'.format(year, np.array(data[ii]), np.array(fa_all[ii])))

	stats_file_fa.close()
	stats_file_all.close()
	outliers_file.close()


def hubble_fellows():

	"""
	The names of all Hubble fellow are in ../data/all_hubble_fellows.dat
	The names of Hubbme fellows since 2010 are in  ../data/2010_hubble_fellows.dat
	Read the latter and then pull the names of only those fellows from the *_pub_stats.dat files
	"""

	import subprocess

	in_file = '../data/2010_hubble_fellows.dat'
	data = ascii.read(in_file)

	files = glob.glob('../data/ads_*_pub_stats.dat')

	out_file = open('../data/hubble_pubs_stats.dat','w')
	out_file.write('n | name | university | phd_year | gender | fa_n_pubs_pre_phd | fa_n_pubs_prost_phd | fa_year_last | all_n_pubs_pre_phd | all_n_pubs_prost_phd | all_year_last | hubble_host | hubble_year | foo\n')

	for line in data:
		print(line['name'])
		found = 0
		for file in files:
			names = line['name'].split()
			get = '{}, {}'.format(names[-1], names[0])
			response = subprocess.call(['grep', get, file])
			if response != 1:
				found = 1
				this_file = ascii.read(file)
				for line1 in this_file:
					if line1['name'].startswith(get):
						out_file.write('{} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} | {} |\n'.format(line1['n'],line1['name'],line1['university'],line1['phd_year'],line1['gender'],line1['fa_n_pubs_pre_phd'],line1['fa_n_pubs_prost_phd'],line1['fa_year_last'],line1['all_n_pubs_pre_phd'],line1['all_n_pubs_prost_phd'],line1['all_year_last'],line['host_institution'],line['hubble_year']))

		if found == 0:
			out_file.write("{} | {} | {} |\n".format(line['name'],line['host_institution'],line['hubble_year']))


	out_file.close()

def top_ten(phd_year = 2010):

	"""
	Split our the publications from graduates of the top 10 PhD institutions.
	"""
	import get_data

	in_file = '../data/ads_{}_pub_stats.dat'.format(phd_year)
	data = ascii.read(in_file)

	out_file = open('../data/ads_{}_pub_stats_top10.dat'.format(phd_year),'w')

	top_10_usa_institutions = get_data.read_top_10_usa_institutions()

	header = ''
	for col in data.colnames[:-1]:
		header = header + ' {} | '.format(col)
	header = header + data.colnames[-1] + '\n'
	out_file.write(header)

	for line in data:
		if line['university'] in top_10_usa_institutions:
			for col in data.colnames[:-1]:
				out_file.write(' {} |'.format(line[col]))
			out_file.write('\n')

def last_institution(name='Smith, John', key='author', phd_year='2009', year_end='2019', n_max_pubs = 5):

	"""
	For a given name, return the country and institution of the last affiliation. 
	By default only check the last 5 publications. 
	"""

	import unidecode

	numFound = 0
	attempts = 0

	if name == 'Detch, J. Lewis, Jr.':
		name = 'Detch, J.'
	if name == 'Massa, Jose Luiz Lunas De Mello':
		name = 'Massa, J.'
	if name == 'Abdel-Monem, M. S. E. D.':
		name = 'Abdel-Monem, M.'
	if name == 'Al-Shukri, Ali Mohammad S. A.':
		name = 'Al-Shukri, A.'
	if name == 'van Putten, Maurice H. P. M.':
		name = 'van Putten, M.'
	if name == 'Wijesundera, Hapu Arachchige R. V. W.':
		name = 'Wijesundera, H.'
	if name == 'Orta Ortiz de Zarate, Jose Alejandro':
		name = 'Orta Ortiz de Zarate, J.'
	if name == "Drouet D'Aubigny, Christian Yann Pierre":
		name = "Drouet D'Aubigny, C."
	if name == 'Guimaraes, Antonio Candido De Camargo, Jr.':
		name = 'Guimaraes, A.'
	if name == 'Vega, Michael Francis Ian G., II':
		name = 'Vega, Michael'
	if name == 'Morris, Clifford Dean, Jr.':
		name = 'Morris, Clifford D.'
	if name == 'Jones Forman, Christine':
		name = 'Jones, Christine'
	if name == 'Elmergreen, Bruce Gordon':
		name = 'Elmegreen, Bruce Gordon'
	if name == 'Devore, John Gerald':
		name = 'DeVore, John Gerald'
	if name == 'Aguilar-Chiu, Luis Alberto':
		name = 'Aguilar, Luis Alberto'
	if name == 'Del Campo, Sergio Enrique':
		name = 'del Campo, Sergio Enrique'
	if name == 'Bjoernsson, Gunnlaugur':
		name = 'Bjornsson, Gunnlaugur'
	if name == 'Deforest, Craig Edward':
		name = 'DeForest, Craig Edward'
	if name == 'Deboer, David Robert':
		name = 'DeBoer, David Robert'
	if name == "dell'Antonio, Ian Pietro":
		name = "Dell'Antonio, Ian Pietro"
	if name == 'Duchêne, Gaspard':
		name = 'Duchene, Gaspard'
	if name == 'van den Broeck, Chris':
		name = 'Van Den Broeck, Chris'
	if name == 'de Felice, Antonio':
		name = 'De Felice, Antonio'
	if name == 'Leblanc, Paul James, IV':
		name = 'LeBlanc, Paul James, IV'
	if name == 'Alonso Garcia, Javier':
		name = 'Alonso-Garcia, Javier'
	if name == 'Bogosavljević, Milan':
		name = 'Bogosavljevic, Milan'

	while numFound == 0:
		r = requests.get('https://api.adsabs.harvard.edu/v1/search/query',
			params = {'q':'author:("{}")'.format(name),
			'fl':'bibcode,author,year,id,aff',
			'sort':'pubdate desc',
			'rows': '{}'.format(n_max_pubs),
			'fq':'year:[{} TO {}],database:"astronomy",property:refereed'.format(phd_year, year_end)},
			headers={'Authorization':'Bearer:{}'.format(ADS_TOKEN)}
			)
		attempts+=1
		print(r.json().keys())
		if 'error' in r.json().keys():
			return ['-','-','-',0,name,'-']
		#print(r.json()['responseHeader'])
		numFound = r.json()['response']['numFound']	
		if attempts > 1:
			print('{}: attempt {}'.format(name, attempts))
			time.sleep(np.random.randint(0,high=5, size=1)[0])

	last_name = name.split(',')[0]

	last_affil = '-'
	country = '-'
	auth_match = '-'
	for ii, doc in enumerate(r.json()['response']['docs']):
		
		doc['author'] = [unidecode.unidecode(s) for s in doc['author']]
		if ii == 4:
			print(name, len(doc['author']), len(doc['aff']))
		aff_dict = dict(zip(map(str,doc['author']), doc['aff']))

		try:
			auth_match = [s for s in aff_dict.keys() if last_name in s][0]
			last_affil = aff_dict[auth_match]

			if 'USA' in last_affil:
				country = 'USA'
			elif last_affil == '-':
				country = '-'
			else:
				country = 'non-USA'



			if last_affil != '-':
				#print(country, doc['year'], last_affil, ii, name, auth_match)
				break
			else:
				continue
		except:
			continue

	return (country, doc['year'], last_affil, ii, name, auth_match)

def get_all_last_institution():

	"""
	people with no affiliation:
	1970 Cleghorn, Timothy Fuller 445 446
	1975 Butler, D. M. 1 1
	1985 Blau, Steven Kennith 1 1
	1990 Herbst, Thomas Michael 36 36
	1995 Montgomery, Kent Alan 4 4
	2000 Saucedo-Morales, Julio Cesar 2 2
	2010 Parsons, Reid Allen 2 2
	2010 Slater, Stephanie Jean 4 4
	"""

	import ads.publications

	files = ['../data/ads_1970_pub_stats.dat','../data/ads_1975_pub_stats.dat','../data/ads_1980_pub_stats.dat','../data/ads_1985_pub_stats.dat',
			'../data/ads_1990_pub_stats.dat','../data/ads_1995_pub_stats.dat','../data/ads_2000_pub_stats.dat','../data/ads_2005_pub_stats.dat',
			'../data/ads_2010_pub_stats.dat']

	past_year = 2015
	for file in files[8:]:    
		print(file)
		outfile = open(file.replace('_pub_stats.dat','_last_institution.dat'),'w')

		year = int(file.split('_')[1])
		data = ascii.read(file)
	
		index = (data['fa_year_last']>=past_year) | (data['all_year_last']>=past_year)
		print(year, len(data), np.sum(index), np.float(np.sum(index))/len(data))
		for name in data['name'][index]:
			r = ads.publications.last_institution(name=name, phd_year=year)

			outfile.write('{}|{}|{}|{}|{}|{}\n'.format(r[0],r[1],r[2],r[3],r[4],r[5]))
        
		outfile.close()


