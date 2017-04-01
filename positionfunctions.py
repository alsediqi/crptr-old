# Import necessary modules
import random

# =============================================================================
# Helper functions to randomly select a position for where to apply a
# modification

def position_mod_uniform(in_str):
  """Select any position in the given input string with uniform likelihood.

     Return 0 is the string is empty.
  """

  if (in_str == ''):  # Empty input string
    return 0

  max_pos = len(in_str)-1

  pos = random.randint(0, max_pos)  # String positions start at 0

  return pos

# -----------------------------------------------------------------------------

def position_mod_normal(in_str):
  """Select any position in the given input string with normally distributed
     likelihood where the average of the normal distribution is set to one
     character behind the middle of the string, and the standard deviation is
     set to 1/4 of the string length.

     This is based on studies on the distribution of errors in real text which
     showed that errors such as typographical mistakes are more likely to
     appear towards the middle and end of a string but not at the beginning.

     Return 0 is the string is empty.
  """

  if (in_str == ''):  # Empty input string
    return 0

  str_len = len(in_str)

  mid_pos = str_len / 2.0 + 1
  std_dev = str_len / 4.0
  max_pos = str_len - 1

  pos = int(round(random.gauss(mid_pos, std_dev)))
  while ((pos < 0) or (pos > max_pos)):
    pos = int(round(random.gauss(mid_pos, std_dev)))

  return pos
