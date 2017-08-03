import math
import random
import basefunctions
import positionfunctions
# ===============================================================================
# Classes for corrupting a value in a list of attributes (fields) of the data set
# ===============================================================================
#attr_name_list Need to be included in this model to allow index selection from records for record level corruptions

attr_name_list = ['crptr-record','FirstName', 'LastName','Gender','DateofBirth','FatherFirstName','FatherLastName', 'FatherOccupation',	'MotherFirstName', 'MotherLastName', 'MotherOccupation']

class CorruptRecord:
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

  def corrupt_value(self, list):
    """Method which corrupts the given input list of strings and returns the modified
       list.
       See implementations in derived classes for details.
    """

    raise Exception, 'Override abstract method in derived class'

# =============================================================================

class CorruptClearRecord(CorruptRecord):
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

    self.clear_val = ' '
    self.name =        'Clear record'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('clear')):
        basefunctions.check_is_string('clear_val', value)
        self.clear_val = value

      else:
        base_kwargs[keyword] = value

    base_kwargs['position_function'] = dummy_position

    CorruptRecord.__init__(self, base_kwargs)  # Process base arguments

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_list):
    """Simply return the missing value string.
    """
    new_list = in_list[:]
    for idx in range (len(new_list)):
        new_list[idx] = self.clear_val
    return new_list

# =============================================================================
#clear_rec = CorruptClearRecord(\
#       clear_val=' ')

#print clear_rec.__dict__
#print clear_rec.corrupt_value(test_list)
# =============================================================================

class CorruptSwapAttributes(CorruptRecord):
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

    self.attr1 = None
    self.attr2 = None
    self.name =        'Swap Attributes'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('attr1')):
        basefunctions.check_is_string('attr1', value)
        self.attr1 = value
        if (value not in attr_name_list):
            raise Exception, 'Value of "%s" is not in dataset attributes. Check dataset correct attributes ' % str(value)


      elif (keyword.startswith('attr2')):
        basefunctions.check_is_string('attr2', value)
        self.attr2 = value
        if (value not in attr_name_list):
            raise Exception, 'Value of "%s" is not in dataset attributes. Check dataset correct attributes ' % str(value)
      else:
        base_kwargs[keyword] = value

    base_kwargs['position_function'] = dummy_position

    CorruptRecord.__init__(self, base_kwargs)  # Process base arguments

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_list):
    """Simply return the missing value string.
    """
    attr1_idx = attr_name_list.index(self.attr1)
    attr2_idx = attr_name_list.index(self.attr2)
    attr1_val = in_list[attr1_idx]
    attr2_val = in_list[attr2_idx]
    new_list = in_list[:]
    new_list[attr1_idx] = attr2_val
    new_list[attr2_idx] = attr1_val

    return new_list

# =============================================================================
# =============================================================================
#swap_attr = CorruptSwapAttributes(\
#    attr1='FirstName',
#    attr2= 'LastName'
#)

#print swap_attr.__dict__
#print swap_attr.corrupt_value(test_list)
# =============================================================================

class CorruptOverflowAttributes(CorruptRecord):
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
    self.attr1 = None
    self.attr2 = None
    self.overflow_level = None
    self.start_pos = None
    self.name =        'Overflow Attributes'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():

      if (keyword.startswith('attr1')):
        basefunctions.check_is_string('attr1', value)
        self.attr1 = value
        if (value not in attr_name_list):
            raise Exception, 'Value of "%s" is not in dataset attributes. Check dataset correct attributes : %s' % str(value)

      elif (keyword.startswith('attr2')):
        basefunctions.check_is_string('attr2', value)
        self.attr2 = value
        if (value not in attr_name_list):
            raise Exception, 'Value of "%s" is not in dataset attributes. Check dataset correct attributes : %s' % str(value)

      elif (keyword.startswith('overflow')):
        basefunctions.check_is_normalised('overflow_level', value)
        self.overflow_level = value

      elif (keyword.startswith('start')):
        basefunctions.check_start_position_of_overflow('start_pos', value)
        self.start_pos = value

      else:
        base_kwargs[keyword] = value

    base_kwargs['position_function'] = dummy_position

    CorruptRecord.__init__(self, base_kwargs)  # Process base arguments

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_list):
    """Simply return the missing value string.
    """
    attr1_idx = attr_name_list.index(self.attr1)
    attr2_idx = attr_name_list.index(self.attr2)
    attr1_val = in_list[attr1_idx]
    attr2_val = in_list[attr2_idx]
    new_list = in_list[:]
    if self.start_pos == 'beginning':
        overflow_len = len(attr2_val) * self.overflow_level
        overflow_len = int(overflow_len)
        print overflow_len
        new_attr1_val = attr1_val + attr2_val[:overflow_len]
        print new_attr1_val
        new_attr2_val = attr2_val[overflow_len:]
        print new_attr2_val
        new_list[attr1_idx] = new_attr1_val
        new_list[attr2_idx] = new_attr2_val

    elif self.start_pos == 'ending':
        overflow_len = len(attr1_val) * self.overflow_level
        overflow_len = int(overflow_len)
        print overflow_len
        new_attr2_val = attr1_val[overflow_len:] + attr2_val
        print new_attr2_val
        new_attr1_val = attr1_val[:overflow_len]
        print new_attr1_val
        new_list[attr1_idx] = new_attr1_val
        new_list[attr2_idx] = new_attr2_val

    return new_list

# =============================================================================
# =============================================================================
'''
over_attr = CorruptOverflowAttributes(\
    attr1='FirstName',
    attr2= 'LastName',
    overflow_level = 0.5,
    start_pos = 'beginning'
)

print over_attr.__dict__
print over_attr.corrupt_value(test_list)
# =============================================================================
'''
class CorruptMissingRecord(CorruptRecord):
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

    #self.missing_val = 'missing'
    self.name =        'Missing record'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():
        base_kwargs[keyword] = value

    base_kwargs['position_function'] = dummy_position

    CorruptRecord.__init__(self, base_kwargs)  # Process base arguments

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_list):
    """Simply return the missing value string.
    """
    new_list = in_list[:]
    for idx in range (len(new_list)):
        new_list[idx] = 'missing'
    return new_list

# =============================================================================
#missing_rec = CorruptMissingRecord()

#print missing_rec.__dict__
#print missing_rec.corrupt_value(test_list)
# =============================================================================

class CorruptDuplicateRecord(CorruptRecord):
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

    self.name =        'Missing record'

    def dummy_position(s):  # Define a dummy position function
      return 0

    # Process all keyword arguments
    #
    base_kwargs = {}  # Dictionary, will contain unprocessed arguments

    for (keyword, value) in kwargs.items():
        base_kwargs[keyword] = value

    base_kwargs['position_function'] = dummy_position

    CorruptRecord.__init__(self, base_kwargs)  # Process base arguments

  # ---------------------------------------------------------------------------

  def corrupt_value(self, in_list):
    """Simply return the missing value string.
    """
    new_list = in_list[:]
    new_list[0]=('duplicate')
    return new_list

# =============================================================================