import requests


# response = requests.post(
#     'http://192.168.1.70:5000/ads/',
#     json={'heading':'test1', 'description':'test2', 'owner':'matushinoleg24d4D5@yandex.ru'}

# )

response = requests.post(
     'http://192.168.1.70:5000/letter/',
)

# response = requests.get(
#     'http://192.168.1.119:5000/ads/8',
# )

print(response.text)