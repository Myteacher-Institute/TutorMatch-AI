import requests, re

s = requests.Session()
# Test find_tutor search -> should create a new chat
r = s.get('http://127.0.0.1:8001/find-tutor/?q=' + 'maths tutor in GRA')
print('find_tutor status', r.status_code, 'redirect to', r.url)
# follow
r2 = s.get(r.url, allow_redirects=True)
print('ai_assistant final', r2.status_code, r2.url)
print('has user prompt msg:', 'maths tutor in GRA' in r2.text)
# how many conversations in sidebar
print('sidebar New chat count approx:', r2.text.count('sidebar-link-wrapper'))

# Print the assistant reply text from the chat test
r3 = s.get('http://127.0.0.1:8001/ai-assistant/')
m = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', r3.text)
token = m.group(1)
r4 = s.post('http://127.0.0.1:8001/ai-assistant/',
            data={'csrfmiddlewaretoken': token, 'message': 'hello there'},
            headers={'X-Requested-With': 'XMLHttpRequest'}, allow_redirects=True)
# extract assistant bubble text
idx = r4.text.find('ai-rendered-msg')
print('--- assistant reply snippet ---')
print(r4.text[idx:idx+400])
