import requests

# response = requests.get('http://127.0.0.1:8080/request_resource')
# print(response.json())

light_id = {}
light_id['Light Node'] = 'n4'
response = requests.post('http://127.0.0.1:8080/request_light_address', json=light_id) # request an address for the corresponding light that is arriving
print(response.json()['address'])