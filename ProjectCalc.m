% this file is meant for project calculations
% I like cats
%% WE BEGIN
% NO LONGER USED

% intervalcount = 1200;
% pointcount = intervalcount+1;
% % 1 arc minute is 1/60 of a degree, 1 arc second is 1/3600 of a degree
% target = [ 121+51*1/60+04*1/3600 38+04*1/60+00*1/3600];
% % dest is 121 deg 51' 04'' W 38 deg 04' 00'' N
% target = [ target; 119+10*1/60+34*1/3600 37+43*1/60+56*1/3600 ];
% % src is 119 deg 10' 34'' W 37 deg 43' 56'' N
% 
% 
% lat = zeros (pointcount, pointcount);
% long = zeros (pointcount, pointcount);
% 
% % generate lat values for the first row
% latbound = [ 39.9999999964079 40.0852255853565 ; 29.8308028608368 29.9062514942912];
% f = @(x) latbound(1,1) + (latbound(1,2)-latbound(1,1))*(x-1)/(2001-1);
% for i = 1:pointcount
%    lat(1,i) = f(i);
% end 
% % similar for last row
% f = @(x) latbound(2,1) + (latbound(2,2)-latbound(2,1))*(x-1)/(2001-1);
% for i = 1:pointcount
%    lat(pointcount,i) = f(i);
% end
% % calculate the lat values going across
% for i = 1:pointcount
%     f = @(x) lat(1,i) + (lat(pointcount,i)-lat(1,i))*(x-1)/(pointcount-1);
%     for j = 2:pointcount-1
%         lat(j,i) = f(j);
%     end
% end
% 
% % same exact thing for long values generate long values for the first row
% longbound = [ 130.540728914638 117.360631853124 ; 115.369550008828 103.699828723654];
% f = @(x) longbound(1,1) + (longbound(1,2)-longbound(1,1))*(x-1)/(2001-1);
% for i = 1:pointcount
%    long(1,i) = f(i);
% end 
% % similar for last row
% f = @(x) longbound(2,1) + (longbound(2,2)-longbound(2,1))*(x-1)/(2001-1);
% for i = 1:pointcount
%    long(pointcount,i) = f(i);
% end
% % calculate the long values going across
% for i = 1:pointcount
%     f = @(x) long(1,i) + (long(pointcount,i)-long(1,i))*(x-1)/(pointcount-1);
%     for j = 2:pointcount-1
%         long(j,i) = f(j);
%     end
% end
% 
% % find the points area
% 
% disp('Finding points');
% 
% targetfound = 0;
% for i = 1:intervalcount
%     longcomp = [];
%     latcomp = [];
%     for j = 1:intervalcount
%         if ( all(long(i,j) < target(:, 1)) && all(long (i+1, j) < target(:, 1)))
%             continue;
%         elseif (all(long(i, j+1) > target(:, 1)) && all(long(i+1, j+1) > target(:, 1)))
%             continue;
%         elseif (all(lat (i, j) < target(1, :)) && all(lat (i, j+1) < target (1, :)))
%             continue;
%         elseif (all(lat (i+1, j) > target(1, :)) && all(lat (i+1, j+1) > target (1, :)))
%             continue;
%         end
%         bounds = [ long(i, j) lat(i,j) ];
%         bounds = [ bounds ; long(i, j+1) lat(i, j+1)];
%         bounds = [ bounds ; long(i+1, j+1) lat(i+1, j+1)];
%         bounds = [ bounds ; long(i+1, j) lat(i+1, j) ];
%         in = inpoly(target, bounds);
%         if max(in)
%             targetfound = targetfound+1;
%             disp(i);
%             disp(j);
%         end
%         if targetfound == length(target)
%             break;
%         end
%     end
%     if targetfound == length(target)
%         break;
%     end
% end

%% this is meant for calcuating area elements for GLDAS data 
% each gldas grid element is 1 degree by 1 degree in spherical and so
% requires separate calcuations to figure out the volume of water

