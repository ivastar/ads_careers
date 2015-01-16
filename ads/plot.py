import urllib
import json
import yaml
import glob
import numpy as np
import astropy
import astropy.io.ascii

def plot_number_phds():

	import matplotlib.pyplot as plt

	phds = astropy.io.ascii.read('number_of_phds.dat')
		
	width=1.
	fig, ax = plt.subplots(figsize=(9,5))

	ads_phds = ax.bar(phds['year'], phds['ads'], width, color='r', alpha=0.5, edgecolor='white')
	nsf_phds = ax.bar(phds['year']+0.5, phds['nsf'], width, color='0.3', alpha=0.8, edgecolor='white')

	ax.set_ylabel('Number of Dissertations per Year', fontsize=12)
	ax.set_xlabel('Year', fontsize=12)
	ax.set_xticks(np.arange(1990, 2011, 2))
	ax.set_xticklabels(np.arange(1990, 2011, 2), fontsize=12)
	ax.set_xlim([1989.5, 2012])
	ax.set_ylim([0, 450])

	ax.legend((nsf_phds[0], ads_phds[0]), ('NSF', 'ADS'), loc='upper left', frameon=False)

	plt.show(block=False)
	
	fig.savefig('number_phds.png', dpi=300)

def plot_number_phds_gender():

	"""
	Plot a histogram with 100% bars, colored by the fraction of PhDs of each gender.
	"""

	import numpy as np
	import matplotlib.pyplot as plt

	phds = astropy.io.ascii.read('/Users/selene/Documents/Career_study/ads_careers/data/gender_breakdown.dat')
	nodata = np.array(phds['nodata1']+phds['nodata2'], dtype=float)
	all = np.array(phds['all'], dtype=float)

	width=1.
	fig, ax = plt.subplots(figsize=(9,5))

	women = ax.bar(phds['year'], phds['women']/all, width, color='red',  alpha=0.5, edgecolor='white',align='center')	
	men = ax.bar(phds['year'], phds['men']/all, width, color='b', alpha=0.3, edgecolor='white', bottom=(phds['women']/all),align='center')	
	nodata = ax.bar(phds['year'], nodata/all, width, color='0.5', bottom=((phds['men']+phds['women'])/all), alpha=0.5, edgecolor='white',align='center')	
	
	print phds['women']/all
	
	ax.set_ylabel('Fraction of PhD Recipients per Year', fontsize=12)
	ax.set_xlabel('Year', fontsize=12)
	ax.set_xticks(np.arange(1990, 2011, 2))
	ax.set_xticklabels(np.arange(1990, 2011, 2), fontsize=12)
	ax.set_xlim([1989, 2011])
	ax.set_ylim([0, 1.1])

	major_yticks = np.arange(0, 1.1, 0.2)                                              
	minor_yticks = np.arange(0, 1.1, 0.1)                                               
	ax.set_yticks(major_yticks)                                                       
	ax.set_yticks(minor_yticks, minor=True)                                           

	ax.text(1990.25, 0.95, 'Unknown')
	ax.text(1990.25, 0.5, 'Men')
	ax.text(1990.25, 0.07, 'Women')
	#ax.yaxis.grid(True, color='1.0', linestyle=':', lw=1.1)
	ax.yaxis.grid(which='minor', alpha=0.5, color='1.0', linestyle=':', lw=1.1)                                                
	ax.yaxis.grid(which='major', alpha=0.9, color='1.0', linestyle=':', lw=1.1)                                                


	plt.show(block=False)
	
	fig.savefig('/Users/selene/Documents/Career_study/ads_careers/plots/number_phds_gender.png', dpi=300)


