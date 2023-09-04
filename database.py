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

    def create_user(self, name: str, profile_pic: str):
        try:
            mycursor = self.mydb.cursor()
            sql = 'INSERT INTO user (name, profile_pic) VALUES (%s, %s)'
            
            if profile_pic:
                profile = self.convertToBinaryData(profile_pic)
                if profile is not None:
                    val = (name, profile)
                else:
                    val = (name, None)
            else:
                val = (name, None)
                
            mycursor.execute(sql, val)
            self.mydb.commit()
            print(f"User '{name}' created successfully.")
        except Error as e:
            print(f"Error creating user: {e}")
            self.mydb.rollback()

    def change_username(self, old_name: str, new_name: str):
        try:
            mycursor = self.mydb.cursor()
            check_sql = 'SELECT COUNT(*) FROM user WHERE name = %s'
            mycursor.execute(check_sql, (new_name,))
            count = mycursor.fetchone()[0]

            if count > 0:
                print(f"Username '{new_name}' is already in use.")
                return

            update_sql = 'UPDATE user SET name = %s WHERE name = %s'
            val = (new_name, old_name)
            mycursor.execute(update_sql, val)
            self.mydb.commit()
            print(f"Username changed from '{old_name}' to '{new_name}' successfully.")
        except Error as e:
            print(f"Error changing username: {e}")
            self.mydb.rollback()

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

