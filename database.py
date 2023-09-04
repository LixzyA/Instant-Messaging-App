import mysql.connector

class DB:

    def __init__(self) -> None:
        self.mydb = mysql.connector.connect(
            host="sql12.freesqldatabase.com",
            user="sql12643810",
            password="9K6hCbWQfH",
            database='sql12643810'
        )

    def convertToBinaryData(self, filename):
    # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData

    def create_user(self, name: str, profile_pic:str):
        mycursor = self.mydb.cursor()
        #need to check if name already exists
        sql = 'INSERT INTO user (name, profile_pic) values (%s, %s)'
        
        if profile_pic:
            profile = self.convertToBinaryData(profile_pic)
            val = (name, profile)
        else:
            val = (name, None)
            
        mycursor.execute(sql, val)
        self.mydb.commit()

    def change_username(self, old_name: str, new_name: str):
        mycursor = self.mydb.cursor()
        #check if new_name is already used
        sql = 'UPDATE user SET name = %s WHERE name = %s'
        val = (new_name, old_name)
        mycursor.execute(sql, val)
        self.mydb.commit()
    
    def change_profile(self, name: str, new_profile:str):
        mycursor = self.mydb.cursor()
        profile = self.convertToBinaryData(new_profile)
        sql = 'UPDATE USER SET profile_pic = %s WHERE name = %s'
        val = (profile, name)
        
        mycursor.execute(sql, val)
        self.mydb.commit()


    def create_chatroom(self, chatroom_name: str, room_type: int, creator_id: int):
        mycursor = self.mydb.cursor()
        sql = 'INSERT INTO chatroom (room_name, room_type, creator_id) values (%s, %s, %s)'
        val = (chatroom_name, room_type, creator_id)
        
        mycursor.execute(sql, val)
        self.mydb.commit()

    def add_friend(self, user_id: int, friend_id: int):
        #check if friend_id exists
        mycursor = self.mydb.cursor()
        sql = 'INSERT INTO friends(user_id, friend_id) values (%s, %s)'
        val = (user_id, friend_id)

        mycursor.execute(sql, val)
        self.mydb.commit()

    def send_message(self, message: str, room_id: int, user_id: int):
        pass

    def print_table(self, table_name: str):
        sql = 'SELECT * FROM '+ table_name
        mycursor = self.mydb.cursor()
        mycursor.execute(sql)

        myresult = mycursor.fetchall()
        for x in myresult:
            print(x) 



if __name__ == '__main__':
    mydb = DB()
    # mydb.create_user('lix', 'Resources/profile.png')
    # mydb.print_table('user')

'''
chatroom = (room_id, room_name, room_type, creator_id)
user = (user_id, name, profile_pic)
friends = (friend_id, user_id)
messages = (message, message_id, room_id, user_id)
participants = (room_id, user_id)

room_type 1 = group chat
room_type 0 = private chat / one on one
'''
