import requests
import string
import random
import time
from threading import Thread


class StressTest:

    URL = "http://0.0.0.0:25192/picker/pick/{0}/{1}"
    users = []
    for i in range(500):
        users.append(''.join(random.choices(string.ascii_lowercase, k=5)))

    def run(self):
        for tmp in range(100):
            campaign_id = random.randint(1, 50)
            username = random.randint(0, 499)
            r = requests.get(url=self.URL.format(campaign_id, self.users[username]))
            if not r.ok:
                print(r)


if __name__ == "__main__":
    my_class = StressTest()

    threads = []

    start_time = int(time.time())
    for i in range(10):
        thread = Thread(target=my_class.run)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    finish_time = int(time.time())
    print("Stress test finished in {} seconds".format(finish_time - start_time))
