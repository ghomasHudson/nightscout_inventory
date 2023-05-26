from flask import Flask, render_template, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
import requests
import time
import json
from tinydb import TinyDB, Query
from tinydb.table import Document
import os
from datetime import datetime, timedelta
from decouple import config

app = Flask(__name__)

BASE_URL = config('NIGHTSCOUT_URL')
ACCESS_TOKEN = config('NIGHTSCOUT_ACCESS_TOKEN')
GLUCOSE_METER_DEVICE = config('GLUCOSE_METER_DEVICE')



if not os.path.exists("db.json"):
    db = TinyDB('db.json')
    timestamp_of_last_check = int((datetime.now() - timedelta(hours=10)).timestamp() * 1000)
    db.insert({
        "timestamp": timestamp_of_last_check,
        "inventory": {
            'needles': 0,
            'insulin_pens': {},
            'lancets': 0,
            'test_strips': 0,
        }
    })
else:
    db = TinyDB('db.json')


# Auth
access_token = 'token=' + ACCESS_TOKEN
response = requests.get(f'{BASE_URL}/api/v2/authorization/request/{access_token}')
jwt = response.json()['token']
headers = {'Authorization': f'Bearer {jwt}'}

#timestamp_of_last_check = int(time.time() * 1000) # current timestamp in ms

# FOR TESTING

def check_inventory():
    print("Check nightscout")

    el = db.all()[-1]
    doc = db.get(doc_id=el.doc_id)

    timestamp_of_last_check = doc["timestamp"]
    inventory = doc["inventory"]
    new_timestamp = int(time.time() * 1000)

    # treatments
    r = requests.get(f'{BASE_URL}/api/v3/treatments/history/{timestamp_of_last_check}', headers=headers)
    data = r.json()
    for treatment in data['result']:
        treatment["insulinInjections"] = json.loads(treatment["insulinInjections"])
        for injection in treatment['insulinInjections']:
            inventory['needles'] -= 1
            insulin_name = injection['insulin']
            if insulin_name in inventory['insulin_pens']:
                inventory['insulin_pens'][insulin_name] -= injection['units']

    # blood tests
    r = requests.get(f'{BASE_URL}/api/v3/entries/history/{timestamp_of_last_check}', headers=headers)
    data = r.json()
    for entry in data["result"]:
        if GLUCOSE_METER_DEVICE in entry["device"]:
            inventory['lancets'] -= 1
            inventory['test_strips'] -= 1

    # Update database
    db.insert(Document({
        "timestamp": new_timestamp,
        "inventory": inventory
    }, doc_id=new_timestamp))

scheduler = BackgroundScheduler()
scheduler.add_job(func=check_inventory, trigger="interval", seconds=20)
scheduler.start()

@app.route('/', methods=['GET'])
def index():
    el = db.all()[-1]
    doc = db.get(doc_id=el.doc_id)
    return render_template('index.html', inventory=doc["inventory"])

@app.route('/add_stock', methods=['POST'])
def add_stock():

    el = db.all()[-1]
    inventory = db.get(doc_id=el.doc_id)["inventory"]

    item = request.form.get('item')
    amount = int(request.form.get('amount'))
    insulin_name = request.form.get('insulin_name')

    if item == 'insulin_pens':
        if insulin_name in inventory[item]:
            inventory[item][insulin_name] += amount
        else:
            inventory[item][insulin_name] = amount
    else:
        inventory[item] += amount

    new_timestamp = int(time.time() * 1000)
    db.insert(Document({
        "timestamp": new_timestamp,
        "inventory": inventory
    }, doc_id=new_timestamp))

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
