import ads 
import glob
import numpy as np



def table_phd_gender():

	data_file = '/Users/selene/Documents/Career_study/ads_careers/data/gender_breakdown.dat'

	table2_file = open('/Users/selene/Documents/Career_study/ads_careers/data/table2.csv','w')
	table2_file.write('Year, Total PhDs, Men PhDs, Women Phds, Underetmined\n')

	with open(data_file) as f:
		for line in f:
			if line.startswith('#'):
				continue
			else:
				values = line.split()
				print values
				table2_file.write('{:s}, {:s}, {:s} ({:5.2f}%), {:s} ({:5.2f}%), {:d} ({:5.2f}%)\n'.format(values[0], values[1], values[3], 100.*float(values[3])/float(values[1]), values[2], 100*float(values[2])/float(values[1]), int(values[4])+int(values[5]), 100*(float(values[4])+float(values[5]))/float(values[1])))

	table2_file.close()

def table_phd_number():

	import yaml, json

	us_institutions = ads.get_data.read_usa_institutions()
	table1_file = open('/Users/selene/Documents/Career_study/ads_careers/data/table1.csv','w')
	table1_file.write('Year, Total PhDs, US PhDs, Foreign PhDs, Unknown Origin\n')

	years = np.arange(1990, 2011, 1)
	years = np.arange(1990, 2014, 1)

	for year in years:
		print year
		no_affil = 0
		us_affil = 0
		foreign_affil = 0

		files = glob.glob('/Users/selene/Documents/Career_study/ads_careers/data/ads_{}*.dat'.format(year))

		for file in files:
			#print file

			data = open(file,'r')
			data_j = yaml.load(data.readline())

			if file == files[0]:
				count = data_j['meta']['hits']

			for i in range(len(data_j["results"]["docs"])):
				if data_j["results"]["docs"][i]["aff"] == ['-']:
					#print data_j["results"]["docs"][i]
					no_affil += 1
				else:
					affil =  json.dumps(data_j["results"]["docs"][i]["aff"])[2:-2]
					if affil in us_institutions:
						us_affil += 1
					else:
						foreign_affil += 1

		table1_file.write('{:d}, {:d}, {:d} ({:5.2f}%), {:d} ({:5.2f}%), {:d} ({:5.2f}%)\n'.format(year, count-1, us_affil, 100.*float(us_affil)/float(count-1), foreign_affil, 100*float(foreign_affil)/float(count-1), no_affil, 100*(no_affil)/float(count-1)))
		#print count-1, (us_affil+foreign_affil+no_affil), us_affil, foreign_affil, no_affil, no_affil/float(count)

	table1_file.close()







