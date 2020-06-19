# Calculate Rescue Patterns

Search and Rescue operations use defined patterns to systematically cover
areas where to find somebody or something.

The script 'pattern.py' outputs data for the the Ladder, Square, and
Sector. They can be piped into other wellknown tools for analysis and
display.

## Ladder
```
 python pattern.py -p ladder>ladder.gp|gnuplot -persist ladder.gp
```

./pattern.py -p square -o 90 -w 100 -l 100 -s 10|tee pattern.dat 
cat pattern.dat |gnuplot -persist pattern.gp

cat pattern.dat |grep "^@"|awk '{print $5,$6}'|gpsbabel -i csv -o gpx -f - -F -

## Square
```
 python pattern.py -p square>pattern.dat|gnuplot -persist pattern.gp
```

./pattern.py -p square -o 90 -w 100 -l 100 -s 10|tee pattern.dat 
cat pattern.dat |gnuplot -persist pattern.gp

cat pattern.dat |grep "^@"|awk '{print $5,$6}'|gpsbabel -i csv -o gpx -f - -F -

## Sector
```
 python pattern.py -p square>pattern.dat|gnuplot -persist pattern.gp
```
