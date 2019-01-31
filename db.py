from mysql.connector import connect

def connectDB(host='localhost',database='sab_pool_karo',user='root',password='1234',):
    return connect(host=host,database=database,user=user,password=password)