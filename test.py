# from cryptography.fernet import Fernet
#
# # Генерация ключа для шифрования
# with open("secret.key", "rb") as key_file:
#     key = key_file.read()
#
# cipher_suite = Fernet(key)
# tt = b"hhheeerrr"
# cipher_text = b'gAAAAABnAk3eWiiJ0rpU18C9max2aHKaFrIp_9LKdy1YbYycKMJ1UcnIuCcbDu8pa2SaQxF7OmMcq6BH791dnRq4GLRCdW_04w=='
# plain_text = cipher_suite.decrypt(cipher_text)
# print("Расшифрованные данные:", plain_text.decode('utf-8'))
# print(cipher_suite.encrypt(tt))
#
#
# import jwt
#
#
# # Секретный ключ для подписи токенов
# with open("secret.key", "rb") as key_file:
#     SECRET_KEY = key_file.read()
#
#
# def encode(data):
#     # Определение полезной нагрузки токена
#     payload = {'data': data}
#     # Создание токена
#     token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
#     return token
#
# def decode(token):
#     try:
#         # Расшифровка токена
#         payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
#         return payload
#     except jwt.ExpiredSignatureError:
#         # Токен истёк
#         return None
#     except jwt.InvalidTokenError:
#         # Невалидный токен
#         return None
#
# print(encode('helloworld'))
# print(encode('helloworld123'))
# print(encode('helloworld321'))
# print(decode('eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjoiaGVsbG93b3JsZDMyMSJ9.Yy51nLTZCszT08uJHcu1j_Qm9qG7N5NFaAuoel5VVC4')['data'])

#
# data = {'111' : "111", "222" : "222", "333" : "333"}
# data["444"] = "444"
# del data["111"]
# for i in data:
#     text = data[i]
#     del data[i]
#     data[f"{i}"] = text
# print(data)

import time
t = time.time()
time.sleep(5)
print(time.time() - t)
