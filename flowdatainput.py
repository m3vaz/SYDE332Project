from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from models import Flow, Storage, Precip, NDVI

engine = create_engine('mysql://root:pass1234@localhost/SYDE332')
Session = sessionmaker(bind=engine)
session = Session()

#######################################################################
# STREAM FLOW DATA
# ORIGINAL DATA IS IN CUBIC FEET PER SECOND
# UNIT CONVERSION IS DONE IN FINAL SQL EXTRACT
#clear flow data
flows = session.query(Flow).delete()

# deal with sacremento data
raw = open('SacrementoFlowData.txt', 'r')

s = raw.readline()
while s[:4] != 'USGS':
	s = raw.readline()

#line = 1
while s != '':
	#print(line)
	#line += 1
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

#line = 1
while s != '':
	#print(line)
	#line += 1
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

print('Flow Processing Complete')

#######################################################################
# The NDVI Spatial data

ndvi = session.query(NDVI).delete()

#reading weight values
weights = {}
raw = open('ndviweights.csv')
s = raw.readline()
s = raw.readline()
# min max
boundLatVal = [180, -180]
boundLongVal = [360, -360]
while s!= '':
	row = s.split(',')
	rowValues = [ float(row[0]), float(row[1]), float(row[2]) ]
	if rowValues [0] < boundLatVal[0]:
		boundLatVal[0] = rowValues[0]
	if rowValues [0] > boundLatVal [1]:
		boundLatVal[1] = rowValues[0]
	if rowValues[1] < boundLongVal[0]:
		boundLongVal[0] = rowValues[1]
	if rowValues[1] > boundLongVal[1]:
		boundLongVal[1] = rowValues[1]
	weights[(rowValues[0], rowValues[1])] = rowValues[2]
	s = raw.readline()
raw.close()

# because we need to do histograms to prove the data is real
ndviStats = 'ndvistats.csv'
statsOut = open(ndviStats, 'w')
statsOut.write('year,month,<0,0-0.2,0.2-0.4,0.4-0.6,0.6<\n')

areaStats = 'ndviareastats.csv'
areaOut = open(areaStats, 'w')
areaOut.write('year,month,<0,0-0.2,0.2-0.4,0.4-0.6,0.6<\n')

import os
ndviPath = 'NDVI'
filenames = next(os.walk(ndviPath))[2]
for name in filenames:
	#print (name)
	raw = open(ndviPath+'\\'+name, 'r')
	year = int(name.strip('NDVI').strip('.CSV')[:4])
	month = int(name.strip('NDVI').strip('.CSV')[4:])
	
	# header data
	s = raw.readline()
	# figure out which columns you need
	row = s.split(',')
	if (row[0] != 'lat/lon'):# stop processing
		print('Error: '+name)
		int('0.5')
	startlongindex = 0;
	endlongindex = 0;
	longValues = []
	for i in range(1, len(row)):
		long = round(float(row[i]), 2) # round to 2 decimal places
		if long <= boundLongVal[0]:
			startlongindex = i
		if long <= boundLongVal[1]:
			endlongindex = i
			
	for i in range(startlongindex, endlongindex+1):
		long = round(float(row[i]), 2) # round to 2 decimal places
		longValues.append(long)
	
	# we should now have the indices to look for
	
	s = raw.readline()
	#line = 1
	amount = 0
	scaleTotal = 0
	areaScale = 0
	dataPoints = 0
	bins = [0, 0, 0, 0, 0] # <0,0-0.2,0.2-0.4,0.4-0.6,0.6<
	areabins = [0, 0, 0, 0, 0] # <0,0-0.2,0.2-0.4,0.4-0.6,0.6<
	while s != '':
		#print(name)
		#print(line)
		#line += 1
		row = s.split(',')
		lat = round(float(row[0]), 2)
		if lat >= boundLatVal[0] and lat <= boundLatVal[1]:
			for i in range(startlongindex, endlongindex+1):
				long = longValues[i-startlongindex]
				areaScale = weights[(lat, long)]
				scaleTotal += areaScale
				value = float(row[i])
				if value <= 0:
					bins[0] += 1
					areabins[0] += areaScale
				elif value<= 0.2:
					bins[1] += 1
					areabins[1] += areaScale
				elif value<= 0.4:
					bins[2] += 1
					areabins[2] += areaScale
				elif value<= 0.6:
					bins[3] += 1
					areabins[3] += areaScale
				else:
					bins[4] += 1
					areabins[4] += areaScale
				amount += value*areaScale
				dataPoints += 1
				
		s = raw.readline()
	
	# we now have total amount, take average
	amount = amount/sum(weights.values())
	#print(str(year) +'-'+str(month)+' '+str(bins))
	statsOut.write(str(year)+','+str(month)+','+str(bins[0])+','+str(bins[1])+','+str(bins[2])+','+str(bins[3])+','+str(bins[4]))
	statsOut.write('\n')
	
	areaOut.write(str(year)+','+str(month)+','+str(areabins[0])+','+str(areabins[1])+','+str(areabins[2])+','+str(areabins[3])+','+str(areabins[4]))
	areaOut.write('\n')
	
	data = NDVI(amount=amount, measuredateyear = year, measuredatemonth = month, datapoints = dataPoints)
	session.add(data)
	
	raw.close()

