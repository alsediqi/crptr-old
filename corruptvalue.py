# -----------------------------------------------------------------------------
# Import necessary modules

import math
import random
import basefunctions
import positionfunctions
# =============================================================================
# Classes for corrupting a value in a single attribute (field) of the data set
# =============================================================================

class CorruptValue:
  """Base class for the definition of corruptor that is applied on a single
     attribute (field) in the data set.

     This class and all of its derived classes provide methods that allow the
     definition of how values in a single attribute are corrupted (modified)
     and the parameters necessary for the corruption process.

     The following variables need to be set when a CorruptValue instance is
     initialised (with further parameters listed in the derived classes):

     position_function  A function that (somehow) determines the location
                        within a string value of where a modification
                        (corruption) is to be applied. The input of this
                        function is assumed to be a string and its return value
                        an integer number in the range of the length of the
                        given input string.
  """

  # ---------------------------------------------------------------------------
#AHMAD# in the initiation (__init__) arguments inserted are checked, valedated and procssed to be used
  def __init__(self, base_kwargs):
    """Constructor, set general attributes.
    """

    # General attributes for all attribute corruptors.
    #
    self.position_function = None

    # Process the keyword argument (all keywords specific to a certain data
    # generator type were processed in the derived class constructor)
    #
    for (keyword, value) in base_kwargs.items():
#AHMAD#This is checking from calls in generate-data-english.py file
#AHMAD# 'position' realted to the inserted argument in the file config and same to others
      if (keyword.startswith('position')):
        basefunctions.check_is_function_or_method('position_function', value)
        #AHMAD# setting position to the given value in the file
        #-----# in this case one of the functions (position_mod_normal or position_mod_uniform)
        self.position_function = value

      else:
        raise Exception, 'Illegal constructor argument keyword: "%s"' % \
              (str(keyword))

    basefunctions.check_is_function_or_method('position_function',
                                              self.position_function)

    # Check if the position function does return an integer value
    #
    pos = self.position_function('test')
    if ((not isinstance(pos, int)) or (pos < 0) or (pos > 3)):
      raise Exception, 'Position function returns an illegal value (either' + \
                       'not an integer or and integer out of range: %s' % \
                       (str(pos))

  # ---------------------------------------------------------------------------

  def corrupt_value(self, str):
    """Method which corrupts the given input string and returns the modified
       string.
       See implementations in derived classes for details.
    """

    raise Exception, 'Override abstract method in derived class'

# =============================================================================

class CorruptMissingValue(CorruptValue):
  """A corruptor method which simply sets an attribute value to a missing
     value.

     The additional argument (besides the base class argument
     'position_function') that has to be set when this attribute type is
     initialised are:

     missing_val  The string which designates a missing value. Default value
                  is the empty string ''.

     Note that the 'position_function' is not required by this corruptor
     method.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.missing_val = ''
    self.name =        'Missing value'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('miss')):
        basefunctions.check_is_string('missing_val', value)
        self.missing_val = value

      else:
        base_kwargs[keyword] = value

    base_kwargs['position_function'] = dummy_position

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_str):
    """Simply return the missing value string.
    """

    return self.missing_val

# =============================================================================

class CorruptValueEdit(CorruptValue):
  """A simple corruptor which applies one edit operation on the given value.

     Depending upon the content of the value (letters, digits or mixed), if the
     edit operation is an insert or substitution a character from the same set
     (letters, digits or both) is selected.

     The additional arguments (besides the base class argument
     'position_function') that has to be set when this attribute type is
     initialised are:

     char_set_funct   A function which determines the set of characters that
                      can be inserted or used of substitution
     insert_prob      These for values set the likelihood of which edit
     delete_prob      operation will be selected.
     substitute_prob  All four probability values must be between 0 and 1, and
     transpose_prob   the sum of these four values must be 1.0
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.char_set_funct =  None
    self.insert_prob =     None
    self.delete_prob =     None
    self.substitute_prob = None
    self.transpose_prob =  None
    self.name =            'Edit operation'

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('char')):
        basefunctions.check_is_function_or_method('char_set_funct', value)
        self.char_set_funct = value

      elif (keyword.startswith('ins')):
        basefunctions.check_is_normalised('insert_prob', value)
        self.insert_prob = value

      elif (keyword.startswith('del')):
        basefunctions.check_is_normalised('delete_prob', value)
        self.delete_prob = value

      elif (keyword.startswith('sub')):
        basefunctions.check_is_normalised('substitute_prob', value)
        self.substitute_prob = value

      elif (keyword.startswith('tran')):
        basefunctions.check_is_normalised('transpose_prob', value)
        self.transpose_prob = value

      else:
        base_kwargs[keyword] = value

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_function_or_method('char_set_funct',
                                              self.char_set_funct)
    basefunctions.check_is_normalised('insert_prob',     self.insert_prob)
    basefunctions.check_is_normalised('delete_prob',     self.delete_prob)
    basefunctions.check_is_normalised('substitute_prob', self.substitute_prob)
    basefunctions.check_is_normalised('transpose_prob',  self.transpose_prob)

    # Check if the character set function returns a string
    #
    test_str = self.char_set_funct('test')   # This might become a problem
    basefunctions.check_is_string_or_unicode_string('test_str', test_str)

    if (abs((self.insert_prob + self.delete_prob + self.substitute_prob + \
         self.transpose_prob) - 1.0) > 0.0000001):
      raise Exception, 'The four edit probabilities do not sum to 1.0'

    # Calculate the probability ranges for the four edit operations
    #
    self.insert_range =     [0.0,self.insert_prob]
    self.delete_range =     [self.insert_range[1],
                             self.insert_range[1] + self.delete_prob]
    self.substitute_range = [self.delete_range[1],
                             self.delete_range[1] + self.substitute_prob]
    self.transpose_range =  [self.substitute_range[1],
                             self.substitute_range[1] + self.transpose_prob]
    assert self.transpose_range[1] == 1.0

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_str):
    """Method which corrupts the given input string and returns the modified
       string by randomly selecting an edit operation and position in the
       string where to apply this edit.
    """

    if (len(in_str) == 0):  # Empty string, no modification possible
      return in_str

    # Randomly select an edit operation
    #
    r = random.random()

    if (r < self.insert_range[1]):
      edit_op = 'ins'
    elif ((r >= self.delete_range[0]) and (r < self.delete_range[1])):
      edit_op = 'del'
    elif ((r >= self.substitute_range[0]) and (r < self.substitute_range[1])):
      edit_op = 'sub'
    else:
      edit_op = 'tra'

    # Do some checks if only a valid edit operations was selected
    #
    if (edit_op == 'ins'):
      assert self.insert_prob > 0.0
    elif (edit_op == 'del'):
      assert self.delete_prob > 0.0
    elif (edit_op == 'sub'):
      assert self.substitute_prob > 0.0
    else:
      assert self.transpose_prob > 0.0

    # If the input string is empty only insert is possible
    #
    if ((len(in_str) == 0) and (edit_op != 'ins')):
      return in_str  # Return input string without modification

    # If the input string only has one character then transposition is not
    # possible
    #
    if ((len(in_str) == 1) and (edit_op == 'tra')):
      return in_str  # Return input string without modification

    # Position in string where to apply the modification
    #
    # For a transposition we cannot select the last position in the string
    # while for an insert we can specify the position after the last
    if (edit_op == 'tra'):
      len_in_str = in_str[:-1]
    elif (edit_op == 'ins'):
      len_in_str = in_str+'x'
    else:
      len_in_str = in_str
    mod_pos = self.position_function(len_in_str)

    # Get the set of possible characters that can be inserted or substituted
    #
    char_set = self.char_set_funct(in_str)

    if (char_set == ''):  # No possible value change
      return in_str

    if (edit_op == 'ins'):  # Insert a character
      ins_char = random.choice(char_set)
      new_str = in_str[:mod_pos] + ins_char + in_str[mod_pos:]

    elif (edit_op == 'del'):  # Delete a character
      new_str = in_str[:mod_pos] + in_str[mod_pos+1:]

    elif (edit_op == 'sub'):  # Substitute a character
      sub_char = random.choice(char_set)
      new_str = in_str[:mod_pos] + sub_char + in_str[mod_pos+1:]

    else:  # Transpose two characters
      char1 = in_str[mod_pos]
      char2 = in_str[mod_pos+1]
      new_str = in_str[:mod_pos]+char2+char1+in_str[mod_pos+2:]

    return new_str

