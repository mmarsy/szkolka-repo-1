import requests

url = "https://math-questions.azurewebsites.net/api/http_trigger"
print(requests.post(url=url, json={'name': 'czym jest apriori?'}))
