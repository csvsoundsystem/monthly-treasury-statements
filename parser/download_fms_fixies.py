#!/usr/bin/env python
import codecs
import datetime
from dateutil.relativedelta import relativedelta
import os
import requests
import sys
from thready import threaded

# MTS notes
# Monthly statements are available in the format
# http://www.fms.treas.gov/mts/mts1097.txt (Oct. 97 is the first statement available)
# http://www.fms.treas.gov/mts/mtsMMYY.txt
# "The release date for the MTS (for the prior month) is at 2:00 PM on the 8th business day of each month."

BASE_URL = 'http://www.fms.treas.gov/mts/'
SAVE_DIR = os.path.join('..', 'data', 'fixie')

################################################################################
def check_dates(start_date, end_date):
	earliest_date = datetime.date(1997, 10, 1)
	if start_date < earliest_date:
		print '\n**WARNING:', start_date, 'before earliest available date (',
		print str(earliest_date), ')'
		print '... setting start_date to', str(earliest_date)
		start_date = earliest_date
	if start_date > end_date:
		temp = start_date
		start_date = end_date
		end_date = temp

	return start_date, end_date

################################################################################
def generate_date_range(start_date, end_date):
	start_date, end_date = check_dates(start_date, end_date)
	dates = []
	td = relativedelta(months=1)
	current_date = start_date
	while current_date <= end_date:
		dates.append(current_date)
		current_date += td
	return dates

################################################################################
def request_fixie(fname):
	request_url = BASE_URL+fname
	print "Requesting:", request_url
	response = requests.get(request_url)
	if response.status_code == 200:
		return response.text
	# check in working directory instead (?? - CMB)
	else:
		return None

################################################################################
def request_and_test_fixie(fname):
	fixie = request_fixie(fname)
	if fixie:
		print 'INFO: saving', os.path.join(SAVE_DIR, fname)
		f = codecs.open(os.path.join(SAVE_DIR, fname), 'wb', 'utf-8')
		f.write(fixie)
		f.close()
	if fixie is None:
		print 'WARNING:', fname, 'not available'

################################################################################
def download_fixies(start_date, end_date=None):
	if not end_date:
		end_date = start_date
	all_dates = generate_date_range(start_date, end_date)
	print '\nINFO: Downloading FMS MTS from', all_dates[0], 'to', all_dates[-1], "!\n"
	fnames = [''.join(['mts',datetime.datetime.strftime(date, '%m%y'), '.txt']) for date in all_dates]
	threaded(fnames, request_and_test_fixie, 20, 100)

################################################################################
if __name__ == '__main__':
	try:
		start_date = datetime.datetime.strptime(str(sys.argv[1]), '%Y-%m').date()
	except IndexError:
		print 'ERROR: must provide date as argument!'
		sys.exit()
	try:
		end_date = datetime.datetime.strptime(str(sys.argv[2]), '%Y-%m').date()
	except IndexError:
		end_date = start_date

	download_fixies(start_date, end_date)