def plot_fa(year=1990):

	"""
	For a given cohort year plot two histograms: 
	1) of the years of the last first author publication
	2) the same but cumulative
	"""

	import matplotlib.pyplot as plt
	import matplotlib
	from astropy.table import Table, Column
	
	gender_names = read_name_genders()

	file_stats = open('ads_fa_stats.dat','a')
	
	fs = 10
	matplotlib.rc('xtick',labelsize=fs)
	matplotlib.rc('ytick',labelsize=fs)
	
	pubs = Table(names=('year', 'npub', 'name', 'gender'), dtypes=('i4', 'i4', 'S20','i2'))
	with open('ads_fa_publications_{}_authors.dat'.format(year)) as f:
		for line in f:
			yy = line.split('\t')[0]
			npu = line.split('\t')[1]
			names = line.split('[')[1].replace(']','').replace('\'','').strip().split(',')
			name = names[1].strip().replace('.','') 
			if name in gender_names.keys():
				pubs.add_row((yy, npu, name, gender_names[name]))
			else:
				pubs.add_row((yy, npu, name, 3))


	#return
	#pubs = astropy.io.ascii.read('ads_fa_publications_{}.dat'.format(year), names=['year', 'npub'])
	pubs = pubs[pubs['npub'] < 40]
	nn_all = float(len(pubs['npub']))
	nn_all_w = float(np.sum(pubs['gender'] == 1))
	nn_all_m = float(np.sum(pubs['gender'] == 2))
	nn_all_u = float(np.sum(pubs['gender'] == 3))

	bins_year = np.arange(1989, 2015, 1)
	bins_npub = np.arange(0,200,5)
	n, bins, patches = plt.hist(pubs['year'], bins = bins_year, histtype='stepfilled', color='red', alpha=0.2)
	n_cum, bins, patches = plt.hist(pubs['year'], bins = bins_year, histtype='stepfilled', color='red', alpha=0.2, cumulative=True)	
	recent = (pubs['year'] >= 2012)
	n_npub, bins_npub, patches = plt.hist(pubs['npub'][recent], bins = bins_npub)
	plt.clf()
		
	fig, ax = plt.subplots(1,3, figsize=(14,4))
	centers = 0.5*(bins_year[1:]+bins_year[:-1])
	width = bins_year[1:]-bins_year[:-1]	

	centers_npub = 0.5*(bins_npub[1:]+bins_npub[:-1])
	width_npub = bins_npub[1:]-bins_npub[:-1]

	ax[0].bar(centers, n, width=width, align='center',color='red', alpha=0.2)
	ax[0].grid(True, color='gray', linestyle=':', zorder=0)
	ax[0].text(1991, (np.max(n)*0.95), 'N = {}'.format(int(nn_all)), fontsize=fs+2)
	
	ax[0].set_ylabel('Number of Last First Author Paper', fontsize=fs)
	ax[0].set_xlabel('Year', fontsize=fs)
	ax[0].set_title('Cohort of {}'.format(year), fontsize=fs)
	ax[0].set_xlim([1989, 2015])
	ax[0].set_ylim([0, max(n+10)])
			
	ax[1].plot([year+3, year+3], [-10, 1000], linestyle='-', color='black')
	ax[1].plot([2014-3, 2014-3], [-10, 1000], linestyle='-', color='black')
	ax[1].bar(centers, n_cum/nn_all, width=width, align='center',color='blue', alpha=0.2)
	ax[1].set_ylabel('Cumulative Fraction of Last First Author Paper', fontsize=fs)
	ax[1].set_xlabel('Year', fontsize=fs)
	ax[1].set_title('Cohort of {}'.format(year), fontsize=fs)
	ax[1].set_xlim([1989, 2015])
	ax[1].set_ylim([0, 1.1])
	ax[1].grid(True, color='gray', linestyle=':', zorder=0)
	
	ax[2].bar(centers_npub, n_npub, width=width_npub, align='center',color='0.5', alpha=0.2)
	ax[2].set_ylabel('Number of Authors', fontsize=fs)
	ax[2].set_xlabel('Number of First Author Papers', fontsize=fs)
	ax[2].set_title('Cohort of {}'.format(year), fontsize=fs)
	ax[2].set_xlim([-5,150])
	ax[2].set_ylim([0, 120])
	ax[2].grid(True, color='gray', linestyle=':', zorder=0)

	aa = np.sum(pubs['year'] <= year+2) # 3-year dropouts
	aa_w = np.sum((pubs['year'] <= year+2) & (pubs['gender'] == 1)) # 3-year women dropouts
	aa_m = np.sum((pubs['year'] <= year+2) & (pubs['gender'] == 2)) # 3-year men dropouts
	aa_u = np.sum((pubs['year'] <= year+2) & (pubs['gender'] == 3)) # 3-year unknown dropouts
	bb = nn_all - np.sum(pubs['year'] <= year+10) # working 10 years after graduation
	bb_w = nn_all_w - np.sum((pubs['year'] <= year+10) & (pubs['gender'] == 1)) # women working 10 years after graduation
	bb_m = nn_all_m - np.sum((pubs['year'] <= year+10) & (pubs['gender'] == 2)) # men working 10 years after graduation
	bb_u = nn_all_u - np.sum((pubs['year'] <= year+10) & (pubs['gender'] == 3)) # unknown working 10 years after graduation
	cc = np.sum(pubs['year'] >= 2012) # published within last 3 years
	cc_w = np.sum((pubs['year'] >= 2012)  & (pubs['gender'] == 1))  # women within last 3 years
	cc_m = np.sum((pubs['year'] >= 2012) & (pubs['gender'] == 2)) # men within last 3 years
	cc_u = np.sum((pubs['year'] >= 2012) & (pubs['gender'] == 3)) # unknown within last 3 years
	n_med = np.median(pubs['npub'][recent]) # published within last 3 years, median n publications
	n_ave = np.average(pubs['npub'][recent])
	n_std = np.std(pubs['npub'][recent].data)
	print n_med, n_ave, n_std

	file_stats.write("{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{:7.2f}\t{:7.2f}\t{:7.2f}\n".format(year, nn_all, nn_all_w, nn_all_m, nn_all_u, aa, aa_w, aa_m, aa_u, bb, bb_w, bb_m, bb_u, cc, cc_w, cc_m, cc_u, n_med, n_ave, n_std))
	file_stats.close()
	
	plt.show(block=False)
	
	fig.savefig('ads_fa_pub_{}.dat.png'.format(year), dpi=300)