decimalize = @(deg, min, sec) sign(deg)*(abs(deg)+abs(min)/60+abs(sec)/3600);
radify = @(deg) deg./180.*pi();
degreefiy = @(rad) rad/pi()*180;
radiusearth = 6371.009*1000; % average rad in meters of earth from IUGG
area = @(lat1, lat2, long1, long2) radiusearth^2 *(cos(lat2)-cos(lat1))*(long2-long1);
% 
% % there are 6 boxes over the watershed
% % top of the entire area is defined by 38 deg 04 min 00 sec N
% % bottom of the area is defined by 37 deg 43 min 56 sec N
% % left side of area is defined by 121 deg 51 min 04 sec W
% % right side of area is defined by 119 deg 10 min 34 sec W
% 
% lat = [decimalize(38, 04, 0) decimalize(38, 00, 00) decimalize(37,43,56) ];
% lat = 90 - lat; % since using azimuthal angles measured from pole
% lat = radify(lat);
% long = [decimalize(121,51,04) decimalize(121, 00, 00) ...
%     decimalize(120, 00, 00) decimalize(119, 10, 34)];
% long = radify(long); % do not need to offset
% 
% A1 = area(lat(1), lat(2), long(1), long(2));
% A2 = area(lat(1), lat(2), long(2), long(3));
% A3 = area(lat(1), lat(2), long(3), long(4));
% A4 = area(lat(2), lat(3), long(1), long(2));
% A5 = area(lat(2), lat(3), long(2), long(3));
% A6 = area(lat(2), lat(3), long(3), long(4));
% areas = [A1 A2 A3; A4 A5 A6] ;

%decimalize = @(deg, min, sec) sign(deg)*(abs(deg)+abs(min)/60+abs(sec)/3600);
radify = @(deg) deg./180.*pi();
degreefiy = @(rad) rad/pi()*180;
radiusearth = 6371.009*1000; % average rad in meters of earth from IUGG
area = @(lat1, lat2, long1, long2) radiusearth^2 *(cos(90-lat2)-cos(90-lat1))*(long2-long1);

watershed = [40.90 -123.16; 41.82 -120.64; 37.22 -118.93; 36.47 -120.93];
% this part is simple sorta
coords = [];
for i =0:5
    for j = 0:5
        bounds = [36+i -124+j; 36+i+1 -124+j; 36+i+1 -124+j+1; 36+i -124+j+1 ]
        areaelement = abs(area(radify(36+i), radify(36+i+1), radify(-124+j), radify(-124+j+1)));
        coords = [coords; 36.5+i -123.5+j areaintersection(watershed, bounds,1500)*areaelement];
    end
end
weights = table (coords(:, 1), coords(:, 2), coords(:, 3));
writetable(weights, 'gldasweights.csv');


%% this is meant for calcuating area elements for NDVI data 
% each nvdi grid element is 0.1 degree by 0.1 degree in spherical and so
% requires separate calcuations to figure out the contribution

radify = @(deg) deg./180.*pi();
radiusearth = 6371.009*1000; % average rad in meters of earth from IUGG
area = @(lat1, lat2, long1, long2) radiusearth^2 *(cos(90-lat2)-cos(90-lat1))*(long2-long1);

watershed = [40.90 -123.16; 41.82 -120.64; 37.22 -118.93; 36.47 -120.93];
% this part is simple sorta
coords = [];
resolution = 0.1;
for i =0:resolution:6
    for j = 0:resolution:6
        bounds = [36+i -124+j; 36+i+resolution -124+j; 36+i+resolution -124+j+resolution; 36+i -124+j+resolution ]
        areaelement = abs(area(radify(36+i), radify(36+i+resolution), radify(-124+j), radify(-124+j+resolution)));
        coords = [coords; 36+resolution/2+i -123+resolution/2+j areaintersection(watershed, bounds,1500)/(resolution^2)*areaelement];
    end
end
weights = table (coords(:, 1), coords(:, 2), coords(:, 3));
writetable(weights, 'ndviweights.csv');

for i = 0:5
    beep;
    pause(1);
    beep;
    pause(1);
end


%% because finding stations is hard >__>

decimalize = @(deg, min, sec) sign(deg)*(abs(deg)+abs(min)/60+abs(sec)/3600);

bounds = [40.9 -123.16;...
    41.82 -120.64;...
    37.224 -118.93;...
    36.47 -120.93];

locs = readtable('locations.csv');

% locs.ID, locs.LAT, locs.LONG
locs.INTERIOR = inpoly(table2array(locs(:, 2:3)), bounds);

locs(locs.INTERIOR, { 'ID' 'LAT' 'LONG' })
