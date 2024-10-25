import requests

r = requests.get("http://192.168.0.88:8000/regions")
print(r.content)