import csv
rec = []

dataset_file = csv.DictReader(open('output-files/birth-crpt-exp25.csv'))
dataset = list(dataset_file)
dataset_len = str(len(dataset))
for i in dataset:
    if None in i:
        print i
for r in dataset:
    if "dup" in r['rec-id']:
        rec, recid, dup, dupid = r['rec-id'].split('-')
        org_of_dup = rec + "-" + recid + "-org"
        #print org_of_dup
        for i in dataset:
            if i['rec-id'] == org_of_dup:
                dataset.remove(i)

fieldnames = dataset[0].keys()
csvfile = open('output-files/birth-cprt-exp25-no-org.csv','wb')
csvwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for r in dataset:
    csvwriter.writerow(r)
csvfile.close()

print "All originals of duplicates removed..."
print "Original dataset total records count is " + dataset_len
print "New dataset count is " + str(len(dataset))
print "New CSV file saved in " + str(csvfile)