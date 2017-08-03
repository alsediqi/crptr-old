import csv
rec = []

dataset_file = csv.DictReader(open('output-files/birth-crpt-dev-no-org.csv'))
dataset = list(dataset_file)
dataset_len = str(len(dataset))
for i in dataset:
    if None in i:
        print i
for r in dataset:
    del r['rec-id']
    del r['crptr-record']
            
fieldnames = dataset[0].keys()
csvfile = open('output-files/birth-crpt-dev-no-org-clear.csv','wb')
csvwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for r in dataset:
    csvwriter.writerow(r)
csvfile.close()
print "records IDs and notes removed..."
print "Original dataset total records count is " + dataset_len
print "New dataset count is " + str(len(dataset))
print "New CSV file saved in " + str(csvfile)