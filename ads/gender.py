"""
Scripts to parse the gender data for the PhD recipients.
genderize.io
gender-api.com

"""

import urllib
import json
import yaml
import glob
import numpy as np
import astropy
from astropy.io import ascii
import requests
import os

### gender-api.com
GENDER_API_KEY = os.getenv(GENDER_API_KEY)

### genederize.io
GENDERIZE_API_KEY = os.getenv(GENDERIZE_API_KEY)

def querry_apis(in_file = '../data/tmp_names.dat', out_file='../data/tmp_names_with_gender.dat'):

	"""
	in_file = '../data/ads_unique_names.dat'
	Take a list of unique first names and run then through:
	gender-api.com
	genederize.io
	Write out a table with the responses.
	"""

	out_file = open(out_file,'w')
	out_file.write('name gender1 accuracy1 samples1 gender2 accuracy2 samples2\n')

	with open(in_file) as f:
		for line in f:
			name = line.strip()
			print(name)
	
			url1 = 'https://gender-api.com/get?name={}&key={}'.format(name, GENDER_API_KEY)
			response1 = requests.get(url1)
			#print(response1.json())

			if (response1.json()['gender'] == 'unknown') & (response1.json()['accuracy'] == 0):
				out_file.write('{0}\t{1}\t{2}\t{2}\t'.format(name,'None',np.nan))
			else: 
				out_file.write('{0}\t{1}\t{2}\t{3}\t'.format(name,response1.json()['gender'],response1.json()['accuracy'],response1.json()['samples']))


			url2 = 'https://api.genderize.io/?name={}'.format(name)
			response2 = requests.get(url2)
			print(response2.json())

			if response2.json()['gender'] == None:
				out_file.write('{0}\t{1}\t{1}\n'.format('None',np.nan))
			else: 
				out_file.write('{}\t{:5.0f}\t{}\n'.format(response2.json()['gender'],response2.json()['probability']*100,response2.json()['count']))


#	count_file = ascii.read(out_file)

#	print('MALE: {}  {}'.format(np.sum(count_file['gender1'] == 'male'), np.sum(count_file['gender2'] == 'male')))
#	print('FEMALE: {}   {}'.format(np.sum(count_file['gender1'] == 'female'), np.sum(count_file['gender2'] == 'female')))
#	print('NONE: {}   {}'.format(np.sum(count_file['gender1'] == 'None'), np.sum(count_file['gender2'] == 'None')))

	out_file.close()


def read_name_genders(file='../data/ads_unique_names_with_gender.dat'):

	"""
	Return a list dictionary of male, female and unknown names.
	"""

	
	name_genders = {}

	api_results = ascii.read(file)

	for line in api_results:
		if (float(line['accuracy1']) > 50.):
			name_genders[line['name']] = line['gender1']
		else: 
			name_genders[line['name']] = 'None'
				
	return name_genders

def parse_names(in_file = '../data/ads_first_names.dat'):

	names = []
	first_initials = []

	with open(in_file,'r') as f:
		for line in f:
			ll = line.strip()
			if (len(ll) == 2) and (ll[-1] == '.'):
				first_initials.append(ll)
			else:
				names.append(ll)
				
	unq_names = np.unique(names)		
	print("There are {} names and {} unique names.".format(len(names), len(unq_names)))
	#print unq_names
	print("There are {} entries with only a first initial.".format(len(first_initials)))

	with open('../data/ads_unique_names.dat', 'w') as f_out:
	    for l in unq_names:
	        f_out.write(l)
	        f_out.write('\n')
					
	print("Output file is ads_unique_names.dat")

def gender_breakdown():

	gender_names = read_name_genders()

	years = np.arange(1970, 2019, 1)

	os.system('rm ../data/gender_breakdown.dat')
	file_out = open('../data/gender_breakdown.dat','a')
	file_out.write('# year all women men nodata\n')

	for year in years:

		file = '../data/ads_{}_parse.dat'.format(year)


		gn = []

		print(file)
		data = ascii.read(file, delimiter='|', names=['n','name','school','year','foo'])

		for i in range(len(data)):
			try:
				tmp_name = data[i]['name'].split(',')[1].split()
				if (len(tmp_name[0]) == 2) and (tmp_name[0][-1] == '.') and (len(tmp_name) > 1) and (tmp_name[1][0] != '-'):
					name = tmp_name[1]
					name = name.replace('.','').replace('(','').replace(')','')
					if name.startswith('-'):
						name = name[1:]
					try:
						gn.append(gender_names[name])
					except:
						gn.append('None')
				elif (len(tmp_name[0]) == 2) and (tmp_name[0][-1] == '.') and (len(tmp_name) == 1):
					gn.append('None')
				else:
					name = tmp_name[0]
					name = name.replace('.','').replace('(','').replace(')','')
					if name.startswith('-'):
						name = name[1:]
					try:
						gn.append(gender_names[name])
					except:
						gn.append('None')
						print(name)
			except:
				print(data[i]['name'])

		gn = np.array(gn, dtype='str')
		
		file_out.write("{}\t{}\t{}\t{}\t{}\n".format(year, len(gn), np.sum(gn == 'female'), np.sum(gn == 'male'), np.sum(gn == 'None')))
		
		print("{}\t{}\t{}\t{}\t{}\n".format(year, len(gn), np.sum(gn == 'female'), np.sum(gn == 'male'), np.sum(gn == 'None')))

	print("Output file is ../data/gender_breakdown.dat")

	file_out.close()

def compare_gender_assignments():

	out_file = '../data/ads_unique_names_with_gender.dat'
	count_file = ascii.read(out_file)


	index = ((count_file['gender1'] == 'female') & (count_file['gender2']=='male'))
	print(count_file[index])

	index = ((count_file['gender1'] == 'male') & (count_file['gender2']=='female'))
	print(count_file[index])











