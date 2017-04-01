import csv
rec = []

dataset_file = csv.DictReader(open('input-files/birth-10k.csv'))
dataset = list(dataset_file)
count = 0
for r in dataset:
    r["rec-id"] = "rec-"+ str(count) + "-org"
    count = count+1

fieldnames = dataset[0].keys()
csvfile = open('input-files/birth-geco-id.csv','wb')
csvwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for r in dataset:
    csvwriter.writerow(r)
csvfile.close()
print "GeCo IDs added..."
print "New CSV file saved"
