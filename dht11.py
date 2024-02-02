import requests
import json
import psycopg2
import pandas as pd
import time
import datetime

# Thông tin cần thiết
USERNAME_ACCOUNT = "tenant@thingsboard.org"
PASSWORD_ACCOUNT = "tenant"
SCHEDULE_MINUTE = 10
TIME_RANGE = SCHEDULE_MINUTE * 60
END_TS = int(time.time()) * 1000
START_TS = int(END_TS / 1000 - TIME_RANGE) * 1000
ENTITY_ID = "d4237b10-c17a-11ee-ae74-59dc5a1c945d"
TYPE = "DEVICE"
DATABASE = "weather"
USERNAME_DB = "postgres"
PASSWORD_DB = "postgres"
HOST = "localhost"
PORT = "5432"

# Chuyển đổi timestamp thành datetime
def calculate_date_time(timeseries):
    datetime_object = pd.to_datetime(timeseries, unit='ms')
    return datetime_object

# Đăng nhập và nhận access token
def get_access_token():
    url_login = "http://localhost:8080/api/auth/login"
    data_login = {'username': USERNAME_ACCOUNT, 'password': PASSWORD_ACCOUNT}
    headers_login = {'accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.post(url_login, headers=headers_login, data=json.dumps(data_login))
    data = json.loads(response.text)
    token = data['token']
    print("TOKEN IS: ")
    print("======================================================================================")
    print(token)
    print("======================================================================================")
    return token

# Lấy dữ liệu từ ThingsBoard API
def get_data(start_ts, end_ts, entity_id, type, token):
    url_get_data = f"http://localhost:8080/api/plugins/telemetry/{type}/{entity_id}/values/timeseries"
    querystring = {"keys": "outsideHumidity,outsideTemp", "startTs": start_ts, "endTs": end_ts}
    headers_get_data = {"accept": "application/json", "X-Authorization": "Bearer " + token}
    response = requests.request("GET", url_get_data, headers=headers_get_data, params=querystring)
    data = json.loads(response.text)
    print("DATA IS: ")
    print(data)
    print("======================================================================================")
    return data

# Gửi dữ liệu vào cơ sở dữ liệu PostgreSQL
def send_data_to_database(data, database, user, password, host, port):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    outsideHumidityArr = data.get('outsideHumidity', [])
    outsideTempArr = data.get('outsideTemp', [])

    for i in range(len(outsideHumidityArr)):
        cur.execute("""
            INSERT INTO "weatherData"("dateTime", "outsideHumidity", "outsideTemp") VALUES (%s, %s, %s);
            """,
            (calculate_date_time(outsideHumidityArr[i]['ts']), outsideHumidityArr[i]['value'], outsideTempArr[i]['value']))

    conn.commit()
    cur.close()
    conn.close()
    print("SUCCESS: SEND DATA TO DATABASE!!!")
    print("======================================================================================")

# Hàm tạo bảng trong cơ sở dữ liệu
def create_database_table(database, user, password, host, port):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS weatherData (
            id SERIAL PRIMARY KEY,
            dateTime TIMESTAMP,
            outsideHumidity FLOAT,
            outsideTemp FLOAT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# Hàm xóa bảng từ cơ sở dữ liệu
def drop_database_table(database, user, password, host, port):
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    cur.execute("""
        DROP TABLE IF EXISTS weatherData;
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("SUCCESS: DROPPED TABLE!!!")
    print("======================================================================================")

# Chạy một lần để tạo bảng (chỉ cần chạy một lần)
create_database_table(DATABASE, USERNAME_DB, PASSWORD_DB, HOST, PORT)

if __name__ == "__main__":
    start_ts = START_TS
    end_ts = END_TS
    entity_id = ENTITY_ID
    type = TYPE
    database = DATABASE
    user = USERNAME_DB
    password = PASSWORD_DB
    host = HOST
    port = PORT

    while True:
        now = "NOW: " + str(str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))
        minute_left = "DATA WILL BE GOT IN: " + str(SCHEDULE_MINUTE - 1 - datetime.datetime.now().minute % SCHEDULE_MINUTE) + " minutes"
        print(now + " || " + minute_left, end="\r", flush=True)
        
        if (datetime.datetime.now().minute % SCHEDULE_MINUTE == 0):
            print("SEND DATA AT: " + str(datetime.datetime.utcnow()))
            token = get_access_token()
            data = get_data(start_ts=start_ts, end_ts=end_ts, entity_id=entity_id, type=type, token=token)
            
            if len(data) != 0:
                send_data_to_database(data=data, database=database, user=user, password=password, host=host, port=port)
            
            time.sleep(60)