def plot_year_multi(year_start=1990, year_end=2010, variable='year_last'):

	"""
	For a series of years plot a 
	"""

	import matplotlib.pyplot as plt
	import matplotlib
	from astropy.table import Table, Column

	fs=8

	years = np.arange(year_start, year_end, 1)
	nn = len(years)
	
	plt.clf()
	fig = plt.figure(1,figsize=(10, 10))

	bins_year = np.arange(1989, 2015, 1)

	for (year,i) in zip(years, range(nn)):

		ax = plt.subplot(5,4,i+1)
		plt.subplots_adjust(hspace=0.0, wspace=0.0)
		
		data = astropy.io.ascii.read('ads_last_publications_{}_authors.dat'.format(year), names=('year_last', 'pubs_total', 'auth_n', 'auth_n_all', 'year_fa_last', 'fa_total', 'last_name', 'first_name','last_affil'), delimiter='|')
	
		n, bins, patches = ax.hist(data[variable], bins = bins_year, histtype='stepfilled', color='red', alpha=0.2)
		#ax[i].bar(centers, n, width=width, align='center',color='red', alpha=0.2)
		ax.grid(True, color='gray', linestyle=':', zorder=0)
		ax.text(1991, (np.max(n)*0.95), 'N = {}'.format(len(data[variable])), fontsize=fs+2)
		
		#ax.set_ylabel('N', fontsize=fs)
		#ax.set_xlabel('Year', fontsize=fs)
		#ax.set_title('Cohort of {}'.format(year), fontsize=fs)
		if (i % 4) == 0:
			ax.set_ylabel('N', fontsize=fs)
			ax.tick_params(axis='y', which='major', labelleft='on')
		else:
			ax.tick_params(axis='y', which='major', labelleft='off')

		if i in range(nn)[-4:]:
			ax.set_xlabel('Year', fontsize=fs)
			ax.tick_params(axis='x', which='major', labelbottom='on')
		else:
			ax.tick_params(axis='x', which='major', labelbottom='off')

		ax.set_xlim([1990, 2015])
		ax.set_ylim([0, 220])

	plt.show(block=False)
	fig.savefig('multi_{}.png'.format(variable), dpi=300)


