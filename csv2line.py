#!/usr/bin/python
import sys, getopt
import progressbar
import time
import pandas as pd
import datetime

def main(argv):
   dbname = 'import'
   inputfile = 'data.csv'
   outputfile = 'import.txt'

   usage = 'csv2line.py -d <dbname> -i <inputfile> -o <outputfile>'
   try:
      opts, args = getopt.getopt(argv,"hd:i:o:",["db=","ifile=","ofile="])
   except getopt.GetoptError:
      print (usage)
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print (usage)
         sys.exit()
      elif opt in ("-d", "--db"):
         dbname = arg.replace(" ", "_")
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg

   convert(dbname, inputfile, outputfile)


def convert(dbname, inputfile, outputfile):
  # Convert csv's to line protocol
  '''
  https://docs.influxdata.com/influxdb/v1.6/write_protocols/line_protocol_tutorial/
  weather,location=us-midwest temperature=82 1465839830100400200
    |    -------------------- --------------  |
    |             |             |             |
    |             |             |             |
  +-----------+--------+-+---------+-+---------+
  |measurement|,tag_set| |field_set| |timestamp|
  +-----------+--------+-+---------+-+---------+
  '''
  start_time = time.time()
  
  # Read csv
  bar = progressbar.ProgressBar(maxval=100, widgets=[progressbar.Bar('=', '[', ']'), 'Read csv file ', progressbar.Percentage()])
  bar.start()
  df_full = pd.read_csv(inputfile)
  bar.finish()

  # Export to file
  theImportFile = open(outputfile, 'w')
  # Write header file
  theImportFile.write('''
# DDL
CREATE DATABASE %s

# DML
# CONTEXT-DATABASE: %s

''' % (dbname, dbname))

  # Measurement
  bar = progressbar.ProgressBar(maxval=len(df_full), widgets=[progressbar.Bar('=', '[', ']'), 'Processing ', progressbar.Percentage()])
  bar.start()

  seen = {}
  for d in range(len(df_full)):
    bar.update(d+1)
    item = "transaction" \
           + ",brand=%s" % str(df_full["brand"][d]).replace(" ", "_") \
           + ",user_gender=%s" % str(df_full["user_gender"][d]).replace(" ", "_") \
           + " " \
           + "model=\"%s\"" % str(df_full["model"][d]) \
           + ",area=\"%s\"" % str(df_full["area"][d]) \
           + ",user_name=\"%s\"" % str(df_full["user_name"][d]) \
           + ",quantity=%s" % str(df_full["quantity"][d]) \
           + ",store=%s" % str(df_full["store"][d]) \
           + ",price=%s" % str(df_full["price"][d]) \
           + ",user_age=%s" % str(df_full["user_age"][d]) \
           + " " \
           + str(int(datetime.datetime.strptime(df_full["time"][d], "%Y-%m-%d %H:%M:%S").timestamp())*1000000000)
           # + str(df_full["time"][d])

    if item in seen: continue
    theImportFile.write("%s\n" % item)
    seen[item] = 1

  bar.finish()

  # Print log
  print ('---Converting finished !!! (%s seconds)---' % (time.time() - start_time))
  print ('\t-Dabase name is: %s' % dbname)
  print ('\t-Input file is: %s' % inputfile)
  print ('\t-Output file is: %s' % outputfile)

if __name__ == "__main__":
   main(sys.argv[1:])