statsOut.close()
areaOut.close()
session.commit()
print('NDVI processing complete')
	
#######################################################################
# The precipitation data has already been preaveraged (thanks to NOAA)

precip = session.query(Precip).delete()

# grab scaling data first
scaling = {}
file = 'precipStationAreas.csv'
raw = open(file, 'r')

# header line
s = raw.readline()

# first line
s = raw.readline()
#line = 1
while s!= '':
	#print (line)
	#line += 1
	# values of interest are 5 and 6, area and id
	row = s.split(',')
	name = row[6].strip("'").strip('"')
	area = int(row[5])
	scaling[name] = area
	s = raw.readline()
	
raw.close()

# actually process data now
import os
precipPath = 'precip'
filenames = next(os.walk(precipPath))[2]
# can deal with missing data in 2 ways
# zero it
# proportional split
# mode = 'zero'
mode = 'prop'
for file in filenames:
	#print(file)
	raw = open(precipPath+'\\'+file, 'r')
	year = int(file.strip('.csv')[-4:])
	loc = file.strip('.csv')[-6:-4]
	
	s = raw.readline() # header lines
	
	#line = 1
	#print (file)
	amount = [0 for i in range(12)]
	names = [[] for i in range(12)]
	missPoints = [[] for i in range(12)]
	areaScale = 0
	dataPoints = [0 for i in range(12)]

	while s != '':
		#print (line)
		#line += 1
		# process lines first
		s = raw.readline()
		#print(s)
		row = s.split(',')
		stationID = row[0]
		if stationID in scaling.keys(): # station is of interest
			areaScale = scaling[stationID]
			for pos in range(2,14):
				ind = pos-2 # index of processing arrays
				if row[pos] != 'M':
					dataPoints[ind] += 1
					names[ind].append(stationID)
					# october of previous year to september of current
					amount[ind] += areaScale*float(row[pos])*25.4/1000
					# 1000 is for mm -> m conversion
				elif row[pos] == 'M':
					missPoints[ind].append(stationID)
		else:
			continue
	# done processing this file
	raw.close()
	
	# deal with missing data

	if mode == 'zero':
		print('not scaling')
		# do nothing
	elif mode == 'prop':
		# how much area is there total
		tot = sum(scaling.values())
		for i in range(12):
			if dataPoints[i] < len(scaling.keys()):
				#print('scaling data')
				# how much data is there now
				curr = 0
				for key in names[i]:
					curr += scaling[key]
				# scale it
				amount[i] = tot/curr*amount[i]
	else:
		print('boom')
		int('3.5')
	
	# input the data
	# start in october of last year
	datayear = year-1
	datamonth = 10
	for i in range(12):
		# who's missing
		#missing = (set(scaling.keys())-set(names[i]))-set(missPoints[i])
		#if len(missing) > 0:
		#	print('Year ' + str(datayear) + ' ' + str(datamonth) ' ' + str(missing))
		
		data = Precip(amount=amount[i], measuredateyear = datayear, measuredatemonth = datamonth, datapoints = dataPoints[i])
		session.add(data)
		datamonth += 1
		if datamonth >= 13:
			datamonth -= 12
			datayear += 1

session.commit()

print('Precipitation Processing Complete')

#######################################################################
# The GLDAS data (courtesy of JPL)
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
	#print(name)
	raw = open(gldasPath+'\\'+name, 'r')
	year = int(name.strip('gldas').strip('.txt')[:4])
	month = int(name.strip('gldas').strip('.txt')[4:])
	# get through header data
	s = raw.readline()
	while s[:3] == 'HDR':
		s = raw.readline()
	
	# now at the actual data, data structure is long lat value
	
	#line = 1
	amount = 0
	areaScale = 0
	dataPoints = 0;
	while s != '':
		#print(line)
		#line += 1
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

print('GLDAS processing complete')




