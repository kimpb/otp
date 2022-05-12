
import pymysql


sqlconn = pymysql.connect(host='localhost', user='root', password='123123', db='smartlock', charset='utf8')
cur = sqlconn.cursor()

sql = 'SELECT * FROM guestkey'
cur.execute(sql)

result = cur.fetchone()
print(result[0])

asd = 'asd'
print(asd)

sqlconn.close()