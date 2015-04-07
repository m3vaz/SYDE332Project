# SYDE332Project
This is the term project for SYDE 332 offered during W15. NDVI data is not included as it would take several GB to upload. 

The python package SQLAlchemy was used to use a MySQL persistent store. 

ProjectCalc.m includes calculations necessary before processing the data (specifically weights for GLDAS and NVDI data)

models.py creates the relevant models in the persistent store. 

FlowDataInput.py processes the data and inputs it into the persistent store.

DataProcessingDump.sql is the final query to be operated on to gather all final data. 

The several CSV files in the root folder.

ndvidump.csv is the dump of processed ndvi data

precipdump.csv is the dump of processed precipitation data

storagedump.csv is the dump of processed gldas moisture data (not the differences)

finaldata.csv is the result of running the processingdump sql script. It contains all variables in the hydrologic budget equation.

This repo will not be updated past 11:55 PM April 6, 2015 EST for a minumum period of 3 weeks and no maximum period of inactivity.
