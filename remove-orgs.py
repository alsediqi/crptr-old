import csv
rec = []

dataset_file = csv.DictReader(open('output-files/birth-crpt-dev.csv'))
dataset = list(dataset_file)
dataset_len = str(len(dataset))
for i in dataset:
    if None in i:
        print i
for r in dataset:
    if "dup" in r['rec-id']:
        rec, recid, dup, dupid = r['rec-id'].split('-')
        org_of_dup = rec + "-" + recid + "-org"
        dup_rec_id = rec + "-" + recid + "-d-" + dupid
        print dup_rec_id
        if r['crptr-record'] == 'duplicate':
            r['rec-id'] = dup_rec_id
            print r
        elif r['crptr-record'] == 'missing':
            dataset.remove(r)
        else:
            dataset.remove(r)

fieldnames = dataset[0].keys()
csvfile = open('output-files/birth-crpt-dev-no-org.csv','wb')
csvwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for r in dataset:
    csvwriter.writerow(r)
csvfile.close()
print "Duplicate corruptions handled..."
print "All originals removed..."
print "Original dataset total records count is " + dataset_len
print "New dataset count is " + str(len(dataset))
print "New CSV file saved in " + str(csvfile)