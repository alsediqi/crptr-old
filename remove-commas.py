#This model is to remove comma to prevent None key value error after corrupting data
#Error occurs because attributes my contains "," and write to csv use "," as delimiter
#input file name - output file name - character to replace by
#todo.fix this to new function and add them all to new model that do necessary work to make GeCo run on all kinds of data

import csv
rec = []

dataset_file = csv.DictReader(open('input-files/birth-geco-id-exp25.csv'))
dataset = list(dataset_file)

for d in dataset:
    for key, value in d.iteritems():
        if "," in d[key]:
            d[key] = d[key].replace(",", "-")
            print d[key]

fieldnames = dataset[0].keys()
csvfile = open('input-files/birth-geco-id-exp25-comma-fix.csv','wb')
csvwriter = csv.DictWriter(csvfile, delimiter=',', fieldnames=fieldnames)
csvwriter.writerow(dict((fn,fn) for fn in fieldnames))
for r in dataset:
    csvwriter.writerow(r)
csvfile.close()
print "Commas removed and replaced by hyphens..."
