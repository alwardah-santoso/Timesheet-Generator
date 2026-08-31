import sys
import os
import urllib.request
import json
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))
from config import settings

url = f"{settings.web_app_url}?id={settings.timesheet_ss_id}&action=get_tabs"
print(url)
try:
    with urllib.request.urlopen(url) as resp:
        print(resp.read().decode('utf-8')[:500])
except Exception as e:
    print(e)
