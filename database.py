import mysql.connector

class DB:

    def __init__(self) -> None:
        self.mydb = mysql.connector.connect(
            host="sql12.freesqldatabase.com",
            user="sql12643810",
            password="9K6hCbWQfH",
            database='sql12643810'
        )

    def show_table(self):
        # self.cursor()
        mycursor = self.mydb.cursor()
        mycursor.execute('SHOW TABLES')
        for i in mycursor:
            print(i)

    def convertToBinaryData(self, filename):
    # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData

    def create_user(self, name: str, profile_pic:str):
        mycursor = self.mydb.cursor()
        sql = 'INSERT INTO user (name, profile_pic) values (%s, %s)'
        
        if profile_pic:
            profile = self.convertToBinaryData(profile_pic)
            val = (name, profile)
        else:
            val = (name, None)
            
        mycursor.execute(sql, val)
        self.mydb.commit()


    def print_table(self, table_name: str):
        sql = 'SELECT * FROM '+ table_name
        mycursor = self.mydb.cursor()
        mycursor.execute(sql)

        myresult = mycursor.fetchall()
        for x in myresult:
            print(x) 

    def create_chatroom(self, name):
        pass


if __name__ == '__main__':
    mydb = DB()
    # mydb.create_user('lix', 'Resources/profile.png')
    # mydb.print_table('user')

