'''

 Doublie Coding Challenge
 Yash Abooj

 A web app:
  1. to create checksum for a callback URL
  2. to verify the checksum of a checksummed URL

'''


from flask import Flask
from flask import request
import hashlib, hmac

# create an instance of a Flask object
app = Flask(__name__)

# declare a private key to sign the URL data
PRIVATE_KEY = 'Doublie_Coding_Challenge'


# function to compute the MD5 sum of a string
def computeMD5checksum(string):
    return hmac.new(PRIVATE_KEY, string, hashlib.md5).hexdigest()


# default page of the web app
@app.route('/')
def index():
    return "Doublie Coding Challenge!"


# function to generate the checksum for the specified URL string

## Method used to generate checksum:
##  - remove the protocol name and 'www', if present in the URL
##  - sort the URL parameters according to the keys present
##  - re-build an ordered URL with the sorted keys
##  - return MD5 sum of the ordered URL
## This approach makes the checksum independent of the order in 
## which the parameters appear

def generate_checksum(url):
    # remove protocol name, if present
    url = url.split('://', 1)
    if len(url) == 2:
        url = url[1]
    else:
        url = url[0]
    # remove 'www'
    if url[:4] == 'www.':
        url = url[4:]

    # split the domain names and the query string
    url = url.split('?', 1)
    # Case: no query string present
    if len(url) == 1:
        return computeMD5checksum(url[0])

    # build the ordered URL
    ordered_url = url[0] + '?'
    parameters = url[1].split('&') # get the parameters in URL query
    param_dict = {}
    for param in parameters:
        key_value = param.split('=', 1)
        param_dict[key_value[0]] = key_value[1]
    keylist = param_dict.keys() # get keys from the parameters
    keylist.sort() # sort the keys
    # re-build URL with the sorted keys
    for key in keylist:
        ordered_url += key + '=' + param_dict[key] + '&'
    return computeMD5checksum(ordered_url[:(len(ordered_url) - 1)])


# function to create checksum of the URL in the HTTP GET request
@app.route('/createchecksum')
def createchecksum():
    query_string = request.query_string # get the URL
    url = query_string.split('=', 1)[1]
    # Case: no query string in the URL
    if url.find('?') == -1:
        return url + '?checksum=' + generate_checksum(url) + '\n'
    return url + '&checksum=' + generate_checksum(url) + '\n'


# function to verify checksum of the URL in the HTTP GET request
@app.route('/checkchecksum')
def checkchecksum():
    query_string = request.query_string # get the URL
    checksum_url = query_string.split('=', 1)[1]
    param_list = checksum_url.split('&')

    # Case: URL has just one - 'checksum' parameter
    if len(param_list) == 1:
        param_list = checksum_url.split('?', 1)
        key_value = param_list[1].split('=', 1)
        if key_value[0] != 'checksum':
            return ('checksum not available\n', 400)
        if generate_checksum(param_list[0]) == key_value[1]:
            return 'verified\n'
        else:
            return ('not verified\n', 400)

    # Case: no checksum present in the URL to be verified
    if 'checksum' not in request.args:
        return ('checksum not available\n', 400)
    
    # remove parameter 'checksum' assuming it to be the last in the URL
    url = param_list[0]
    for i in range(1,len(param_list) - 1):
        url += '&' + param_list[i]
    # verify the checksum
    if generate_checksum(url) == request.args['checksum']:
        return 'verified\n'
    else:
        return ('not verified\n', 400)


# start the web server
if __name__ == '__main__':
    app.run()
