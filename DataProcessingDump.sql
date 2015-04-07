select a.measuredateyear, a.measuredatemonth, a.flowAmount, b.NDVIAmount, c.precipAmount, d.storageAmount, c.precipAmount - d.storageAmount - a.flowAmount as ET
from (
	SELECT sum(amount)*0.0283168*86400*day(last_day(concat(measuredateyear, '-', measuredatemonth, '-01'))) as flowAmount, -- convert value from cubic feet per second to cubic meters per day then multiply by number of days
	measuredateyear, 
	measuredatemonth, 
	count(amount) as points 
	FROM syde332.flowdata
	where average
	group by measuredateyear, measuredatemonth
	having points = 2 -- using data from both rivers
	order by measuredateyear, measuredatemonth) a
left outer join (select amount as NDVIAmount, measuredateyear, measuredatemonth from syde332.ndvidata) b
	on a.measuredateyear = b.measuredateyear and a.measuredatemonth = b.measuredatemonth
left outer join (select amount as precipAmount, measuredateyear, measuredatemonth from syde332.precipdata) c
	on a.measuredateyear = c.measuredateyear and a.measuredatemonth = c.measuredatemonth
left outer join (select b.amount-a.amount as storageAmount, a.measuredateyear, a.measuredatemonth
					from syde332.storagedata a 
					inner join syde332.storagedata b 
					on DATE_ADD(STR_TO_DATE(concat(a.measuredateyear, ',', a.measuredatemonth, ',01'),'%Y,%m,%d'), INTERVAL 1 MONTH) 
							= STR_TO_DATE(concat(b.measuredateyear, ',', b.measuredatemonth, ',01'),'%Y,%m,%d')
				) d
	on a.measuredateyear = d.measuredateyear and a.measuredatemonth = d.measuredatemonth
;