def plot_n_multi(year_start=1990, year_end=2010, variable='pubs_total'):

	"""
	For a series of years plot histograms of the number of publications:
	variable = 'pubs_total'
	variable = 'fa_total' 
	"""

	import matplotlib.pyplot as plt
	import matplotlib
	from astropy.table import Table, Column

	fs=8

	years = np.arange(year_start, year_end, 1)
	nn = len(years)
	
	plt.clf()
	fig = plt.figure(1,figsize=(10, 10))

	bins_papers = np.arange(0, 200, 5)

	for (year,i) in zip(years, range(nn)):

		ax = plt.subplot(5,4,i+1)
		plt.subplots_adjust(hspace=0.0, wspace=0.0)
		
		data = astropy.io.ascii.read('ads_last_publications_{}_authors.dat'.format(year), names=('year_last', 'pubs_total', 'auth_n', 'auth_n_all', 'year_fa_last', 'fa_total', 'last_name', 'first_name','last_affil'), delimiter='|')
	
		n, bins, patches = ax.hist(data[variable], bins = bins_papers, histtype='stepfilled', color='red', alpha=0.2)
		n1, bins, patches = ax.hist(data[variable][data['year_last'] >= 2012], bins = bins_papers, histtype='stepfilled', color='0.9', alpha=0.5)
		#ax[i].bar(centers, n, width=width, align='center',color='red', alpha=0.2)
		ax.grid(True, color='gray', linestyle=':', zorder=0)
		ax.text(30, 200, 'N = {}'.format(len(data[variable])), fontsize=fs)
		ax.text(30, 180, 'sum = {}'.format(np.sum(data[variable])), fontsize=fs)
		ax.text(30, 160, 'med = {}'.format(np.median(data[variable])), fontsize=fs)
		ax.text(30, 140, 'med = {}'.format(np.median(data[variable][data['year_last'] >= 2012])), fontsize=fs)
		
		#ax.set_ylabel('N', fontsize=fs)
		#ax.set_xlabel('Year', fontsize=fs)
		#ax.set_title('Cohort of {}'.format(year), fontsize=fs)
		if (i % 4) == 0:
			ax.set_ylabel('N', fontsize=fs)
			ax.tick_params(axis='y', which='major', labelleft='on')
		else:
			ax.tick_params(axis='y', which='major', labelleft='off')

		if i in range(nn)[-4:]:
			ax.set_xlabel('Year', fontsize=fs)
			ax.tick_params(axis='x', which='major', labelbottom='on')
		else:
			ax.tick_params(axis='x', which='major', labelbottom='off')

		ax.set_xlim([0, 50])
		ax.set_ylim([0, 220])

	plt.show(block=False)
	#fig.savefig('multi_{}.png'.format(variable), dpi=300)

def plot_fa_multi(year_start=1990, year_end=2010):

	"""
	For a series of years plot histograms of the number of publications:
	variable = 'pubs_total'
	variable = 'fa_total' 
	"""

	import matplotlib.pyplot as plt
	import matplotlib
	from astropy.table import Table, Column

	fs=8

	years = np.arange(year_start, year_end, 1)
	nn = len(years)
	
	plt.clf()
	fig = plt.figure(1,figsize=(10, 10))

	bins_papers = np.arange(0, 200, 5)

	for (year,i) in zip(years, range(nn)):

		ax = plt.subplot(5,4,i+1)
		plt.subplots_adjust(hspace=0.0, wspace=0.0)
		
		data = astropy.io.ascii.read('ads_last_publications_{}_authors.dat'.format(year), names=('year_last', 'pubs_total', 'auth_n', 'auth_n_all', 'year_fa_last', 'fa_total', 'last_name', 'first_name','last_affil'), delimiter='|')
	
		ax.plot(data['fa_total'], data['pubs_total'], 'o', color='red', alpha=0.2)
		ax.grid(True, color='gray', linestyle=':', zorder=0)
		#ax.text(30, 200, 'N = {}'.format(len(data[variable])), fontsize=fs)
		#ax.text(30, 180, 'sum = {}'.format(np.sum(data[variable])), fontsize=fs)
		#ax.text(30, 160, 'med = {}'.format(np.median(data[variable])), fontsize=fs)
		#ax.text(30, 140, 'med = {}'.format(np.median(data[variable][data['year_last'] >= 2012])), fontsize=fs)
		
		#ax.set_ylabel('N', fontsize=fs)
		#ax.set_xlabel('Year', fontsize=fs)
		#ax.set_title('Cohort of {}'.format(year), fontsize=fs)
		if (i % 4) == 0:
			ax.set_ylabel('Co-authored Articles', fontsize=fs)
			ax.tick_params(axis='y', which='major', labelleft='on')
		else:
			ax.tick_params(axis='y', which='major', labelleft='off')

		if i in range(nn)[-4:]:
			ax.set_xlabel('First Author Articles', fontsize=fs)
			ax.tick_params(axis='x', which='major', labelbottom='on')
		else:
			ax.tick_params(axis='x', which='major', labelbottom='off')

		ax.set_xlim([0, 100])
		ax.set_ylim([0, 300])

	plt.show(block=False)

