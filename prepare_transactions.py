# -*- coding: utf-8 -*-
import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import xlsxwriter
import vq_help

DATADIR = "C:/Projects/code/fp-growth/datafiles"
DATAFILE = "query_result_fixedEOF.csv"
TRANSFILE = "transactions.csv"
INDEXFILE = "fp-growth_results_del.txt"
RESULTSFILE = "results.xlsx"

def calc_jaccard(transfile, p_sets):

    jaccards = []
    items = {}
    print('Calculating Jaccard score...')
    
    with open(transfile, "r") as t_file:
        t_reader = csv.reader(t_file, delimiter=',')
        full_set = set([25, 50, 75])        
        
        for line in t_reader:
            curr_set = set(line)
            if len(curr_set) < 2:
                continue
            best_jaccard = 0
            # update progress
            curr_progress = set([round(len(jaccards)/1750)])
            if full_set.difference(curr_progress) != full_set:
                print('Done {0} %'.format(round(len(jaccards)/1750)))
                full_set = full_set.difference(curr_progress)
            #----------------
            for p_set in p_sets:
                    inner_set = curr_set.intersection(p_set)
                    curr_jaccard = float(len(inner_set)) / (len(curr_set) + len(p_set) - len(inner_set))
                    if curr_jaccard > best_jaccard:
                        best_jaccard = curr_jaccard
            
            items[curr_set.__str__().strip('{}')] = best_jaccard
                
            jaccards.append(best_jaccard)
            #print("{} : {}".format(curr_set, best_jaccard))
    print('Done for {0} transactions.'.format(len(jaccards)))
    return jaccards, items
    
def calc_distr(jaccards):
    dist = list(range(11))
    dist[0:11] = [0 for i in range(11)]
    print('Calculating distribution...')
    for score in jaccards:
        try:        
            idx = round(score*10)
            dist[idx] += 1
        except IndexError as e:
            print(e, idx)
    print('Done!')
    return dist

def save_to_xls(dist, patterns, s_val, n_chart):

    from numpy import arange

    global workbook
    worksheet = workbook.add_worksheet('Sheet{0}'.format(n_chart))
    bold = workbook.add_format({'bold': 1})
    
    # Add the worksheet data that the charts will refer to.
    headings = ['Jaccard Score', 'Data']
    print('Writing results to Sheet{0}'.format(n_chart))
    x_val = arange(0, 1.1, 0.1)
    y_val = dist
   
    worksheet.write_row('A1', headings, bold)
    worksheet.write_column('A2', x_val)
    worksheet.write_column('B2', y_val)
    
    #######################################################################
    #
    # Create a new bar chart.
    #
    chart1 = workbook.add_chart({'type': 'column'})
    
    # Configure the first series.
    chart1.add_series({
        'name':       '=Sheet{0}!$B$1'.format(n_chart),
        'categories': '=Sheet{0}!$A$2:$A$12'.format(n_chart),
        'values':     '=Sheet{0}!$B$2:$B$12'.format(n_chart),
    })

#    chart1.add_series({
#        'name':       ['Sheet1', 0, n_chart],
#        'categories': ['Sheet1', 1, 0, 12, 0],
#        'values':     ['Sheet1', 1, n_chart, 12, n_chart],
#    })
    
    # Add a chart title and some axis labels.
    chart1.set_title ({'name': 'Transactions support: {0}, # of patterns: {1}'.format(s_val, patterns)})
    chart1.set_x_axis({'name': 'Jaccard score'})
    chart1.set_y_axis({'name': 'Number of transactions'})
    
    # Set an Excel chart style.
    chart1.set_style(11)
    
    # Insert the chart into the worksheet (with an offset).
    worksheet.insert_chart('D2', chart1, {'x_offset': 25, 'y_offset': 10})    

def match_patterns(items, p_sets):
    s = pd.Series(items)
    s = s[s < 1.0]
    s = s[s >= 0.85]
    s.sort(kind='mergesort', ascending=True)
    print("Printing top 5 transactions:")    
    for i in range(10):
        curr_set = set(s.index[i].replace("'", "").replace(" ", "").split(","))
        print(curr_set, s[i])
        print('-------------------------')
        jaccards = {}
        for p_set in p_sets:
            inner_set = curr_set.intersection(p_set)
            curr_jaccard = float(len(inner_set)) / (len(curr_set) + len(p_set) - len(inner_set))
            jaccards[p_set.__str__().strip('{}')] = curr_jaccard
        patterns = pd.Series(jaccards)
        patterns.sort(kind='quicksort', ascending=False)
        print(patterns[0:5])
        print('=========================')
    
def do_all(s_val, n_chart):
#    old way to display data
#    run(s_val)
#    prob, p_val = calc()
#    display(s_val, int(prob*100), p_val, n_chart)

    run(s_val)
    indexfile = os.path.join(DATADIR, INDEXFILE)
    transfile = os.path.join(DATADIR, TRANSFILE)
    p = patterns_as_sets(indexfile)
    j, items = calc_jaccard(transfile, p)
    d = calc_distr(j)
    save_to_xls(d, len(p), s_val, n_chart)
    match_patterns(items, p)

#main
#prepare() #transposing transactions - one time job

s_array = [2000]
resultsfile = os.path.join(DATADIR, RESULTSFILE)
workbook = xlsxwriter.Workbook(resultsfile)

for i, s_val in enumerate(s_array):
    do_all(s_val, i)

workbook.close()