# =============================================================================

class CorruptValueKeyboard(CorruptValue):
  """Use a keyboard layout to simulate typing errors. They keyboard is
     hard-coded into this method, but can be changed easily for different
     keyboard layout.

     A character from the original input string will be randomly chosen using
     the position function, and then a character from either the same row or
     column in the keyboard will be selected.

     The additional arguments (besides the base class argument
     'position_function') that have to be set when this attribute type is
     initialised are:

     row_prob  The probability that a neighbouring character in the same row
               is selected.

     col_prob  The probability that a neighbouring character in the same
               column is selected.

     The sum of row_prob and col_prob must be 1.0.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.row_prob = None
    self.col_prob = None
    self.name =     'Keybord value'

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('row')):
        basefunctions.check_is_normalised('row_prob', value)
        self.row_prob = value

      elif (keyword.startswith('col')):
        basefunctions.check_is_normalised('col_prob', value)
        self.col_prob = value

      else:
        base_kwargs[keyword] = value

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_normalised('row_prob', self.row_prob)
    basefunctions.check_is_normalised('col_prob', self.col_prob)

    if (abs((self.row_prob + self.col_prob) - 1.0) > 0.0000001):
      raise Exception, 'Sum of row and column probablities does not sum ' + \
                       'to 1.0'

    # Keyboard substitutions gives two dictionaries with the neigbouring keys
    # for all leters both for rows and columns (based on ideas implemented by
    # Mauricio A. Hernandez in his dbgen).
    # This following data structures assume a QWERTY keyboard layout
    #
    self.rows = {'a':'s',  'b':'vn', 'c':'xv', 'd':'sf', 'e':'wr', 'f':'dg',
                 'g':'fh', 'h':'gj', 'i':'uo', 'j':'hk', 'k':'jl', 'l':'k',
                 'm':'n',  'n':'bm', 'o':'ip', 'p':'o',  'q':'w',  'r':'et',
                 's':'ad', 't':'ry', 'u':'yi', 'v':'cb', 'w':'qe', 'x':'zc',
                 'y':'tu', 'z':'x',
                 '1':'2',  '2':'13', '3':'24', '4':'35', '5':'46', '6':'57',
                 '7':'68', '8':'79', '9':'80', '0':'9'}

    self.cols = {'a':'qzw', 'b':'gh',  'c':'df', 'd':'erc','e':'ds34',
                 'f':'rvc', 'g':'tbv', 'h':'ybn', 'i':'k89',  'j':'umn',
                 'k':'im', 'l':'o', 'm':'jk',  'n':'hj',  'o':'l90', 'p':'0',
                 'q':'a12', 'r':'f45', 's':'wxz', 't':'g56',  'u':'j78',
                 'v':'fg', 'w':'s23',  'x':'sd', 'y':'h67',  'z':'as',
                 '1':'q',  '2':'qw', '3':'we', '4':'er', '5':'rt',  '6':'ty',
                 '7':'yu', '8':'ui', '9':'io', '0':'op'}

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_str):
    """Method which corrupts the given input string by replacing a single
       character with a neighbouring character given the defined keyboard
       layout at a position randomly selected by the position function.
    """

    if (len(in_str) == 0):  # Empty string, no modification possible
      return in_str

    max_try = 10  # Maximum number of tries to find a keyboard modification at
                  # a randomly selected position

    done_key_mod = False  # A flag, set to true once a modification is done
    try_num =      0

    mod_str = in_str[:]  # Make a copy of the string which will be modified

    while ((done_key_mod == False) and (try_num < max_try)):

      mod_pos =  self.position_function(mod_str)
      mod_char = mod_str[mod_pos]

      r = random.random()  # Create a random number between 0 and 1

      if (r <= self.row_prob):  # See if there is a row modification
        if (mod_char in self.rows):
          key_mod_chars = self.rows[mod_char]
          done_key_mod =  True

      else:  # See if there is a column modification
        if (mod_char in self.cols):
          key_mod_chars = self.cols[mod_char]
          done_key_mod =  True

      if (done_key_mod == False):
        try_num += 1

    # If a modification is possible do it
    #
    if (done_key_mod == True):

      # Randomly select one of the possible characters
      #
      new_char = random.choice(key_mod_chars)

      mod_str = mod_str[:mod_pos] + new_char + mod_str[mod_pos+1:]

    assert len(mod_str) == len(in_str)

    return mod_str

# =============================================================================

class CorruptValueOCR(CorruptValue):
  """Simulate OCR errors using a list of similar pairs of characters or strings
     that will be applied on the original string values.

     These pairs of characters will be loaded from a look-up file which is a
     CSV file with two columns, the first is a single character or character
     sequence, and the second column is also a single character or character
     sequence. It is assumed that the second value is an OCR modification of
     the first value, and the other way round. For example:

       5,S
       5,s
       2,Z
       2,z
       1,|
       6,G

     It is possible for an 'original' string value (first column) to have
     several variations (second column). In such a case one variation will be
     randomly selected during the value corruption (modification) process.

     The additional arguments (besides the base class argument
     'position_function') that have to be set when this attribute type is
     initialised are:

     lookup_file_name  Name of the file which contains the OCR character
                       variations.

     has_header_line   A flag, set to True or False, that has to be set
                       according to if the look-up file starts with a header
                       line or not.

     unicode_encoding  The Unicode encoding (a string name) of the file.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.lookup_file_name = None
    self.has_header_line =  None
    self.unicode_encoding = None
    self.ocr_val_dict =     {}  # The dictionary to hold the OCR variations
    self.name =             'OCR value'

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('look')):
        basefunctions.check_is_non_empty_string('lookup_file_name', value)
        self.lookup_file_name = value

      elif (keyword.startswith('has')):
        basefunctions.check_is_flag('has_header_line', value)
        self.has_header_line = value

      elif (keyword.startswith('unicode')):
        basefunctions.check_is_non_empty_string('unicode_encoding', value)
        self.unicode_encoding = value

      else:
        base_kwargs[keyword] = value

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_non_empty_string('lookup_file_name',
                                            self.lookup_file_name)
    basefunctions.check_is_flag('has_header_line', self.has_header_line)
    basefunctions.check_is_non_empty_string('unicode_encoding',
                                            self.unicode_encoding)

    # Load the OCR variations lookup file - - - - - - - - - - - - - - - - - - -
    #
    header_list, lookup_file_data = \
                     basefunctions.read_csv_file(self.lookup_file_name,
                                                 self.unicode_encoding,
                                                 self.has_header_line)

    # Process values from file and their frequencies
    #
    for rec_list in lookup_file_data:
      if (len(rec_list) != 2):
        raise Exception, 'Illegal format in OCR variations lookup file ' + \
                         '%s: %s' % (self.lookup_file_name, str(rec_list))
      org_val = rec_list[0].strip()
      var_val = rec_list[1].strip()

      if (org_val == ''):
        raise Exception, 'Empty original OCR value in lookup file %s' % \
                         (self.lookup_file_name)
      if (var_val == ''):
        raise Exception, 'Empty OCR variation value in lookup file %s' % \
                         (self.lookup_file_name)
      if (org_val == var_val):
        raise Exception, 'OCR variation is the same as original value in ' + \
                         'lookup file %s' % (self.lookup_file_name)

      # Now insert the OCR original value and variation twice (with original
      # and variation both as key and value), i.e. swapped
      #
      this_org_val_list = self.ocr_val_dict.get(org_val, [])
      this_org_val_list.append(var_val)
      self.ocr_val_dict[org_val] = this_org_val_list

      this_org_val_list = self.ocr_val_dict.get(var_val, [])
      this_org_val_list.append(org_val)
      self.ocr_val_dict[var_val] = this_org_val_list

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_str):
    """Method which corrupts the given input string by replacing a single
       character or a sequence of characters with an OCR variation at a
       position randomly selected by the position function.

       If there are several OCR variations then one will be randomly chosen.
    """

    if (len(in_str) == 0):  # Empty string, no modification possible
      return in_str

    max_try = 10  # Maximum number of tries to find an OCR modification at a
                  # randomly selected position

    done_ocr_mod = False  # A flag, set to True once a modification is done
    try_num =      0

    mod_str = in_str[:]  # Make a copy of the string which will be modified

    while ((done_ocr_mod == False) and (try_num < max_try)):

      mod_pos = self.position_function(mod_str)

      # Try one to three characters at selected position
      #
      ocr_org_char_set = set([mod_str[mod_pos], mod_str[mod_pos:mod_pos+2], \
                              mod_str[mod_pos:mod_pos+3]])

      mod_options = []  # List of possible modifications that can be applied

      for ocr_org_char in ocr_org_char_set:
        if ocr_org_char in self.ocr_val_dict:
          ocr_var_list = self.ocr_val_dict[ocr_org_char]
          for mod_val in ocr_var_list:
            mod_options.append([ocr_org_char,len(ocr_org_char),mod_val])

      if (mod_options != []):  # Modifications are possible

        # Randomly select one of the possible modifications that can be applied
        #
        mod_to_apply = random.choice(mod_options)
        assert mod_to_apply[0] in self.ocr_val_dict.keys()
        assert mod_to_apply[2] in self.ocr_val_dict.keys()

        mod_str = in_str[:mod_pos] + mod_to_apply[2] + \
                  in_str[mod_pos+mod_to_apply[1]:]

        done_ocr_mod = True

      else:
        try_num += 1

    return mod_str