def scatter_year_last_fa(year_start=1990, year_end=2010):

	"""
	For a series of years plot histograms of the number of publications:
	variable = 'pubs_total'
	variable = 'fa_total' 
	"""

	import matplotlib.pyplot as plt
	import matplotlib
	from astropy.table import Table, Column

	fs=8

	years = np.arange(year_start, year_end, 1)
	nn = len(years)
	
	plt.clf()
	fig = plt.figure(1,figsize=(10, 10))

	bins_papers = np.arange(0, 200, 5)

	for (year,i) in zip(years, range(nn)):

		ax = plt.subplot(5,4,i+1)
		plt.subplots_adjust(hspace=0.0, wspace=0.0)
		 
		data = astropy.io.ascii.read('ads_last_publications_{}_authors.dat'.format(year), names=('year_last', 'pubs_total', 'auth_n', 'auth_n_all', 'year_fa_last', 'fa_total', 'last_name', 'first_name','last_affil'), delimiter='|')
		year_last = data['year_last']*1. + np.random.random(size=len(data['year_last'])) 
		year_fa_last = data['year_fa_last']*1. + np.random.random(size=len(data['year_fa_last']))

		ax.plot(year_last, year_fa_last, 'o', color='red', alpha=0.2)
		ax.grid(True, color='gray', linestyle=':', zorder=0)
		#ax.text(30, 200, 'N = {}'.format(len(data[variable])), fontsize=fs)
		#ax.text(30, 180, 'sum = {}'.format(np.sum(data[variable])), fontsize=fs)
		#ax.text(30, 160, 'med = {}'.format(np.median(data[variable])), fontsize=fs)
		#ax.text(30, 140, 'med = {}'.format(np.median(data[variable][data['year_last'] >= 2012])), fontsize=fs)
		
		#ax.set_ylabel('N', fontsize=fs)
		#ax.set_xlabel('Year', fontsize=fs)
		#ax.set_title('Cohort of {}'.format(year), fontsize=fs)
		if (i % 4) == 0:
			ax.set_ylabel('Last First Author Article', fontsize=fs)
			ax.tick_params(axis='y', which='major', labelleft='on')
		else:
			ax.tick_params(axis='y', which='major', labelleft='off')

		if i in range(nn)[-4:]:
			ax.set_xlabel('Last Co-authored Article', fontsize=fs)
			ax.tick_params(axis='x', which='major', labelbottom='on')
		else:
			ax.tick_params(axis='x', which='major', labelbottom='off')

		ax.set_xlim([year-1, 2016])
		ax.set_ylim([year-1, 2016])

	plt.show(block=False)

