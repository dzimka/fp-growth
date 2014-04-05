# -*- coding: utf-8 -*-
import os
import csv
from subprocess import call
import pandas as pd
import numpy

s = pd.Series(0, index=['420', '270', '300', '320', '430', '480', '920', '731', '258', '490', '272', '636', '260', '250', '450', '510', '940', '340', '402', '921', '730', '120', '410', '352', '440', '350', '206', '360', '307', '305', '301', '999', '370', '312', '310', '995', '710', '637', '351', '271', '391', '390', '657', '552', '750', '762', '761', '572', '560', '324', '00', '403', '302', '311', '942', '280', '610', '650', '551', '361', '611', '571', '306', '335', '421', '655', '732', '333', '401', '656', '110', '720', '723', '470', '171', '460', '652', '901', '612', '740', '431', '722', '943', '917', '278', 'MISCBILL', '276', '329', '482', '331', '489', '481', '274', '200', '800', '540', '321', '322', '441', '770', '128', '922', '275', '471', '404', '483', '424', '434', '122', '990', '771', '174', '343', '341', '172', '309', '682', '801', '170', '444', '615', '173', '683', '123', '949', '821', '323', '516', '616', '342', '618', '180', '344', '623', '456', '111', '214', '689', '614', '112', '780', '948', '635', '760', '802', '621', '114', '204', '240', '259', '359', '255', '249', '622', '210', '191', '451', '164', '721', '254', '369', '681', '419', '941', '129', '273', '569', '115', '113'])
#s = None
#fig, axes = plt.subplots(nrows=len(s_array), ncols=1, figsize=(10, 7))

def parse_file(datafile):
    print("Loading file %s to pandas data frame." % DATAFILE)    
    df = pd.read_csv(datafile, encoding='utf-8-sig', dtype={'ub92_revenue_code':str}) #, nrows=100)
    trim_zeros = df['ub92_revenue_code'].str.startswith('0')
    trim_zeros = trim_zeros.fillna(False)
    df['ub92_revenue_code'][trim_zeros] = df['ub92_revenue_code'][trim_zeros].str.slice(1,5)
    global s
    s = pd.Series(0, index=df['ub92_revenue_code'].unique())
    return df

def save_transactions(outfile, df):

    print("Iterating through groups and saving transactions to %s." % TRANSFILE)
    lines_counter = 0   # number of lines read
    trans_counter = 0   # number of transactions written

    with open(outfile,'w') as out_f:
        writer = csv.writer(out_f, delimiter=',', quoting=csv.QUOTE_NONE)    
        # iterate through groups and combine codes into transactions
        for name, group in df.groupby(['"facility_code"', 'account_number']):#, 'service_date']):
            data = []
            # data.append(name)
            for i in group['ub92_revenue_code']:
                data.append(i)
                lines_counter += 1
            writer.writerow(data)
            trans_counter += 1

    print("Finished processing %s lines from the native file." % lines_counter)
    print("Written %s transactions to the transactions file." % trans_counter)

def calc_probability(indexfile, transfile):

    print("Building index from %s file." % indexfile)
    df = pd.read_csv(indexfile, header=None, sep="|", index_col=0)
    
    print("Reading file %s and searching the index..." % transfile)
    with open(transfile, "r") as t_file:

        t_reader = csv.reader(t_file, delimiter="|")

        cnt_found = 0
        cnt_lines = 0
        cnt_empty = 0
        global s        
        s[:] = 0
        
        for line in t_reader:
#            if t_reader.line_num > 100:
#                break   #reading 100 first lines for test purpose
            try:            
                if (len(line) > 0):
                    cnt_lines += 1
                    if (df.ix[line[0]][1] > 0) and (df.ix[line[0]][2] > 1):
                        #print("Found pattern {0} with support {1}".format(line[0], df.ix[line[0]][1]))
                        cnt_found += 1
                        for field in line[0].split(','):
                            s[field] += 1
                else:
                    cnt_empty += 1
                    
            except KeyError as e:
                #print("Pattern %s is not found." % e)
                pass
                
        prob = cnt_found / (cnt_lines)
#        print("Skipped {0} empty lines.".format(cnt_empty))                
#        print("Processed {0} lines (reader).".format(t_reader.line_num-1))        
        print("Processed {0} lines.\nFor {1} transactions the frequent pattern was found.\nCalculated probability is {2}.".format(cnt_lines, cnt_found, prob))
    return prob, df[1].count()

def patterns_as_sets(indexfile):
    
    with open(indexfile, "r") as i_file:
        i_reader = csv.reader(i_file, delimiter="|")

        p_sets = []
        p_scores = []        
        p_set = set()
        
        for line in i_reader:
            p_set = set(line[0].split(','))
            p_score = int(line[1])
            if len(p_set) < 2:
                continue
            p_sets.append(p_set)
            p_scores.append(p_score)
    return [p_sets, p_scores]

def prepare():

    datafile = os.path.join(DATADIR, DATAFILE)
    outfile = os.path.join(DATADIR, TRANSFILE)

    df = parse_file(datafile)
    print(df.count())
    print(df['ub92_revenue_code'].unique())
    save_transactions(outfile, df)

def run(s_val):
    print("Running fp-growth...")
    cmd_line = 'fpgrowth -s-{0} -f"," -k, -v"|%a|%i" datafiles/transactions.csv datafiles/fp-growth_results_del.txt'.format(s_val)
    retcode = call(cmd_line, shell=True)
    print("Completed with code {0}.".format(retcode))
