import urllib
import json
import yaml
import glob
import numpy as np
import astropy
import astropy.io.ascii
import ads


def read_name_genders(file='/Users/selene/Documents/Career_study/Results/genderize_api_results.csv'):

	"""
	3 == unknown
	2 == male
	1 == female
	"""

	name_genders = {}
	with open(file) as f:
		for line in f:
			if line.startswith("#"):
				continue
			values = line.split(',')
			if values[1].strip() == 'u':
				name_genders[values[0].strip()] = 3
			elif values[1].strip() == 'm':
				name_genders[values[0].strip()] = 2
			elif values[1].strip() == 'f':
				name_genders[values[0].strip()] = 1
			else: 
				name_genders[values[0].strip()] = 0
				
	return name_genders

def parse_names():

	files = glob.glob('ads_[12]*_*.dat')
	us_institutions = read_usa_institutions()
		
	names = []

	for file in files:
		print file
		data = open(file,'r')
		data_j = yaml.load(data.readline())
		for i in range(len(data_j["results"]["docs"])):
			if json.dumps(data_j["results"]["docs"][i]["aff"])[2:-2] in us_institutions:
				all_names = data_j["results"]["docs"][i]["author"][0]
				name = all_names.split()[1].encode('ascii','replace').replace(',','')
				names.append(name)
				
	unq_names = np.unique(names)		
	print "There are {} names and {} unique names.".format(len(names), len(unq_names))
	#print unq_names
	
	with open('ads_names.dat', 'w') as f:
	    for l in unq_names:
	        f.write(l)
	        f.write('\n')
					
	print "Output file is ads_names.dat"	

def gender_breakdown(year = 2002, genders_file='/Users/selene/Documents/Career_study/Results/genderize_api_results.csv'):

	gender_names = read_name_genders(file=genders_file)
	us_institutions = ads.get_data.read_usa_institutions()

	files = glob.glob('/Users/selene/Documents/Career_study/ads_careers/data/ads_{}_*.dat'.format(year))
	file_out = open('/Users/selene/Documents/Career_study/ads_careers/data/gender_breakdown.dat','a')


	gn = []

	for file in files:
		print file
		data = open(file,'r')
		data_j = yaml.load(data.readline())
		for i in range(len(data_j["results"]["docs"])):
			if json.dumps(data_j["results"]["docs"][i]["aff"])[2:-2] in us_institutions:
				all_names = data_j["results"]["docs"][i]["author"][0]
				name = all_names.split()[1].encode('ascii','replace').replace(',','')
				if name in gender_names.keys():
					gn.append(gender_names[name])
				else:
					gn.append(-1)
	
	gn = np.array(gn)
	file_out.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(year, len(gn), np.sum(gn == 1), np.sum(gn == 2), np.sum(gn == 3), np.sum(gn == -1)))
	
	print "Output file is gender_breakdown.dat"


def querry_genderize():

	name_genders = read_name_genders()
	d = dict((k,v) for k,v in name_genders.items() if v == 3)
	test_names = d.keys()
	test_names = name_genders.keys()

	n_calls = int(len(test_names)/300)+1

	gender = np.zeros(len(test_names),dtype='10S')

	out_file = open('/Users/selene/Documents/Career_study/Results/genderize_api_results_compare.csv','w')

	for nn in range(n_calls):
		url = 'http://api.genderize.io?'
		n_min = nn*300
		if nn*300+299 > len(test_names):
			n_max = len(test_names)-1
		else:
			n_max = nn*300+299
		print n_min, n_max, len(test_names)
		run_names = test_names[n_min:n_max]

		for name,i in zip(run_names, range(len(run_names))):
			name_first = name.split('-')[0]
			if (i != 0):
				url = url+'&'
			url = url+'name[{}]={}'.format(i,name_first.lower())

		response = urllib.urlopen(url)
		response_data =  yaml.load(response.read())

		for i, name in zip(range(len(response_data)),run_names):
			gender[n_min+i] = response_data[i]['gender']
			if response_data[i]['gender'] == None:
				out_file.write('{0}, {1}, {2}, {2}\n'.format(name,'u',-1))
			elif response_data[i]['gender'] == 'male':
				out_file.write('{0}, {1}, {2}, {3}\n'.format(name,response_data[i]['gender'][0],float(response_data[i]['probability']), 1-float(response_data[i]['probability'])))
			else:
				out_file.write('{0}, {1}, {2}, {3}\n'.format(name,response_data[i]['gender'][0],1-float(response_data[i]['probability']), float(response_data[i]['probability'])))

	print 'MALE: ',np.sum(gender == 'male')
	print 'FEMALE: ',np.sum(gender == 'female')
	print 'NONE: ',np.sum(gender == 'None')


def compare_gender_assignments():

	names_ss = read_name_genders(file = '/Users/selene/Documents/Career_study/Results/results.csv')
	names_genderize = read_name_genders(file = '/Users/selene/Documents/Career_study/Results/genderize_api_results_compare.csv')

	for key in names_ss.keys():
		if key in names_genderize.keys():
			if ((names_ss[key] != names_genderize[key]) & (names_ss[key] == 3) & (names_genderize[key] != 3)):
				print key, names_ss[key], names_genderize[key]














