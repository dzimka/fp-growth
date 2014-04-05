# -*- coding: utf-8 -*-
import os
import csv
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import xlsxwriter
import vq_help.helpers as hlp

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
    headings = ['Jaccard Score', '# of transactions']
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
    worksheet.insert_chart('G1', chart1, {'x_offset': 25, 'y_offset': 10})
    
    return worksheet

def save_data_to_xls(worksheet, curr_set, curr_support, df_top, row):

    print('Writing sample transactions to Excel...')

    global workbook
    bold = workbook.add_format({'bold': 1})
    
    # Add the worksheet data that the charts will refer to.
    headings = ['Transaction', 'Jaccard Idx', 'Support']
  
    worksheet.write_row('D1', headings, bold)
    worksheet.write_row('D{0}'.format(row), [curr_set.__str__().strip('{}'), curr_support], bold)
    row += 1
    for i in range(len(df_top)):
#        print(df_top.index[i])
        worksheet.write_row('D{0}'.format(row), [df_top.index[i], round(df_top['jaccard'][i], 2), df_top['support'][i]])
        row += 1
    return row

def match_patterns(worksheet, items, p_sets, p_scores):
    row = 2
    s = pd.Series(items)
    s = s[s <= 1.0]
    s = s[s >= 0.5]
    if len(s) == 0:
        print("Zero elements! Nothing to display...")
        return False
    s.sort(kind='mergesort', ascending=False)
    print("Printing top 10 transactions:")    
    for i in range(10):
        curr_set = set(s.index[i].replace("'", "").replace(" ", "").split(","))
        print(curr_set, s[i])
        print('-------------------------')
        jaccards = {}
        supports = {}
        for p_set, p_score in itertools.zip_longest(p_sets, p_scores):
            inner_set = curr_set.intersection(p_set)
            curr_jaccard = float(len(inner_set)) / (len(curr_set) + len(p_set) - len(inner_set))
            if curr_jaccard > 0:            
                jaccards[p_set.__str__().strip('{}')] = curr_jaccard
                supports[p_set.__str__().strip('{}')] = p_score
        data = {'jaccard': jaccards, 'support' : supports}
        df = pd.DataFrame(data)
        df.sort('jaccard', ascending=False, inplace=True)
        print(df[:][0:10])
        print('=========================')
        row = save_data_to_xls(worksheet, curr_set, s[i], df[:][0:10], row)
    
def do_all(s_val, n_chart):
#    old way to display data
#    run(s_val)
#    prob, p_val = calc()
#    display(s_val, int(prob*100), p_val, n_chart)

    hlp.run(s_val)
    indexfile = os.path.join(DATADIR, INDEXFILE)
    transfile = os.path.join(DATADIR, TRANSFILE)
    p_sets, p_scores = hlp.patterns_as_sets(indexfile)
    j, items = calc_jaccard(transfile, p_sets)
    d = calc_distr(j)
    ws = save_to_xls(d, len(p_sets), s_val, n_chart)
    match_patterns(ws, items, p_sets, p_scores)

#main block
#prepare() #transposing transactions - one time job

s_array = [30000]
resultsfile = os.path.join(DATADIR, RESULTSFILE)
workbook = xlsxwriter.Workbook(resultsfile)

for i, s_val in enumerate(s_array):
    do_all(s_val, i)

workbook.close()