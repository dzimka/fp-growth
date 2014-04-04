1. First you need to preprocess the query_results file with the Python script (tested with Python 3.3).

2. Next you need to run the program to identify frequent item sets:

-s parameter is the minimal support in percent, so -s1 means 1%
-f parameter is fields delimeter

See example:

fpgrowth -s-1000 -f"," datafiles/transactions.csv datafiles/fp-growth_results.txt

fpgrowth -s-1000 -f"," -k, -v" - %i|%a" datafiles/transactions.csv datafiles/fp-growth_results_del.txt

More details are here

http://www.borgelt.net//doc/fpgrowth/fpgrowth.html
