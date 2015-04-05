clear all;
close all;

statsTbl = readtable('ndvistats.csv');
areaTbl = readtable('ndviareastats.csv');

areaTbl.date = strcat(num2str(areaTbl.year), '-', num2str(areaTbl.month));
statsTbl.date = strcat(num2str(statsTbl.year), '-', num2str(statsTbl.month));

areavals = table2array(areaTbl(:, 3:7));
statvals = table2array(statsTbl(:, 3:7));

figure
plot(areavals);
ax = gca;
set(ax, 'XGrid', 'on');
set(ax, 'YGrid', 'off');
set(ax, 'XTick', 1:12:length(areavals));
set(ax, 'XTickLabel', areaTbl.year(1:12:length(areavals)));
legend('\leq0','0<N\leq0.2','0.2<N\leq0.4','0.4<N\leq0.6','\geq0.6');

figure
plot(statvals);
ax = gca;
set(ax, 'XGrid', 'on');
set(ax, 'YGrid', 'off');
set(ax, 'XTick', 1:12:length(statvals));
set(ax, 'XTickLabel', areaTbl.year(1:12:length(statvals)));
legend('\leq0','0<N\leq0.2','0.2<N\leq0.4','0.4<N\leq0.6','\geq0.6');