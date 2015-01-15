import urllib
import json
import yaml
import glob
import numpy as np
import astropy
import astropy.io.ascii


def read_name_genders():

	"""
	3 == unknown
	2 == male
	1 == female
	"""

	name_genders = {}
	with open('../Results/results.csv') as f:
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

def gender_breakdown(year = 2002):

	gender_names = read_name_genders()
	us_institutions = read_usa_institutions()

	files = glob.glob('ads_{}_*.dat'.format(year))
	file_out = open('../data/gender_breakdown.dat','a')

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