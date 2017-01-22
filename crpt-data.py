# generate-data-english.py - Python module to generate synthetic data based on
#                            English look-up and error tables.
#
# Peter Christen and Dinusha Vatsalan, January-March 2012
# =============================================================================
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# =============================================================================

# Import the necessary other modules of the data generator
#
import csv
import sys
import basefunctions  # Helper functions
#import corruptor      # Main classes to corrupt attribute values and records
import positionfunctions
import crptr
import corruptvalue
import random

rec_dict = {}
with open("input-files/birth-geco-id.csv","r") as f:
    dataset = csv.reader(f, delimiter=",")
    for row in dataset:
        if not row[0] in rec_dict:
            rec_dict[row[0]]=[]
        for value in row[1:]:
            #print row[1:]
            #print value
            rec_dict[row[0]].append(value)


random.seed(42)  # Set seed for random generator, so data generation can be
                 # repeated

# Set the Unicode encoding for this data generation project. This needs to be
# changed to another encoding for different Unicode character sets.
# Valid encoding strings are listed here:
# http://docs.python.org/library/codecs.html#standard-encodings
#
unicode_encoding_used = 'ascii'

# The name of the record identifier attribute (unique value for each record).
# This name cannot be given as name to any other attribute that is generated.
#
rec_id_attr_name = 'rec-id'
header_list = [rec_id_attr_name]+rec_dict[rec_id_attr_name]
del rec_dict["rec-id"]

# Set the file name of the data set to be generated (this will be a comma
# separated values, CSV, file).
#
output_file_name = 'output-files/birth_crpt_no_mspl.csv'

# Set how many original and how many duplicate records are to be generated.
#
num_org_rec = len(rec_dict)
num_dup_rec = 4000

# Set the maximum number of duplicate records can be generated per original
# record.
#
max_duplicate_per_record = 1

# Set the probability distribution used to create the duplicate records for one
# original record (possible values are: 'uniform', 'poisson', 'zipf').
#
num_duplicates_distribution = 'zipf'

# Set the maximum number of modification that can be applied to a single
# attribute (field).
#
max_modification_per_attr = 1

# Set the number of modification that are to be applied to a record.
#
num_modification_per_record = 5

# Check if the given the unicode encoding selected is valid.
#
basefunctions.check_unicode_encoding_exists(unicode_encoding_used)

# -----------------------------------------------------------------------------
# Define how the generated records are to be corrupted (using methods from
# the corruptor.py module).

# For a value edit corruptor, the sum or the four probabilities given must
# be 1.0.
#
edit_corruptor = \
    corruptvalue.CorruptValueEdit(\
          position_function = positionfunctions.position_mod_normal,
          char_set_funct = basefunctions.char_set_ascii,
          insert_prob = 0.5,
          delete_prob = 0.5,
          substitute_prob = 0.0,
          transpose_prob = 0.0)

edit_corruptor2 = \
    corruptvalue.CorruptValueEdit(\
          position_function = positionfunctions.position_mod_uniform,
          char_set_funct = basefunctions.char_set_ascii,
          insert_prob = 0.25,
          delete_prob = 0.25,
          substitute_prob = 0.25,
          transpose_prob = 0.25)

surname_misspell_corruptor = \
    corruptvalue.CorruptCategoricalValue(\
          lookup_file_name = 'lookup-files/surname-misspell.csv',
          has_header_line = False,
          unicode_encoding = unicode_encoding_used)

ocr_corruptor = corruptvalue.CorruptValueOCR(\
          position_function = positionfunctions.position_mod_normal,
          lookup_file_name = 'lookup-files/ocr-variations.csv',
          has_header_line = False,
          unicode_encoding = unicode_encoding_used)

keyboard_corruptor = corruptvalue.CorruptValueKeyboard(\
          position_function = positionfunctions.position_mod_normal,
          row_prob = 0.5,
          col_prob = 0.5)

phonetic_corruptor = corruptvalue.CorruptValuePhonetic(\
          lookup_file_name = 'lookup-files/phonetic-variations.csv',
          has_header_line = False,
          unicode_encoding = unicode_encoding_used)

missing_val_corruptor = corruptvalue.CorruptMissingValue()

postcode_missing_val_corruptor = corruptvalue.CorruptMissingValue(\
       missing_val='missing')

