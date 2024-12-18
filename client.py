import json
import requests
# пример отправки запросов через requests!
s = requests.sessions.Session()
token_res = s.post("http://0.0.0.0:8000/login", data={"username": "geruto","password": "zxc"})
token = json.loads(token_res.text)
print(token) # вывод токена
resp = s.get("http://0.0.0.0:8000/bonus-program", headers={"Authorization": f"Bearer {token['access_token']}"})
print(resp.text) # пример с авторизацией, выведет данные о клиенте!
resp = s.get("http://0.0.0.0:8000/bonus-program")
print(resp.text) # пример без авторизации, выведет {"detail":"Not authenticated"}