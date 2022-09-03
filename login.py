import requests
from bs4 import BeautifulSoup
import json, datetime
import sys, os

import random
import base64
from Crypto.Cipher import AES
from Crypto.Util import Padding

if len(sys.argv) == 3:
  username = sys.argv[1]
  password = sys.argv[2]
else:
  username = os.environ['NJU_USERNAME']
  password = os.environ['NJU_PASSWORD']

url = "https://authserver.nju.edu.cn/authserver/login?service=http%3A%2F%2Fp.nju.edu.cn%2Fcas%2F&login_type=mobileLogin"

# Reference: https://github.com/forewing/nju-health-checkin/blob/master/checkin.py
def encryptAES(data, key):
  def rds(len):
    return ''.join(random.choices("ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678", k=len))
  encrypt = AES.new(key.strip().encode('utf-8'), AES.MODE_CBC, rds(16).encode('utf-8'))
  return base64.b64encode(encrypt.encrypt(Padding.pad((rds(64) + data).encode('utf-8'), 16))).decode('utf-8')

def getInput(soup, id=None, name=None):
  if id:
    return soup.find("input", {"id": id})['value']
  elif name:
    return soup.find("input", {"name": name})['value']

s = requests.Session()
s.headers.update({'User-Agent': 'iPhone cpdaily'})
r = s.get(url)
try:
  soup = BeautifulSoup(r.text, 'html.parser')
  salt_start = r.text.index("pwdDefaultEncryptSalt") + len("pwdDefaultEncryptSalt") + 4
  salt_end = r.text.index("\";", salt_start)
  salt = r.text[salt_start : salt_end]

  data = {
    'username': username,
    'password': encryptAES(password, salt),
    'lt': getInput(soup, name="lt"),
    'dllt': "mobileLogin",
    'execution': getInput(soup, name="execution"),
    '_eventId': getInput(soup, name="_eventId"),
    'rmShown': getInput(soup, name="rmShown"),
  }
except:
  print("Failed to retrieve login information")

r = requests.get("https://authserver.nju.edu.cn/authserver/needCaptcha.html?username=" + username)
if r.text == "true":
  print("CAPTCHA required")
  
  print("Initializing OCR...")
  import muggle_ocr
  os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
  
  print("Obtaining CAPTCHA...")
  res = s.get("https://authserver.nju.edu.cn/authserver/captcha.html")
  
  print("Solving CAPTCHA...")
  sdk = muggle_ocr.SDK(model_type = muggle_ocr.ModelType.Captcha)
  captcha_text = sdk.predict(image_bytes = res.content)
  print("CAPTCHA:", captcha_text)
  
  data["captchaResponse"] = captcha_text

print("Logging in...")
s.post(url, data)

r = requests.get("http://p.nju.edu.cn/api/selfservice/v1/volume/" + datetime.datetime.now().strftime("%m"))
try:
  data = json.loads(r.text)
except:
  print(r.text)
  print("Failed to parse data")

if data["reply_code"] == 403:
  print(r.text)
  print("Failed to login")
else:
  total_secs = data["results"]["rows"][0]["total_time"]
  print("Uptime: {}h{}m{}s".format(total_secs // 3600, total_secs % 3600 // 60, total_secs % 60))
