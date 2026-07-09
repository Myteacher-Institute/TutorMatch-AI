import requests, re

s = requests.Session()
r = s.get('http://127.0.0.1:8001/ai-assistant/')
print('GET status', r.status_code)
m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r.text)
print('csrf found:', bool(m))
token = m.group(1) if m else ''
r2 = s.post('http://127.0.0.1:8001/ai-assistant/',
            data={'csrfmiddlewaretoken': token, 'message': 'I need a maths tutor in GRA'},
            headers={'X-Requested-With': 'XMLHttpRequest'}, allow_redirects=True)
print('POST status', r2.status_code, 'final', r2.url)
print('has user msg:', 'I need a maths tutor in GRA' in r2.text)
print('has assistant:', 'ai-rendered-msg' in r2.text)
print('has failure:', 'Failed to connect' in r2.text)
