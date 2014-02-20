def ConvertJson(json_str):
  """Convert json string to a python object.

  Args:
    json_str: string, json response.
  Returns:
    dictionary of deserialized json string.
  """
  j = {}
  try:
    j = json.loads(json_str)
    j['json'] = True
  except ValueError, e:
    # This means the format from json_str is probably bad.
    logger.error('Error parsing json string %s\n%s', json_str, e)
    j['json'] = False
    j['error'] = e

  return j

def GetKeyValue(line, sep=':'):
    """Return value from a key value pair string.

    Args:
      line: string containing key value pair.
      sep: separator of key and value.
    Returns:
      string: value from key value string.
    """
    s = line.split(sep)
    return StripPunc(s[1])

def StripPunc(s):
  """Strip puncuation from string, except for - sign.

  Args:
    s: string.
  Returns:
    string with puncuation removed.
  """
  for c in string.punctuation:
    if c == '-':  # Could be negative number, so don't remove '-'.
      continue
    else:
      s = s.replace(c, '')
  return s.strip()

def Validate(response):
  """Determine if JSON response indicated success."""
  if response.find('"success": true') > 0:
    return True
  else:
    return False

def GetMessage(response):
  """Extract the API message from a Cloud Print API json response.

  Args:
    response: json response from API request.
  Returns:
    string: message content in json response.
  """
  lines = response.split('\n')
  for line in lines:
    if '"message":' in line:
      msg = line.split(':')
      return msg[1]

  return None

def ReadFile(pathname):
  """Read contents of a file and return content.

  Args:
    pathname: string, (path)name of file.
  Returns:
    string: contents of file.
  """
  try:
    f = open(pathname, 'rb')
    try:
      s = f.read()
    except IOError, e:
      logger('Error reading %s\n%s', pathname, e)
    finally:
      f.close()
      return s
  except IOError, e:
    logger.error('Error opening %s\n%s', pathname, e)
    return None

def WriteFile(file_name, data):
  """Write contents of data to a file_name.

  Args:
    file_name: string, (path)name of file.
    data: string, contents to write to file.
  Returns:
    boolean: True = success, False = errors.
  """
  status = True

  try:
    f = open(file_name, 'wb')
    try:
      f.write(data)
    except IOError, e:
      logger.error('Error writing %s\n%s', file_name, e)
      status = False
    finally:
      f.close()
  except IOError, e:
    logger.error('Error opening %s\n%s', file_name, e)
    status = False

  return status

def Base64Encode(pathname):
  """Convert a file to a base64 encoded file.

  Args:
    pathname: path name of file to base64 encode..
  Returns:
    string, name of base64 encoded file.
  For more info on data urls, see:
    http://en.wikipedia.org/wiki/Data_URI_scheme
  """
  b64_pathname = pathname + '.b64'
  file_type = mimetypes.guess_type(pathname)[0] or 'application/octet-stream'
  data = ReadFile(pathname)

  # Convert binary data to base64 encoded data.
  header = 'data:%s;base64,' % file_type
  b64data = header + base64.b64encode(data)

  if WriteFile(b64_pathname, b64data):
    return b64_pathname
  else:
    return None
