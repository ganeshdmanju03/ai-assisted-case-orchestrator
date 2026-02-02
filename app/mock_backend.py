import random
import time

def call_partner_api():
    # Simulate network call + occasional failure
    time.sleep(0.2)
    return random.random() < 0.75  # 75% success