# =============================================================================

class CorruptValuePhonetic(CorruptValue):
  """Simulate phonetic errors using a list of phonetic rules which are stored
     in a CSV look-up file.

     Each line (row) in the CSV file must consist of seven columns that contain
     the following information:
     1) Where a phonetic modification can be applied. Possible values are:
        'ALL','START','END','MIDDLE'
     2) The original character sequence (i.e. the characters to be replaced)
     3) The new character sequence (which will replace the original sequence)
     4) Precondition: A condition that must occur before the original string
        character sequence in order for this rule to become applicable.
     5) Postcondition: Similarly, a condition that must occur after the
        original string character sequence in order for this rule to become
        applicable.
     6) Pattern existence condition: This condition requires that a certain
        given string character sequence does ('y' flag) or does not ('n' flag)
        occur in the input string.
     7) Start existence condition: Similarly, this condition requires that the
        input string starts with a certain string pattern ('y' flag) or not
        ('n' flag)

     A detailed description of this phonetic data generation is available in

       Accurate Synthetic Generation of Realistic Personal Information
       Peter Christen and Agus Pudjijono
       Proceedings of the Pacific-Asia Conference on Knowledge Discovery and
                          Data Mining (PAKDD), Bangkok, Thailand, April 2009.

     For a given input string, one of the possible phonetic modifications will
     be randomly selected without the use of the position function.

     The additional arguments (besides the base class argument
     'position_function') that have to be set when this attribute type is
     initialised are:

     lookup_file_name  Name of the file which contains the phonetic
                       modification patterns.

     has_header_line   A flag, set to True or False, that has to be set
                       according to if the look-up file starts with a header
                       line or not.

     unicode_encoding  The Unicode encoding (a string name) of the file.

     Note that the 'position_function' is not required by this corruptor
     method.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.lookup_file_name = None
    self.has_header_line =  None
    self.unicode_encoding = None
    self.replace_table =    []
    self.name =             'Phonetic value'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('look')):
        basefunctions.check_is_non_empty_string('lookup_file_name', value)
        self.lookup_file_name = value

      elif (keyword.startswith('has')):
        basefunctions.check_is_flag('has_header_line', value)
        self.has_header_line = value

      elif (keyword.startswith('unicode')):
        basefunctions.check_is_non_empty_string('unicode_encoding', value)
        self.unicode_encoding = value

      else:
        base_kwargs[keyword] = value

    base_kwargs['position_function'] = dummy_position

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_non_empty_string('lookup_file_name',
                                            self.lookup_file_name)
    basefunctions.check_is_flag('has_header_line', self.has_header_line)
    basefunctions.check_is_non_empty_string('unicode_encoding',
                                            self.unicode_encoding)

    # Load the misspelling lookup file - - - - - - - - - - - - - - - - - - - - -
    #
    header_list, lookup_file_data = \
                     basefunctions.read_csv_file(self.lookup_file_name,
                                                 self.unicode_encoding,
                                                 self.has_header_line)

    # Process values from file and misspellings
    #
    for rec_list in lookup_file_data:
      if (len(rec_list) != 7):
        raise Exception, 'Illegal format in phonetic lookup file %s: %s' \
                         % (self.lookup_file_name, str(rec_list))
      val_tuple = ()
      for val in rec_list:
        if (val != ''):
          val = val.strip()
          val_tuple += val,
        else:
          raise Exception, 'Empty value in phonetic lookup file %s" %s' % \
                           (self.lookup_file_name, str(rec_list))
      self.replace_table.append(val_tuple)

  # ---------------------------------------------------------------------------

  def __apply_change__(self, in_str, ch):
    """Helper function which will apply the selected change to the input
       string.

       Developed by Agus Pudjijono, ANU, 2008.
    """

    work_str = in_str
    list_ch = ch.split('>')
    subs = list_ch[1]
    if (list_ch[1] == '@'): # @ is blank
      subs = ''
    tmp_str = work_str
    org_pat_length = len(list_ch[0])
    str_length =     len(work_str)

    if (list_ch[2] == 'end'):
      org_pat_start = work_str.find(list_ch[0], str_length-org_pat_length)
    elif (list_ch[2] == 'middle'):
      org_pat_start = work_str.find(list_ch[0],1)
    else: # Start and all
      org_pat_start = work_str.find(list_ch[0],0)

    if (org_pat_start == 0):
      work_str = subs + work_str[org_pat_length:]
    elif (org_pat_start > 0):
      work_str = work_str[:org_pat_start] + subs + \
                 work_str[org_pat_start+org_pat_length:]

    if (work_str == tmp_str):
      work_str = str_to_change

    return work_str

  # ---------------------------------------------------------------------------

  def __slavo_germanic__(self, in_str):
    """Helper function which determines if the inputstring could contain a
       Slavo or Germanic name.

       Developed by Agus Pudjijono, ANU, 2008.
    """

    if ((in_str.find('w') > -1) or (in_str.find('k') > -1) or \
        (in_str.find('cz') > -1) or (in_str.find('witz') > -1)):
      return 1
    else:
      return 0

  # ---------------------------------------------------------------------------

  def __collect_replacement__(self, s, where, orgpat, newpat, precond,
                              postcond, existcond, startcond):
    """Helper function which collects all the possible phonetic modification
       patterns that are possible on the given input string, and replaces a
       pattern in a string.

       The following arguments are needed:
       - where     Can be one of: 'ALL','START','END','MIDDLE'
       - precond   Pre-condition (default 'None') can be 'V' for vowel or
                   'C' for consonant
       - postcond  Post-condition (default 'None') can be 'V' for vowel or
                   'C' for consonant

       Developed by Agus Pudjijono, ANU, 2008.
    """

    vowels = 'aeiouy'
    tmpstr = s
    changesstr = ''

    start_search = 0  # Position from where to start the search
    pat_len =      len(orgpat)
    stop =         False

    # As long as pattern is in string
    #
    while ((orgpat in tmpstr[start_search:]) and (stop == False)):

      pat_start = tmpstr.find(orgpat, start_search)
      str_len =   len(tmpstr)

      # Check conditions of previous and following character
      #
      OKpre  = False   # Previous character condition
      OKpre1 = False   # Previous character1 condition
      OKpre2 = False   # Previous character2 condition

      OKpost  = False  # Following character condition
      OKpost1 = False  # Following character1 condition
      OKpost2 = False  # Following character2 condition

      OKexist = False  # Existing pattern condition
      OKstart = False  # Existing start pattern condition

      index =  0

      if (precond == 'None'):
        OKpre = True

      elif (pat_start > 0):
        if (((precond == 'V') and (tmpstr[pat_start-1] in vowels)) or \
            ((precond == 'C') and (tmpstr[pat_start-1] not in vowels))):
          OKpre = True

        elif ((precond.find(';')) > -1):
          if (precond.find('|') > -1):
            rls=precond.split('|')
            rl1=rls[0].split(';')

            if (int(rl1[1]) < 0):
              index =  pat_start+int(rl1[1])
            else:
              index =  pat_start+(len(orgpat)-1)+int(rl1[1])

            i=2
            if (rl1[0] == 'n'):
              while (i < (len(rl1))):
                if (tmpstr[index:(index+len(rl1[i]))] == rl1[i]):
                  OKpre1 = False
                  break
                else:
                  OKpre1 = True
                i+=1
            else:
              while (i < (len(rl1))):
                if (tmpstr[index:(index+len(rl1[i]))] == rl1[i]):
                  OKpre1 = True
                  break
                i+=1

            rl2=rls[1].split(';')

            if (int(rl2[1]) < 0):
              index =  pat_start+int(rl2[1])
            else:
              index =  pat_start+(len(orgpat)-1)+int(rl2[1])

            i=2
            if (rl2[0] == 'n'):
              while (i < (len(rl2))):
                if (tmpstr[index:(index+len(rl2[i]))] == rl2[i]):
                  OKpre2 = False
                  break
                else:
                  OKpre2 = True
                i+=1
            else:
              while (i < (len(rl2))):
                if (tmpstr[index:(index+len(rl2[i]))] == rl2[i]):
                  OKpre2 = True
                  break
                i+=1

            OKpre=OKpre1 and OKpre2

          else:
            rl=precond.split(';')
            #-
            if (int(rl[1]) < 0):
              index =  pat_start+int(rl[1])
            else:
              index =  pat_start+(len(orgpat)-1)+int(rl[1])

            i=2
            if (rl[0] == 'n'):
              while (i < (len(rl))):
                if (tmpstr[index:(index+len(rl[i]))] == rl[i]):
                  OKpre = False
                  break
                else:
                  OKpre = True
                i+=1
            else:
              while (i < (len(rl))):
                if (tmpstr[index:(index+len(rl[i]))] == rl[i]):
                  OKpre = True
                  break
                i+=1

      if (postcond == 'None'):
        OKpost = True

      else:
        pat_end = pat_start+pat_len

        if (pat_end < str_len):
          if (((postcond == 'V') and (tmpstr[pat_end] in vowels)) or \
              ((postcond == 'C') and (tmpstr[pat_end] not in vowels))):
            OKpost = True
          elif ((postcond.find(';')) > -1):
            if (postcond.find('|') > -1):
              rls=postcond.split('|')

              rl1=rls[0].split(';')

              if (int(rl1[1]) < 0):
                index =  pat_start+int(rl1[1])
              else:
                index =  pat_start+(len(orgpat)-1)+int(rl1[1])

              i=2
              if (rl1[0] == 'n'):
                while (i < (len(rl1))):
                  if (tmpstr[index:(index+len(rl1[i]))] == rl1[i]):
                    OKpost1 = False
                    break
                  else:
                    OKpost1 = True
                  i+=1
              else:
                while (i < (len(rl1))):
                  if (tmpstr[index:(index+len(rl1[i]))] == rl1[i]):
                    OKpost1 = True
                    break
                  i+=1

              rl2=rls[1].split(';')

              if (int(rl2[1]) < 0):
                index =  pat_start+int(rl2[1])
              else:
                index =  pat_start+(len(orgpat)-1)+int(rl2[1])

              i=2
              if (rl2[0] == 'n'):
                while (i < (len(rl2))):
                  if (tmpstr[index:(index+len(rl2[i]))] == rl2[i]):
                    OKpost2 = False
                    break
                  else:
                    OKpost2 = True
                  i+=1
              else:
                while (i < (len(rl2))):
                  if (tmpstr[index:(index+len(rl2[i]))] == rl2[i]):
                    OKpost2 = True
                    break
                  i+=1

              OKpost=OKpost1 and OKpost2

            else:
              rl=postcond.split(';')

              if (int(rl[1]) < 0):
                index =  pat_start+int(rl[1])
              else:
                index =  pat_start+(len(orgpat)-1)+int(rl[1])

              i=2
              if (rl[0] == 'n'):
                while (i < (len(rl))):
                  if (tmpstr[index:(index+len(rl[i]))] == rl[i]):
                    OKpost = False
                    break
                  else:
                    OKpost = True
                  i+=1
              else:
                while (i < (len(rl))):
                  if (tmpstr[index:(index+len(rl[i]))] == rl[i]):
                    OKpost = True
                    break
                  i+=1

      if (existcond == 'None'):
        OKexist = True

      else:
        rl=existcond.split(';')
        if (rl[1] == 'slavo'):
          r=self.__slavo_germanic__(s)
          if (rl[0] == 'n'):
            if (r == 0):
              OKexist=True
          else:
            if (r == 1):
              OKexist=True
        else:
          i=1
          if (rl[0] == 'n'):
            while (i < (len(rl))):
              if (s.find(rl[i]) > -1):
                OKexist = False
                break
              else:
                OKexist = True
              i+=i
          else:
            while (i < (len(rl))):
              if (s.find(rl[i]) > -1):
                OKexist = True
                break
              i+=i

      if (startcond == 'None'):
        OKstart = True

      else:
        rl=startcond.split(';')
        i=1
        if (rl[0] == 'n'):
          while (i < (len(rl))):
            if (s.find(rl[i]) > -1):
              OKstart = False
              break
            else:
              OKstart = True
            i+=i
        else:
          while (i < (len(rl))):
            if (s.find(rl[i]) == 0):
              OKstart = True
              break
            i+=i

      # Replace pattern if conditions and position OK
      #
      if ((OKpre == True) and (OKpost == True) and (OKexist == True) and \
          (OKstart == True)) and (((where == 'START') and (pat_start == 0)) \
          or ((where == 'MIDDLE') and (pat_start > 0) and \
          (pat_start+pat_len < str_len)) or ((where == 'END') and \
          (pat_start+pat_len == str_len)) or (where == 'ALL')):
        tmpstr = tmpstr[:pat_start]+newpat+tmpstr[pat_start+pat_len:]
        changesstr += ',' +orgpat + '>' + newpat + '>' + where.lower()
        start_search = pat_start + len(newpat)

      else:
        start_search = pat_start+1

      if (start_search >= (len(tmpstr)-1)):
        stop = True

    tmpstr += changesstr

    return tmpstr

  # ---------------------------------------------------------------------------

  def __get_transformation__(self, in_str):
    """Helper function which generates the list of possible phonetic
       modifications for the given input string.

       Developed by Agus Pudjijono, ANU, 2008.
    """

    if (in_str == ''):
      return in_str

    changesstr2 = ''

    workstr = in_str

    for rtpl in self.replace_table:  # Check all transformations in the table
      if (len(rtpl) == 3):
         rtpl += ('None','None','None','None')

      workstr = self.__collect_replacement__(in_str,rtpl[0],rtpl[1],rtpl[2],
                                             rtpl[3],rtpl[4],rtpl[5],rtpl[6])
      if (workstr.find(',') > -1):
        tmpstr = workstr.split(',')
        workstr = tmpstr[0]
        if (changesstr2.find(tmpstr[1]) == -1):
          changesstr2 += tmpstr[1]+';'
    workstr += ',' + changesstr2

    return workstr

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_str):
    """Method which corrupts the given input string by applying a phonetic
       modification.

       If several such modifications are possible then one will be randomly
       selected.
    """

    if (len(in_str) == 0):  # Empty string, no modification possible
      return in_str

    # Get the possible phonetic modifications for this input string
    #
    phonetic_changes = self.__get_transformation__(in_str)

    mod_str = in_str

    if (',' in phonetic_changes):  # Several modifications possible
      tmp_str = phonetic_changes.split(',')
      pc = tmp_str[1][:-1] # Remove the last ';'
      list_pc = pc.split(';')
      change_op = random.choice(list_pc)
      if (change_op != ''):
        mod_str = self.__apply_change__(in_str, change_op)
        #print in_str, mod_str, change_op

    return mod_str

# =============================================================================

class CorruptCategoricalValue(CorruptValue):
  """Replace a categorical value with another categorical value from the same
     look-up file.

     This corruptor can be used to modify attribute values with known
     misspellings.

     The look-up file is a CSV file with two columns, the first is a
     categorical value that is expected to be in an attribute in an original
     record, and the second is a variation of this categorical value.

     It is possible for an 'original' categorical value (first column) to have
     several misspelling variations (second column). In such a case one
     misspelling will be randomly selected.

     The additional arguments (besides the base class argument
     'position_function') that have to be set when this attribute type is
     initialised are:

     lookup_file_name  Name of the file which contains the categorical values
                       and their misspellings.

     has_header_line   A flag, set to True or False, that has to be set
                       according to if the look-up file starts with a header
                       line or not.

     unicode_encoding  The Unicode encoding (a string name) of the file.

     Note that the 'position_function' is not required by this corruptor
     method.
  """

  # ---------------------------------------------------------------------------

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.lookup_file_name = None
    self.has_header_line =  None
    self.unicode_encoding = None
    self.misspell_dict =    {}  # The dictionary to hold the misspellings
    self.name =             'Categorial value'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('look')):
        basefunctions.check_is_non_empty_string('lookup_file_name', value)
        self.lookup_file_name = value

      elif (keyword.startswith('has')):
        basefunctions.check_is_flag('has_header_line', value)
        self.has_header_line = value

      elif (keyword.startswith('unicode')):
        basefunctions.check_is_non_empty_string('unicode_encoding', value)
        self.unicode_encoding = value

      else:
        base_kwargs[keyword] = value

    base_kwargs['position_function'] = dummy_position

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_non_empty_string('lookup_file_name',
                                            self.lookup_file_name)
    basefunctions.check_is_flag('has_header_line', self.has_header_line)
    basefunctions.check_is_non_empty_string('unicode_encoding',
                                            self.unicode_encoding)

    # Load the misspelling lookup file - - - - - - - - - - - - - - - - - - - - -
    #
    header_list, lookup_file_data = \
                     basefunctions.read_csv_file(self.lookup_file_name,
                                                 self.unicode_encoding,
                                                 self.has_header_line)

    # Process values from file and misspellings
    #
    for rec_list in lookup_file_data:
      if (len(rec_list) != 2):
        raise Exception, 'Illegal format in misspellings lookup file %s: %s' \
                         % (self.lookup_file_name, str(rec_list))

      org_val =  rec_list[0].strip()
      if (org_val == ''):
        raise Exception, 'Empty original attribute value in lookup file %s' % \
                         (self.lookup_file_name)
      misspell_val = rec_list[1].strip()
      if (misspell_val == ''):
        raise Exception, 'Empty misspelled attribute value in lookup ' + \
                         'file %s' % (self.lookup_file_name)
      if (org_val == misspell_val):
        raise Exception, 'Misspelled value is the same as original value' + \
                         ' in lookup file %s' % (self.lookup_file_name)

      this_org_val_list = self.misspell_dict.get(org_val, [])
      this_org_val_list.append(misspell_val)
      self.misspell_dict[org_val] = this_org_val_list

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_str):
    """Method which corrupts the given input string and replaces it with a
       misspelling, if there is a known misspelling for the given original
       value.

       If there are several known misspellings for the given original value
       then one will be randomly selected.
    """

    if (len(in_str) == 0):  # Empty string, no modification possible
      return in_str

    if (in_str not in self.misspell_dict):  # No misspelling for this value
      return in_str

    misspell_list = self.misspell_dict[in_str]

    return random.choice(misspell_list)


# =============================================================================

# =============================================================================
# ===========THIS IS NEW DEVELPOMENT- CRPTR====================================
class CorruptUnknownCharacter(CorruptValue):

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.unknown_char =  None
    self.name =            'Unknown Character'

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('unknown')):
        basefunctions.check_is_string('unknown_char', value)
        self.unknown_char = value

      else:
        base_kwargs[keyword] = value

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_string('unknown_char',
                                              self.unknown_char)
  def corrupt_value(self, in_str):
    """Method which corrupts the given input string and returns the modified
       string by randomly selecting an edit operation and position in the
       string where to apply this edit.
    """
    if (len(in_str) == 0):  # Empty string, no modification possible
      return in_str
    mod_pos = self.position_function(in_str)
    new_str = in_str[:mod_pos] + self.unknown_char + in_str[mod_pos + 1:]
    return new_str

class CorruptAbbreviatedNameForms(CorruptValue):

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.num_of_char =  None
    self.name =            'Abbreviated Name Forms'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('num')):
        basefunctions.check_is_integer('num_of_char', value)
        self.num_of_char = value
      else:
        base_kwargs[keyword] = value
    base_kwargs['position_function'] = dummy_position
    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_integer('num_of_char',
                                              self.num_of_char)
  def corrupt_value(self, in_str):
    """Method which corrupts the given input string and returns the modified
       string by randomly selecting an edit operation and position in the
       string where to apply this edit.
    """
    if (len(in_str) == 0) or (len(in_str) < self.num_of_char):  # Empty string, no modification possible
      return in_str
    new_str = in_str[:self.num_of_char]
    return new_str

# =============================================================================

class CorruptCategoricalDomain(CorruptValue):

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.categories_list =  None
    self.name =            'Categorical Domain'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('categories')):
        basefunctions.check_is_list('categories_list', value)
        self.categories_list = value
      else:
        base_kwargs[keyword] = value
    base_kwargs['position_function'] = dummy_position

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_list('categories_list',
                                              self.categories_list)
  def corrupt_value(self, in_str):
    """Method which corrupts the given input string and returns the modified
       string by randomly selecting an edit operation and position in the
       string where to apply this edit.
    """
    if in_str not in self.categories_list:
      return in_str
    #cat_list = self.categories_list
    if in_str in self.categories_list:
      new_str = in_str
      while new_str == in_str:
        new_str = random.choice(self.categories_list)
      return new_str



# =============================================================================
# =============================END - CRPTR=====================================
# =============================================================================

class CorruptDate(CorruptValue):

  def __init__(self, **kwargs):
    """Constructor. Process the derived keywords first, then call the base
       class constructor.
    """

    self.date_order =  None
    self.separator = None
    self.components_to_modify = None
    self.date_corruption_methods = None
    self.name =            'Date'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('date_ord')):
        basefunctions.check_date_order('date_order', value)
        self.date_order = value

      elif (keyword.startswith('separator')):
        basefunctions.check_date_separator('separator', value)
        self.separator = value

      elif (keyword.startswith('components')):
        basefunctions.check_date_components_to_modify('components_to_modify', value)
        self.components_to_modify = value

      elif (keyword.startswith('date_corruption')):
        basefunctions.check_date_modification_methods('date_corruption_methods', value)
        self.date_corruption_methods = value

      else:
        base_kwargs[keyword] = value
    base_kwargs['position_function'] = dummy_position

    CorruptValue.__init__(self, base_kwargs)  # Process base arguments

    # Check if the necessary variables have been set
    #
    basefunctions.check_is_non_empty_string('date_order',
                                              self.date_order)
    basefunctions.check_is_non_empty_string('separator',
                                self.separator)
    basefunctions.check_is_list('components_to_modify',
                                self.components_to_modify)
    basefunctions.check_is_list('date_corruption_methods',
                                self.date_corruption_methods)

  def corrupt_value(self, in_str):
    """Method which corrupts the given input string and returns the modified
       string by randomly selecting an edit operation and position in the
       string where to apply this edit.
    """
    if self.date_order == "dd-mm-yyyy":
      day, month, year = in_str.split(self.separator)
      day = day.zfill(2)
      month = month.zfill(2)
      year = year.zfill(4)
    elif self.date_order == "mm-dd-yyyy":
      month, day, year = in_str.split(self.separator)
      day = day.zfill(2)
      month = month.zfill(2)
      year = year.zfill(4)
    elif self.date_order == "yyyy-mm-dd":
      year, month, day = in_str.split(self.separator)
      day = day.zfill(2)
      month = month.zfill(2)
      year = year.zfill(4)
    else:
      print "date format and order is not correct"

    comp_mod = random.choice(self.components_to_modify)
    crpt_method = random.choice(self.date_corruption_methods)

    ran_num = random.randint(1, 10)

    if crpt_method == 'add':
      if comp_mod == 'day':
        day = int(day) + ran_num
      elif comp_mod == "month":
        month = int(month) + ran_num
      elif comp_mod == "year":
        year = int(year) + ran_num

    elif crpt_method == "decline":
      if comp_mod == 'day':
        if int(day) - ran_num < 1:
          day = 1
        else:
          day = int(day) - ran_num
      elif comp_mod == "month":
        if int(month) - ran_num < 1:
          month = 1
        else:
          month = int(month) - ran_num
      elif comp_mod == "year":
        year = int(year) - ran_num

    elif crpt_method == "first":
      day = '01'
      month = '01'

    elif crpt_method == "random":
      if comp_mod == "day":
        ran_day = random.randint(1, 30)
        day = ran_day
      elif comp_mod == "month":
        ran_month = random.randint(1, 12)
        month = ran_month
      elif comp_mod == "year":
        ran_year = random.randint(1750, 2100)
        year = ran_year

    elif crpt_method == "swap_comp":
      if comp_mod == "day":
        other_comp = ['month', 'year']
        swap_attr = random.choice(other_comp)
        print swap_attr
        if swap_attr == "month":
          h_day = day
          day = month
          month = h_day
        elif swap_attr == "year":
          h_day = day
          day = year
          year = h_day
      elif comp_mod == "month":
        other_comp = ['day', 'year']
        swap_attr = random.choice(other_comp)
        print swap_attr
        if swap_attr == "day":
          h_month = month
          month = day
          day = h_month
        elif swap_attr == "year":
          h_month = month
          month = year
          year = h_month
      elif comp_mod == "year":
        other_comp = ['day', 'month']
        swap_attr = random.choice(other_comp)
        print swap_attr
        if swap_attr == "day":
          h_year = year
          year = day
          day = h_year
        elif swap_attr == "month":
          h_year = year
          year = month
          month = h_year

    elif crpt_method == "swap_digit":
      if comp_mod == "day":
        comp_lst = list(day)
        print comp_lst
        index_lst = range(0, len(comp_lst))
        print index_lst
        swap_lst = sorted(random.sample(index_lst, 2))
        print swap_lst
        fst_index = comp_lst[swap_lst[0]]
        print fst_index
        snd_index = comp_lst[swap_lst[1]]
        print snd_index
        comp_lst[swap_lst[0]] = snd_index
        comp_lst[swap_lst[1]] = fst_index
        new_comp = ''.join(comp_lst)
        print comp_lst
        print new_comp
        day = new_comp

      elif comp_mod == "month":
        comp_lst = list(month)
        print comp_lst
        index_lst = range(0, len(comp_lst))
        print index_lst
        swap_lst = sorted(random.sample(index_lst, 2))
        print swap_lst
        fst_index = comp_lst[swap_lst[0]]
        print fst_index
        snd_index = comp_lst[swap_lst[1]]
        print snd_index
        comp_lst[swap_lst[0]] = snd_index
        comp_lst[swap_lst[1]] = fst_index
        new_comp = ''.join(comp_lst)
        print comp_lst
        print new_comp
        month = new_comp
      elif comp_mod == "year":
        comp_lst = list(year)
        print comp_lst
        index_lst = range(0, len(comp_lst))
        print index_lst
        swap_lst = sorted(random.sample(index_lst, 2))
        print swap_lst
        fst_index = comp_lst[swap_lst[0]]
        print fst_index
        snd_index = comp_lst[swap_lst[1]]
        print snd_index
        comp_lst[swap_lst[0]] = snd_index
        comp_lst[swap_lst[1]] = fst_index
        new_comp = ''.join(comp_lst)
        print comp_lst
        print new_comp
        year = new_comp

    elif crpt_method == "full_month" or "abbr_month":
      comp_mod = "month"
      month = int(month)
      if crpt_method == "full_month":
        full_month_dict = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, \
                           'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
        for key, value in full_month_dict.iteritems():
          if value == month:
            month = key
      elif crpt_method == "abbr_month":
        abbr_month_dict = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, \
                           'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        for key, value in abbr_month_dict.iteritems():
          if value == month:
            month = key

    if self.date_order == "dd-mm-yyyy":
      new_date = str(day) + self.separator + str(month) + self.separator + str(year)
    elif self.date_order == "mm-dd-yyyy":
      new_date = str(month) + self.separator + str(day) + self.separator + str(year)
    elif self.date_order == "yyyy-mm-dd":
      new_date = str(year) + self.separator + str(month) + self.separator + str(day)

    return new_date

