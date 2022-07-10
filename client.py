import requests
import time

# response = requests.post(
#     'http://192.168.8.107:5000/ads/',
#     json={'heading':'test7', 'description':'test7', 'owner':'danila.dolgov.23555@gmail.com'}
#
# )
# print(response.text)

response = requests.post(
     'http://192.168.8.107:5000/letter/',
)



resp_data = response.json()
print(resp_data)
task_id = resp_data.get('task_id')
print(task_id)

response1 = requests.get(
     f'http://192.168.8.107:5000/letter/{task_id}'
)
print(response1.text)
time.sleep(3)

response1 = requests.get(
     f'http://192.168.8.107:5000/letter/{task_id}'
)
print(response1.text)
# response = requests.get(
#     'http://192.168.1.119:5000/ads/8',
# )

