def check_is_non_empty_string(variable, value):
  """Check if the value given is of type string and is not an empty string.

     The argument 'variable' needs to be set to the name (as a string) of the
     value which is checked.
  """

  if ((not isinstance(variable, str)) or (variable == '')):
    raise Exception, 'Value of "variable" is not a non-empty string: %s (%s)' \
                     % (str(variable), type(variable))

  if ((not isinstance(value, str)) or (value == '')):
    raise Exception, 'Value of "%s" is not a non-empty string: %s (%s)' % \
                     (variable, str(value), type(value))

x = "THIS is string"
#x = 1
print check_is_non_empty_string(x,x)