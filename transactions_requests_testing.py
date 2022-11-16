import requests

my_app = "http://127.0.0.1:5000/"

header1 = {"Content-Type": "application/json"}

transactions = requests.post(
    my_app + "transaction/new",
    headers=header1,
    json={
        "sender": "d4ee26eee15148ee92c6cd394edd974e",
        "recipient": "recipient-address",
        "amount": 5
    }
)

history = requests.get(my_app + "chain")

print(history.json())

print(transactions.json())