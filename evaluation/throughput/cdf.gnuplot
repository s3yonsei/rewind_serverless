#!/usr/bin/gnuplot

set output "cdf.eps"
set terminal postscript eps color enhanced solid clip size 6,4 font "Times-Roman,34"

set bmargin 4
set lmargin 6
set rmargin 2
set tmargin 2.2

#set xrange [0:24.4]
set yrange [0:1]

set xtics scale 0
set ytics 0,0.1,1

set grid noxtics ytics
#set style fill border lc rgb "black"

set ylabel "CDF" offset 1.8,0
set xlabel "Execution Time (s)" offset 0,-0.1

#set label "2GB" at 0.225,-0.4 center

set key outside vertical bottom center maxrows 1
set key samplen 1 at 0.225,1.1 center
set key font "Times-Roman,34"

plot "exectimes.txt" using 1:2 with lines title "Base" lw 8 lc rgb "gray30",\
  "" using 3:4 with lines title "Fork" lw 8 lc rgb "dark-goldenrod",\
  "" using 5:6 with lines title "GH" lw 8 lc rgb "light-green",\
  "" using 7:8 with lines title "Rewind" lw 8 lc rgb "royalblue"
  
