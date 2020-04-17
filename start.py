import requests
import time, math, random
import hashlib, json
from lxml import html


#TODO Generate a random ID and MD5 Hash it, package I use in nodejs is uniqid and then cryptoJS to hash it.
#TODO Make POST request to https://profile.callofduty.com/cod/mapp/registerDevice with said device ID
#TODO You will receive a authheader as a response
#TODO pass that and device id as headers to https://profile.callofduty.com/cod/mapp/login
#TODO Headers should be Authorization: bearer {authheader} and x_cod_device_id {deviceid}

defaultUri = 'https://my.callofduty.com/api/papi-client'

session_requests = requests.session()

cookies = {
    'new_SiteId': 'cod',
    'ACT_SSO_LOCALE': 'en_US',
    'country': 'US',
    'XSRF-TOKEN': '68e8b62e-1d9d-4ce1-b93f-cbe5ff31a041'
}

session_requests.headers.update({'content-type': 'application/json'})
session_requests.cookies.update(cookies)

def uniqid(prefix = '', more_entropy=False):
    m = time.time()
    sec = math.floor(m)
    usec = math.floor(1000000 * (m - sec))
    if more_entropy:
        lcg = random.random()
        the_uniqid = "%08x%05x%.8F" % (sec, usec, lcg * 10)
    else:
        the_uniqid = '%8x%05x' % (sec, usec)

    the_uniqid = prefix + the_uniqid
    return the_uniqid


def generateId():
    deviceId = uniqid()
    result = hashlib.md5(deviceId.encode())
    return result.hexdigest() 

def authenticate(email, password):
    deviceId = generateId()
    data = json.dumps({'deviceId': deviceId}, separators=(',', ':'))
    res = postReq("https://profile.callofduty.com/cod/mapp/registerDevice", data)
    output = res.content.decode()
    json_obj = json.loads(output)
    if json_obj['status'] != 'success': return print("Could not authenticate.")
    authHeader = json_obj['data']['authHeader']
    session_requests.headers.update({ 'Authorization': 'bearer %s' % authHeader, 'x_cod_device_id': deviceId })
    login(email, password)

def login(email, password): 
    data = json.dumps({ "email": email, "password": password }, separators=(',', ':'))
    res = postReq("https://profile.callofduty.com/cod/mapp/login", data)
    output = res.content.decode()
    json_obj = json.loads(output)
    if json_obj["success"] != True: return print("Could not Login.")
    session_requests.cookies.update({
        'rtkn': json_obj["rtkn"],
        'ACT_SSO_COOKIE': json_obj["s_ACT_SSO_COOKIE"],
        'atkn': json_obj["atkn"]
    })
    testFunc("Lierrmm%232364", "battle")

def testFunc(gamertag, platform):
    result = getReq('{}/stats/cod/v1/title/mw/platform/{}/gamer/{}/profile/type/mp'.format(defaultUri, platform, gamertag))
    print(result.content.decode())

def getReq(url):
    result = session_requests.get(url)
    return result

def postReq(url, data):
    result = session_requests.post(url, data = data)
    return result

authenticate('<email>', '<password>')
