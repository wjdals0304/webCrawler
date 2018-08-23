# -*- coding:utf-8 -*-

# 디비 처리,연결,해체 ,검색어 가져오기
import pymysql as my
# import sys
#
# reload(sys)
#
# sys.setdefaultencoding('utf-8')

class DBHelper:
    '''
    멤버변수 : 커넥션
    '''
    conn = None

    def __init__(self):
        self.db_init()


    def db_init(self):
        self.conn = my.connect(
            host='mydb.clnezy5ep2wb.us-east-2.rds.amazonaws.com',
            user='testdb',
            password='wjdals12',
            db='pythonDB',
            charset='utf8',
            cursorclass=my.cursors.DictCursor)


    def db_free(self):
        if self.conn:
            self.conn.close()


    def db_selectKeyword(self):
        rows = None
        with self.conn.cursor() as cursor:

           sql = "SELECT * FROM tbl_keyword;"
           cursor.execute(sql)
           rows = cursor.fetchall()


        return rows


    def db_insertCrawlingData(self,title,price,area,contents,keyword):
         with self.conn.cursor() as cursor:
               sql = '''
                   insert into tbl_crawlingData (title,price,area,contents,keyword) 
                   values ( %s, %s,%s,%s,%s)  
                   '''

               cursor.execute(sql,(title,price,area,contents,keyword))

         self.conn.commit()


if __name__ == '__main__':
    db = DBHelper()
    db.db_insertCrawlingData('[hello=]로마','212','ass','aaaa','로마')

    db.db_free()
