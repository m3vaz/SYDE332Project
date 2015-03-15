from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from models import Flow

engine = create_engine('mysql://root:pass1234@localhost/SYDE332')
Session = sessionmaker(bind=engine)
session = Session()


#clear flow data
flows = session.query(Flow).delete()

# deal with sacremento data first
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

# deal with san joaquin data first
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