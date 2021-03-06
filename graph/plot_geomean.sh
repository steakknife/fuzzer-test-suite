#!/usr/local/bin/gnuplot --persist

reset
set term pdf
set output ARG3.'_'.ARG1.'.pdf'
set ylabel ARG1
col=ARG2 + 0
set title "Julian's nice work"
set style data linespoints
plot 'geomean_baseline_'.ARG3.'.csv' using col t "Geomean" lc -1, \
     'geomean_simpler_'.ARG3.'.csv' using col t "Geomean" lc 1, \
    #  'geomean_simpler_'.ARG3.'.csv' using col t "Geomean" lc 2
