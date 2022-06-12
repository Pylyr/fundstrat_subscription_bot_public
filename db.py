'''
Everything to do with pulling from and updating the database is here
I initially wrote everything in mysql,
But the client wanted the database on google sheets
Instead of syncing the existing mysql table to google sheets
I thought it would just be easier to quickly recode in entirely using gsheets API
'''

from dateutil.relativedelta import relativedelta
from google.oauth2 import service_account
from global_init import SCOPES, SERVICE_ACCOUNT_FILE, SPREADSHEET_ID
from googleapiclient.discovery import build
from datetime import datetime


credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets().values()

# I kept mysql functionality if one day I want to use it again

# connection = mysql.connector.connect(host='34.77.97.251',
#                                      database='subscriptions',
#                                      user='root',
#                                      password='subscriptions2022')

# cursor = connection.cursor()

# def get_expiration(id):
#     cursor.execute(f"SELECT valid_until FROM subscriptions WHERE id = {id};")
#     res = cursor.fetchall()
#     if len(res) != 1:
#         return False
#     expir = res[0][0]
#     return expir


# def valid(id):
#     expir = get_expiration(id)
#     if expir:
#         return expir >= datetime.date(datetime.now())
#     return False


# def add_user(id):
#     expr = datetime.date(datetime.now()) + relativedelta(months=1)
#     cursor.execute(
#         f"INSERT INTO subscriptions (id, valid_until) VALUES ({id}, '{expr}');")
#     connection.commit()


# def delete_user(id):
#     cursor.execute(f"DELETE FROM subscriptions where id = {id};")
#     connection.commit()


# def get_expired_list():
#     cursor.execute(
#         f"SELECT id FROM subscriptions WHERE valid_until > CURDATE();")
#     return [user[0] for user in cursor.fetchall()]

def get_expiration(id):
    ''' Retrieves the date of expiration of the user '''
    strid = str(id)
    response = sheet.get(spreadsheetId=SPREADSHEET_ID, range='main!A2:B').execute()
    rows = response.get('values', [])
    for row in rows:
        if not row:
            continue
        if row[0] == strid:
            date = datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S')
            return date
    return False


def valid(id):
    ''' Checks if the users expiration date has passed '''

    expir = get_expiration(id)
    if expir:
        return expir >= datetime.now()
    return False


def add_user(id):
    ''' Adds a user to the database '''

    response = sheet.get(spreadsheetId=SPREADSHEET_ID, range='main!A2:A').execute()
    rows = response.get('values', [])
    present = [str(id)] in rows
    expr = datetime.now() + relativedelta(months=1)
    expr = expr.replace(microsecond=0)
    expr = str(expr)
    res = {
        "majorDimension": "ROWS",
        "values": [[id, expr, 'FALSE']]
    }
    if present:
        idx = rows.index([str(id)])
        r = sheet.update(spreadsheetId=SPREADSHEET_ID, range=f'main!A{idx+2}',
                         valueInputOption="USER_ENTERED", body=res).execute()
    else:
        sheet.append(
            spreadsheetId=SPREADSHEET_ID, range='main!A:C', body=res, valueInputOption="USER_ENTERED").execute()


def get_expired_list():
    ''' Returns a list of users whose expiration date has passed '''

    response = sheet.get(spreadsheetId=SPREADSHEET_ID, range='main!A2:C').execute()
    rows = response.get('values', [])
    ids = [row[0] for row in rows]
    expired = []
    res = {
        "majorDimension": "ROWS",
        "values": [['TRUE']]
    }
    for row in rows:
        if datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S') < datetime.now() and row[2] == 'FALSE':
            idx = ids.index(row[0])
            r = sheet.update(spreadsheetId=SPREADSHEET_ID, range=f'main!C{idx+2}',
                             valueInputOption="USER_ENTERED", body=res).execute()
            expired.append(row[0])

    return expired
