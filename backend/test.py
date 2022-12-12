import schedule
import time

def my_job():
    print("Sohaib Ahmad is phenominal")
    # Add your script here

schedule.every(1).minutes.do(my_job)

while True:
    schedule.run_pending()
    time.sleep(1)