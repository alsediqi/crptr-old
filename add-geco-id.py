import csv
rec = []

dataset_file = csv.DictReader(open('input-files/birth-dev.csv'))
dataset = list(dataset_file)
count = 0
for r in dataset:
    r["rec-id"] = "rec-"+ str(count) + "-org"
    count = count+1
    r["crptr-record"] = "original"

fieldnames = dataset[0].keys()
csvfile = open('input-files/birth-dev-rec.csv','wb')
csvwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for r in dataset:
    csvwriter.writerow(r)
csvfile.close()
print "GeCo IDs added..."
print "Attribute (column) to handle whole record level corruptions added..."
print "New CSV file saved"
