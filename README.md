# Sensor-Xuan-Thuy
DHT11 to ThingsBoard and getData from ThingsBoard to Database

#CREATE DATABASE 
CREATE TABLE IF NOT EXISTS "weatherData" (
    id SERIAL PRIMARY KEY,
    "dateTime" TIMESTAMP,
    "outsideHumidity" FLOAT,
    "outsideTemp" FLOAT
);

`Chương trình python dùng để get dữ liệu từ ThingsBoard thông qua API, sau đó lưu dữ liệu vào PostgreSQL`
# Khai báo biến và hằng số
- `import requests` : Thư viện requests để gửi các yêu cầu HTTP.
- `import json` : Thư viện json để làm việc với dữ liệu JSON.
- `import psycopg2` : Thư viện psycopg2 để kết nối và làm việc với cơ sở dữ liệu PostgreSQL.
- `import pandas as pd` : Thư viện pandas với tên rút gọn là pd, sử dụng để chuyển đổi dữ liệu timestamp thành datatime.
- `import time` : Thư viện time để làm việc với thời gian.
- `import datatime` : Thư viện datatime để làm việc với đối tượng ngày giờ.
- `USERNAME_ACCOUNT = "tenant@thingsboard.org"`: Đây là một biến hằng số, chứa tên người dùng (username) của tài khoản ThingsBoard.
- `PASSWORD_ACCOUNT = "tenant"`: Một biến hằng số, chứa mật khẩu (password) của tài khoản ThingsBoard.
- `SCHEDULE_MINUTE = 10` : Một biến hằng số, xác định thời gian (tính bằng phút) giữa các lần lấy dữ liệu từ ThingsBoard.
- `TIME_RANGE = SCHEDULE_MINUTE * 60` : Một biến hằng số, xác định khoảng thời gian (tính bằng giây) mà dữ liệu sẽ được lấy từ ThingsBoard.
- `END_TS = int(time.time()) * 1000` : Một biến, lấy thời gian hiện tại (dưới dạng timestamp Unix) và nhân với 1000 để chuyển sang miliseconds.
- `START_TS = int(END_TS / 1000 - TIME_RANGE) * 1000` : Một biến dùng để tính toán thời điểm bắt đầu lấy dữ liệu từ ThingsBoard, bằng cách lấy thời gian kết thúc trừ đi khoảng thời gian cần lấy.
- `ENTITY_ID = "ID DEVICE hoặc ENTITY bất kì trên ThingsBoard"` : Trong trường hợp này, thực thể là DEVICE.
- `TYPE = "DEVICE"` : Một biến hằng số dùng để xác định loại thực thể mà dùng để lấy dữ liệu ( Trong trường hợp này là DEVICE).
- `DATABASE = "weather"` : Một biến hằng số, `chứa tên của CSDL PostgreSQL` dùng để lưu trữ dữ liệu.
- `USERNAME_DB = "postgres"` : Một biến hằng số, chứa tên người dùng (username) CSDL.
- `PASSWORD_DB = "postgres"` : passwor CSDL.
- `HOST = "localhost"` : Biến hằng số chứa địa chỉ host của CSDL PostgreSQL (trong trường hợp này là PostgreSQL localhost.
- `PORT = "5432"` : Cổng kết nối đến CSDL PostgreSQL.

# Các hàm được sử dụng
```sh
# Chuyển đổi timestamp thành datetime
def calculate_date_time(timeseries):
    datetime_object = pd.to_datetime(timeseries, unit='ms')
    return datetime_object
```
- `def calculate_data_time(timeseries):` : Khai báo hàm `calculate_data_time` nhận đổi số `timeseries`, được sử dụng để chuyển đổi `timestamp` thành đối tượng `datatime`.
- `datatime_object = pd.to_datatime(timeseries, unit='ms')` : Trong hàm `calculate_data_time` , lane này sử dụng phương thức `to_datatime` của thư viện `pandas` để chuyển đổi `timeseries` (timestamp) từ đơn vị miliseconds thành đối tượng datatime va lưu vào biến `datatime_object`.
- `return datatime_object` : Trả về đối tượng `datatime` sau khi chuyển đổi.
```sh
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
```
- `def get_access_token():` : Khai báo một hàm get_access_token không nhận tham số, được sử dụng để đăng nhập vào hệ thống ThingsBoard và nhận access token.
- `url_login = "http://localhost:8080/api/auth/login"`: Định nghĩa biến url_login chứa URL để gửi yêu cầu đăng nhập.
- `data_login = {'username': USERNAME_ACCOUNT, 'password': PASSWORD_ACCOUNT}`: Tạo một từ điển data_login chứa thông tin tên người dùng và mật khẩu.
- `headers_login = {'accept': 'application/json', 'Content-Type': 'application/json'}` : Tạo một từ điển headers_login chứa các tiêu đề HTTP cần thiết cho yêu cầu đăng nhập.
- `response = requests.post(url_login, headers=headers_login, data=json.dumps(data_login))` : Gửi một yêu cầu POST đến URL đăng nhập với các tiêu đề và dữ liệu được chỉ định, và lưu kết quả trong biến response.
- `data = json.loads(response.text): Chuyển đổi dữ liệu JSON từ phản hồi thành một đối tượng Python sử dụng json.loads và lưu vào biến data.
- `token = data['token']` : Trích xuất access token từ dữ liệu JSON và lưu vào biến token.
- `print("TOKEN IS: ")` : In ra thông báo "TOKEN IS:".
- `print("======================================================================================")`: In ra dòng gạch ngang để phân biệt.
- `print(token)`: In ra access token.
- `print("======================================================================================")` : In ra dòng gạch ngang để phân biệt.
- `return token` : Trả về access token.
```sh
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
```
- `def get_data(start_ts, end_ts, entity_id, type, token):` : Khai báo một hàm get_data nhận các tham số start_ts, end_ts, entity_id, type, token, được sử dụng để lấy dữ liệu từ ThingsBoard.
- `url_get_data = f"http://localhost:8080/api/plugins/telemetry/{type}/{entity_id}/values/timeseries"` : Tạo URL để gửi yêu cầu lấy dữ liệu từ ThingsBoard dựa trên các tham số truyền vào.
- `querystring = {"keys": "outsideHumidity,outsideTemp", "startTs": start_ts, "endTs": end_ts}`: Tạo một từ điển querystring chứa thông tin về các khóa dữ liệu cần lấy và khoảng thời gian cần lấy dữ liệu.
- `headers_get_data = {"accept": "application/json", "X-Authorization": "Bearer " + token}` : Tạo một từ điển headers_get_data chứa các tiêu đề cần thiết cho yêu cầu lấy dữ liệu, bao gồm cả access token.
- `response = requests.request("GET", url_get_data, headers=headers_get_data, params=querystring)` : Gửi một yêu cầu GET đến URL lấy dữ liệu với các tiêu đề và tham số được chỉ định, và lưu kết quả trong biến response.
- `data = json.loads(response.text)`: Chuyển đổi dữ liệu JSON từ phản hồi thành một đối tượng Python và lưu vào biến `data`.
- `print("DATA IS: ")`: In ra thông báo "DATA IS:".
- `print(data)`: In ra dữ liệu đã nhận được.
- `print("======================================================================================")` : In ra dòng gạch ngang để phân biệt.
- `return data`: Trả về dữ liệu đã nhận được từ ThingsBoard
```sh
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
```
- `def send_data_to_database(data, database, user, password, host, port):`: Đây là khai báo một hàm có tên là send_data_to_database, nhận các tham số là data (dữ liệu cần gửi), database, user, password, host, và port (các thông tin cần thiết để kết nối đến cơ sở dữ liệu PostgreSQL).
- `conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)`: Thiết lập kết nối đến cơ sở dữ liệu PostgreSQL bằng cách sử dụng thông tin được cung cấp.
- `cur = conn.cursor()` : Tạo một đối tượng con trỏ (cursor) để thực thi các lệnh SQL trên kết nối đến cơ sở dữ liệu.
- `outsideHumidityArr = data.get('outsideHumidity', []) và outsideTempArr = data.get('outsideTemp', [])`: Lấy dữ liệu về độ ẩm và nhiệt độ từ biến data nếu có, nếu không có thì gán cho chúng một list rỗng.
- `for i in range(len(outsideHumidityArr)):` :Bắt đầu một vòng lặp qua các giá trị trong list outsideHumidityArr.
- `cur.execute("""INSERT INTO "weatherData"("dateTime", "outsideHumidity", "outsideTemp") VALUES (%s, %s, %s);""",` : thực thi một câu lệnh SQL để chèn dữ liệu vào bảng "weatherData" trong cơ sở dữ liệu. Câu lệnh này chèn giá trị của thời gian ("dateTime"), độ ẩm ("outsideHumidity"), và nhiệt độ  ("outsideTemp") từ biến data vào bảng.
- `(calculate_date_time(outsideHumidityArr[i]['ts']), outsideHumidityArr[i]['value'], outsideTempArr[i]['value']))` : Đây là các tham số được truyền vào trong câu lệnh SQL INSERT INTO. calculate_date_time(outsideHumidityArr[i]['ts']) được sử dụng để chuyển đổi timestamp ts thành đối tượng datetime. outsideHumidityArr[i]['value'] và outsideTempArr[i]['value'] là giá trị của độ ẩm và nhiệt độ tương ứng.
- `conn.commit()` : Gửi các thay đổi được thực hiện trong cơ sở dữ liệu và lưu chúng.
- `cur.close()` : Đóng con trỏ của đối tượng cursor.
- `conn.close()` : Đóng kết nối đến cơ sở dữ liệu.
- `print("SUCCESS: SEND DATA TO DATABASE!!!")` : In ra thông báo "SUCCESS: SEND DATA TO DATABASE!!!" để thông báo rằng dữ liệu đã được gửi thành công vào cơ sở dữ liệu.
- `print("======================================================================================")`: In ra một dòng ngăn cách để phân biệt giữa các thông báo.

```sh
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
```
- `def create_database_table(database, user, password, host, port):` : Khai báo một hàm create_database_table, nhận các đối số là database, user, password, host, và port. Chức năng của hàm này là tạo bảng "weatherData" trong cơ sở dữ liệu PostgreSQL nếu bảng chưa tồn tại.
- `conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)` : Tạo kết nối đến cơ sở dữ liệu PostgreSQL.
- `cur = conn.cursor()` : Tạo một đối tượng con trỏ (cursor) để thực thi các câu lệnh SQL.
- `cur.execute("""CREATE TABLE IF NOT EXISTS weatherData ( id SERIAL PRIMARY KEY, dateTime TIMESTAMP, outsideHumidity FLOAT, outsideTemp FLOAT );""")` : Thực thi một câu lệnh SQL để tạo bảng "weatherData" nếu bảng chưa tồn tại.
- `conn.commit()` : Xác nhận các thay đổi vào cơ sở dữ liệu.
- `cur.close()` : Đóng con trỏ (cursor).
- `conn.close()` : Đóng kết nối đến cơ sở dữ liệu.
```sh
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
```
- `def drop_database_table(database, user, password, host, port):` : Khai báo một hàm drop_database_table, nhận các đối số là database, user, password, host, và port. Chức năng của hàm này là xóa bảng "weatherData" khỏi cơ sở dữ liệu PostgreSQL.
- `cur.execute("""DROP TABLE IF EXISTS weatherData;""")` : Thực thi một câu lệnh SQL để xóa bảng "weatherData" nếu bảng tồn tại.
- `print("SUCCESS: DROPPED TABLE!!!")` : In ra thông báo khi bảng đã được xóa thành công.
- `print("======================================================================================")` : In ra một đường gạch ngang để phân biệt giữa các quá trình.
```sh
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
```
- `create_database_table(DATABASE, USERNAME_DB, PASSWORD_DB, HOST, PORT)` : Gọi hàm để tạo bảng trong cơ sở dữ liệu PostgreSQL. Hàm này được gọi một lần duy nhất khi ứng dụng được khởi động để đảm bảo rằng bảng cần thiết đã được tạo.
- `if __name__ == "__main__":` : Phương pháp phổ biến trong Python để kiểm tra xem tập tin đang được thực thi trực tiếp hay được import vào một tập tin khác.
- `Trong khối if __name__ == "__main__":`, chương trình tiếp tục thực thi các dòng bên dưới:
- `start_ts = START_TS, end_ts = END_TS, entity_id = ENTITY_ID, type = TYPE, database = DATABASE, user = USERNAME_DB, password = PASSWORD_DB, host = HOST, port = PORT` : Gán các giá trị cho các biến từ các hằng số được khai báo trước đó.
- Vòng lặp vô hạn `while True`: được sử dụng để lặp lại một số công việc với một tần suất nhất định.
- `now = "NOW: " + str(str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')))` : Tạo một chuỗi chứa thời gian hiện tại (theo giờ địa phương), định dạng theo "%Y-%m-%d %H:%M:%S".
- `minute_left = "DATA WILL BE GOT IN: " + str(SCHEDULE_MINUTE - 1 - datetime.datetime.now().minute % SCHEDULE_MINUTE) + " minutes"` : Tính thời gian còn lại cho việc lấy dữ liệu tiếp theo dựa trên biến SCHEDULE_MINUTE.
- `print(now + " || " + minute_left, end="\r", flush=True)` : In ra thời gian hiện tại và thời gian còn lại trước khi lấy dữ liệu tiếp theo.
- `if (datetime.datetime.now().minute % SCHEDULE_MINUTE == 0):` : Kiểm tra xem đã đến thời điểm để lấy dữ liệu mới chưa (dựa trên SCHEDULE_MINUTE).
- `print("SEND DATA AT: " + str(datetime.datetime.utcnow()))` : In ra thời điểm gửi dữ liệu vào cơ sở dữ liệu.
- `token = get_access_token()` : Nhận mã token để truy cập vào ThingsBoard.
- `data = get_data(start_ts=start_ts, end_ts=end_ts, entity_id=entity_id, type=type, token=token)` : Lấy dữ liệu từ ThingsBoard với các tham số đã được định nghĩa trước đó.
- `if len(data) != 0: send_data_to_database(data=data, database=database, user=user, password=password, host=host, port=port)` : Gửi dữ liệu nhận được từ ThingsBoard vào cơ sở dữ liệu PostgreSQL nếu có dữ liệu.
- `time.sleep(60)` : Dừng chương trình trong 60 giây (một phút) trước khi lặp lại quá trình, để đảm bảo rằng dữ liệu không được lấy quá nhanh.

# Cách chỉnh sửa chương trình khi thêm, bớt, sửa bảng trong database 
1. **Tên bảng và các cột:**

   Trong phần này, chúng ta thay đổi tên của bảng và tên của các cột nếu cần thiết. Ví dụ, nếu bạn muốn đổi tên bảng thành "dữ_liệu_thời_tiết" thay vì "weatherData", và bạn muốn thêm một cột mới gọi là "windSpeed", bạn sẽ làm như sau:

   ```python
   cur.execute("""
       CREATE TABLE IF NOT EXISTS dữ_liệu_thời_tiết (
           id SERIAL PRIMARY KEY,
           dateTime TIMESTAMP,
           outsideHumidity FLOAT,
           outsideTemp FLOAT,
           windSpeed FLOAT
       );
   """)
   ```

2. **Dữ liệu được lưu vào bảng:**

   Trong phần này, chúng ta thay đổi cách dữ liệu được chèn vào bảng. Nếu bạn đã thêm một cột mới như "windSpeed", bạn cần chắc chắn rằng bạn cũng chèn dữ liệu vào cột mới này. Ví dụ:

   ```python
   cur.execute("""
       INSERT INTO "dữ_liệu_thời_tiết"("dateTime", "outsideHumidity", "outsideTemp", "windSpeed") VALUES (%s, %s, %s, %s);
       """,
       (calculate_date_time(outsideHumidityArr[i]['ts']), outsideHumidityArr[i]['value'], outsideTempArr[i]['value'], windSpeedArr[i]['value']))
   ```

   - Trong ví dụ trên, "windSpeed" là tên cột mới và "windSpeedArr" là một danh sách chứa giá trị của cột này.

3. **Thông tin kết nối cơ sở dữ liệu:**

   Nếu thông tin kết nối đến cơ sở dữ liệu PostgreSQL của bạn thay đổi, bạn cần cập nhật các biến như `DATABASE`, `USERNAME_DB`, `PASSWORD_DB`, `HOST`, và `PORT` ở đầu chương trình để phản ánh những thay đổi này.

   ```python
   DATABASE = "tên_cơ_sở_dữ_liệu_mới"
   USERNAME_DB = "tên_người_dùng_mới"
   PASSWORD_DB = "mật_khẩu_mới"
   HOST = "địa_chỉ_host_mới"
   PORT = "cổng_mới"
   ```

   - Thay đổi các giá trị của các biến này để phản ánh thông tin kết nối mới đến cơ sở dữ liệu PostgreSQL của bạn.

Bằng cách thực hiện các điều chỉnh này, bạn có thể điều chỉnh chương trình để phản ánh các thay đổi trong cấu trúc bảng hoặc các yêu cầu của bạn về dữ liệu và kết nối cơ sở dữ liệu.
