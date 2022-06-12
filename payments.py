# All the payment processing is done here

import requests
import hashlib

from global_init import TERM_PASS, PRICE


def sign(js):
    ''' Signs the request according to the Tinkoff API '''

    js["Password"] = TERM_PASS
    jsl = sorted(js.items())
    jss = "".join([x[1] for x in jsl])
    hash = hashlib.sha256(jss.encode('utf-8'))
    js["Token"] = hash.hexdigest()
    del js["Password"]
    return js


def get_link(terminalKey: str, orderId: str, amount: str):
    ''' Retrieves a payment link for the user to pay '''

    headers = {'Content-type': 'application/json'}
    parms = {"TerminalKey": terminalKey,
             "OrderId": orderId,
             "Amount": amount,
             "Receipt": {
                 "Email": "fundstrat@yandex.ru",
                 "Taxation": "usn_income_outcome",
                 "Items":
                 [
                     {
                         "Name": "Подписка Fundstrat GA Россия - 1 месяц",
                         "Price": f"{PRICE}",
                         "Amount": f"{PRICE}",
                         "Quantity": "1",
                         "Tax": "none"
                     }
                 ]
             }}
    r = requests.post('https://securepay.tinkoff.ru/v2/Init/',
                      json=parms,
                      headers=headers)

    return r.json()["PaymentURL"], r.json()["PaymentId"]


def get_status(terminalKey: str, paymentId: str):
    ''' Retrieves the status of the payment '''

    headers = {'Content-type': 'application/json'}
    parms = {"TerminalKey": terminalKey,
             "PaymentId": paymentId}

    r = requests.post('https://securepay.tinkoff.ru/v2/GetState',
                      json=sign(parms),
                      headers=headers)

    return r.json()["Status"]