def plot_dropout_trend():

	import matplotlib.pyplot as plt
	import matplotlib

	data = astropy.io.ascii.read('ads_fa_stats.dat')
		
	fig, ax = plt.subplots(figsize=(9,5))
	
	plt.plot(data['year'][:-3], (data['dropouts']/data['nn_all'])[:-3], 'o', linestyle='-', color='black', lw=2, alpha=0.7)
	plt.plot(data['year'][:-3], (data['dropouts_w']/data['nn_all_w'])[:-3], 'o', linestyle='-', color='red', alpha=0.35)
	plt.plot(data['year'][:-3], (data['dropouts_m']/data['nn_all_m'])[:-3], 'o', linestyle='-', color='blue', alpha=0.35)
	plt.plot(data['year'][:-3], (data['dropouts_u']/data['nn_all_u'])[:-3], 'o', linestyle='-', color='0.5', alpha=0.35)

	
	ax.set_ylabel('Fraction Leaving Active Research Within 3 Years of PhD', fontsize=12)
	ax.set_xlabel('Dissertation Year', fontsize=12)
	ax.set_title('Based on the last first author publication.', fontsize=13)
	ax.set_xticks(np.arange(1990, 2011, 2))
	ax.set_xticklabels(np.arange(1990, 2011, 2), fontsize=12)
	ax.set_xlim([1989.5, 2008.5])
	ax.set_ylim([0, 1.0])
	ax.grid(True, color='0.5', linestyle=':', lw=1.1)
	
	
	plt.show(block=False)
	
	fig.savefig('droput_trend_fa.png', dpi=300)

def plot_still_active():

	import matplotlib.pyplot as plt
	import matplotlib

	data = astropy.io.ascii.read('ads_fa_stats.dat')
		
	fig, ax = plt.subplots(figsize=(9,5))
	
	plt.plot(data['year'][:-3], (data['stillhere']/data['nn_all'])[:-3], 'o', linestyle='-', color='black', lw=2, alpha=0.7)
	plt.plot(data['year'][:-3], (data['stillhere_w']/data['nn_all_w'])[:-3], 'o', linestyle='-', color='red', alpha=0.35)
	plt.plot(data['year'][:-3], (data['stillhere_m']/data['nn_all_m'])[:-3], 'o', linestyle='-', color='blue', alpha=0.35)
	plt.plot(data['year'][:-3], (data['stillhere_u']/data['nn_all_u'])[:-3], 'o', linestyle='-', color='0.5', alpha=0.35)

	
	ax.set_ylabel('Fraction Active Since 2012', fontsize=12)
	ax.set_xlabel('Dissertation Year', fontsize=12)
	ax.set_title('Based on the last first author publication.', fontsize=13)
	ax.set_xticks(np.arange(1990, 2011, 2))
	ax.set_xticklabels(np.arange(1990, 2011, 2), fontsize=12)
	ax.set_xlim([1989.5, 2008.5])
	ax.set_ylim([0, 1.0])
	ax.grid(True, color='0.5', linestyle=':', lw=1.1)
	
	
	plt.show(block=False)
	
	fig.savefig('stillhere_trend_fa.png', dpi=300)

def plot_10_active():

	import matplotlib.pyplot as plt
	import matplotlib

	data = astropy.io.ascii.read('ads_fa_stats.dat')
		
	fig, ax = plt.subplots(figsize=(9,5))
	
	plt.plot(data['year'][:-9], (data['ten']/data['nn_all'])[:-9], 'o', linestyle='-', color='black', lw=2, alpha=0.7)
	plt.plot(data['year'][:-9], (data['ten_w']/data['nn_all_w'])[:-9], 'o', linestyle='-', color='red', alpha=0.35)
	plt.plot(data['year'][:-9], (data['ten_m']/data['nn_all_m'])[:-9], 'o', linestyle='-', color='blue', alpha=0.35)
	plt.plot(data['year'][:-9], (data['ten_u']/data['nn_all_u'])[:-9], 'o', linestyle='-', color='0.5', alpha=0.35)

	
	ax.set_ylabel('Fraction Active 10 Years Post-defense', fontsize=12)
	ax.set_xlabel('Dissertation Year', fontsize=12)
	ax.set_title('Based on the last first author publication.', fontsize=13)
	ax.set_xticks(np.arange(1990, 2011, 2))
	ax.set_xticklabels(np.arange(1990, 2011, 2), fontsize=12)
	ax.set_xlim([1989.5, 2008.5])
	ax.set_ylim([0, 1.0])
	ax.grid(True, color='0.5', linestyle=':', lw=1.1)
	
	
	plt.show(block=False)
	
	fig.savefig('ten_trend_fa.png', dpi=300)