given_name_missing_val_corruptor = corruptvalue.CorruptMissingValue(\
       missing_value='unknown')

# -----------------------------------------------------------------------------
# Define the attributes to be generated for this data set, and the data set
# itself.
#
attr_name_list = ['FirstName', 'LastName','Gender','DateofBirth','FatherFirstName','FatherLastName', 'FatherOccupation',	'MotherFirstName', 'MotherLastName', 'MotherOccupation']

#attr_name_list = ['gender', 'given-name', 'surname', 'postcode', 'city',
#                  'telephone-number', 'credit-card-number', 'income-normal',
#                  'age-uniform', 'income', 'age', 'sex', 'blood-pressure']



# Define the probability distribution of how likely an attribute will be
# selected for a modification.
# Each of the given probability values must be between 0 and 1, and the sum of
# them must be 1.0.
# If a probability is set to 0 for a certain attribute, then no modification
# will be applied on this attribute.
#

attr_mod_prob_dictionary = {'FirstName': 0.5, 'LastName':0.5, 'Gender': 0.0,'DateofBirth': 0.0,
                            'FatherFirstName': 0.0,'FatherLastName': 0.0, 'FatherOccupation': 0.0,
                            'MotherFirstName': 0.0, 'MotherLastName': 0.0, 'MotherOccupation':0.0}


#attr_mod_prob_dictionary = {'gender':0.1, 'given-name':0.2,'surname':0.2,
#                            'postcode':0.1,'city':0.1, 'telephone-number':0.15,
#                            'credit-card-number':0.1,'age':0.05}

# Define the actual corruption (modification) methods that will be applied on
# the different attributes.
# For each attribute, the sum of probabilities given must sum to 1.0.
#
attr_mod_data_dictionary = {'LastName':[(0.0, surname_misspell_corruptor),
                                       (0.5, ocr_corruptor),
                                       (0.5, keyboard_corruptor)],
                            'FirstName':[(0.4, edit_corruptor2),
                                          (0.2, ocr_corruptor),
                                          (0.4, keyboard_corruptor)]}

# Nothing to change here - set-up the data set corruption object
#
test_data_corruptor = crptr.CorruptDataSet(number_of_org_records = \
                                          num_org_rec,
                                          number_of_mod_records = num_dup_rec,
                                          attribute_name_list = attr_name_list,
                                          max_num_dup_per_rec = \
                                                 max_duplicate_per_record,
                                          num_dup_dist = \
                                                 num_duplicates_distribution,
                                          max_num_mod_per_attr = \
                                                 max_modification_per_attr,
                                          num_mod_per_rec = \
                                                 num_modification_per_record,
                                          attr_mod_prob_dict = \
                                                 attr_mod_prob_dictionary,
                                          attr_mod_data_dict = \
                                                 attr_mod_data_dictionary)

# =============================================================================
# No need to change anything below here

# Start the data generation process
#

assert len(rec_dict) == num_org_rec  # Check the number of generated records

# Corrupt (modify) the original records into duplicate records
#


rec_dict = test_data_corruptor.corrupt_records(rec_dict)
print rec_dict
print len(rec_dict)
assert len(rec_dict) == num_org_rec+num_dup_rec # Check total number of records

#Inject any CSV Here (rec_dict is the dataset handler)
#Records must have the same IDs format [rec-000-org]
'''
print "+++++++++++++++++++++++++++++++"
for i in rec_dict:
	print i, rec_dict[i]
print len(rec_dict)
print "+++++++++++++++++++++++++++++++"
'''

rec_id_list = rec_dict.keys()
rec_id_list.sort()

# Convert record dictionary into a list, with record identifier added
#
rec_list = []

for rec_id in rec_id_list:
    this_rec_list = [rec_id]+rec_dict[rec_id]
    rec_list.append(this_rec_list)
    #print this_rec_list

#header_list = [rec_id_attr_name]+rec_dict[rec_id_attr_name]
print header_list
basefunctions.write_csv_file(output_file_name, unicode_encoding_used, header_list, rec_list)

'''
with open('crptd-test.csv', 'wb') as f:
    writer = csv.writer(f, delimiter=',')
    for row in rec_dict.iteritems():
        print row
        writer.writerow(row)
'''
# Write generate data into a file
#
#test_data_corruptor.write()

# End.
# =============================================================================
