import requests
import string
import random
import time


users = []
for i in range(500):
    users.append(''.join(random.choices(string.ascii_lowercase, k=5)))

start_time = int(time.time())

URL = "http://0.0.0.0:25192/peaker/pick/{0}/{1}"
for i in range(5000):
    campaign_id = random.randint(1, 50)
    username = random.randint(0, 499)
    r = requests.get(url=URL.format(campaign_id, username))
    if not r.ok:
        print(r)

finish_time = int(time.time())

print("Stress test finished in {} seconds".format(finish_time-start_time))
