from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from models import Flow, Storage, Precip

engine = create_engine('mysql://root:pass1234@localhost/SYDE332')
Session = sessionmaker(bind=engine)
session = Session()


#clear flow data
flows = session.query(Flow).delete()

# deal with sacremento data
raw = open('SacrementoFlowData.txt', 'r')

s = raw.readline()
while s[:4] != 'USGS':
	s = raw.readline()

line = 1
while s != '':
	print(line)
	line += 1
	row = s.split('\t')
	date = row[2].split('-')
	# first column is agency, second column is site, 
	# third column is date, fourth column is flow
	parseddata = Flow(site=row[1], measuredateyear = date[0], measuredatemonth = date[1], measuredateday = date[0], amount = row[3], datapoints = 1)
	session.add(parseddata)
	
	s = raw.readline()
	
raw.close()

# deal with san joaquin data
raw = open('SanJoaquinFlowData.txt', 'r')

s = raw.readline()
while s[:4] != 'USGS':
	s = raw.readline()

line = 1
while s != '':
	print(line)
	line += 1
	row = s.split('\t')
	date = row[2].split('-')
	# first column is agency, second column is site, 
	# third column is date, fourth column is flow
	parseddata = Flow(site=row[1], measuredateyear = date[0], measuredatemonth = date[1], measuredateday = date[0], amount = row[3], datapoints = 1)
	session.add(parseddata)
	
	s = raw.readline()
	
raw.close()
session.commit()
# all flow data added
# compile monthly averages

# session.rollback()

sites = session.query(Flow.site).distinct().all(); # each object is a tuple

for site in sites:
	from datetime import date
	from dateutil.relativedelta import *
	site = site[0]; # get the numeric values
	startyear = session.query(func.min(Flow.measuredateyear)).scalar()
	startmonth = session.query(func.min(Flow.measuredatemonth)).filter(Flow.measuredateyear == startyear).scalar()
	endyear = session.query(func.max(Flow.measuredateyear)).scalar()
	endmonth = session.query(func.max(Flow.measuredatemonth)).filter(Flow.measuredateyear == endyear).scalar()
	
	currentdate = date(startyear, startmonth, 1)
	enddate = date(endyear, endmonth, 1)
	
	while currentdate <= enddate:
		
		val = session.query(func.avg(Flow.amount), func.count(Flow.amount)).filter(Flow.measuredateyear == currentdate.year).filter(Flow.measuredatemonth == currentdate.month).filter(Flow.site == site).one()
		avgdata = Flow(site=site, measuredateyear = currentdate.year, measuredatemonth = currentdate.month, measuredateday = None, amount = val[0], datapoints = val[1], average = True)
		session.add(avgdata)
		currentdate = currentdate+relativedelta(months=+1);

session.commit()

# The NVDI spatial data has been extracted using the hdftool from matlab and then slimmed down to size by using the area encompassed by the source and mouth of the san joaquin river


# The precipitation data has already been preaveraged (thanks to NOAA)
scaling = {'CHVC1': 0,'HETC1': 0,'NMDC1': 0,'SCKC1': 0,'SONC1': 0,'YPQC1': 0}
files = ['precipSJ2002.csv','precipSJ2012.csv']
for file in files:
	raw = open(file, 'r')
	year = file.strip('.csv')[-4:]
	
	raw.readline() # header lines
	
	line = 1
	mayamount = 0
	apramount = 0
	areaScale = 0
	dataPoints = 0
	
	while s != '':
		print (line)
		line += 1
		s.readLine()
		row = s.split(',')
		if row[0] in scaling.keys():
			areaScale = scaling[rows[0]];
			dataPoints += 1
			# indexes 8 and 9 are apr, may
			apramount += areaScale*rows[8]/1000
			mayamount += areaScale*rows[9]/1000
		else:
			continue;
	
	aprdata = Precip(amount=apramount, measuredateyear = year, measuredatemonth = 4, datapoints = dataPoints)
	maydata = Precip(amount=mayamount, measuredateyear = year, measuredatemonth = 5, datapoints = dataPoints)
	session.add(aprdata)
	session.add(maydata)
	raw.close()

session.commit()

# The GLDAS data (courtesy of JPL)
# there are 6 boxes over the watershed
# top of the entire area is defined by 38 deg 04 min 00 sec N
# bottom of the area is defined by 37 deg 43 min 56 sec N
# left side of area is defined by 121 deg 51 min 04 sec W
# right side of area is defined by 119 deg 10 min 34 sec W
# the areas have already been calculated in matlab (see other projectcalc.m)

#clear storage data
storage = session.query(Storage).delete()

# reading weight values
weights = {}
raw = open('gldasweights.csv')
s = raw.readline()
s = raw.readline()
while s != '':
	row = s.split(',')
	rowValues = [ float(row[0]), float(row[1]), float(row[2])]
	weights[(rowValues[0], rowValues[1])] = rowValues[2]
	s = raw.readline()
raw.close()
		


import os
gldasPath = 'gldas'
filenames = next(os.walk(gldasPath))[2]
for name in filenames:
	raw = open(gldasPath+'\\'+name, 'r')
	year = int(name.strip('gldas').strip('.txt')[:4])
	month = int(name.strip('gldas').strip('.txt')[4:])
	# get through header data
	s = raw.readline()
	while s[:3] == 'HDR':
		s = raw.readline()
	
	# now at the actual data, data structure is long lat value
	
	line = 1
	amount = 0
	areaScale = 0
	dataPoints = 0;
	while s != '':
		print(line)
		line += 1
		row = s.split();
		rowValues = [ float(row[0]), float(row[1]), float(row[2])]
		# looking for long values of 121.5, 120.5, 119.5
		if (rowValues[0] < 236 or rowValues[0] > 242):
			s = raw.readline()
			continue
		# looking for lat values of 37.5, 38.5
		if (rowValues[1] < 36 or rowValues[1] > 42):
			s = raw.readline()
			continue
		
		areaScale = weights[(rowValues[1], rowValues[0]-360)]
		amount += rowValues[2]/100*areaScale # convert from cm -> m
		dataPoints += 1
		
		s = raw.readline()
		#end month processing
	# add the month in now
	parseddata = Storage(amount=amount, measuredateyear = year, measuredatemonth = month, datapoints = dataPoints)
	session.add(parseddata)	
	raw.close()
	
session.commit()





