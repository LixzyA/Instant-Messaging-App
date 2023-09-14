import mysql.connector
import logging

class DB:

    def __init__(self) -> None:
        self.mydb = mysql.connector.connect(
            host ='barudak.covg8lehzfxt.ap-northeast-2.rds.amazonaws.com',
            user ='admin',
            password = 'admin123',
            database = 'barudak'
        )

    def convertToBinaryData(self, filename):
    # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData

    def create_user(self, name: str, profile_pic:str):
        found = self.check_username_if_exists(name)
        try:
            if not found:
                #need to check if name already exists
                sql = 'INSERT INTO user (name, profile_pic) values (%s, %s)'
                
                if profile_pic not in [None, ' ', '']:
                    profile = self.convertToBinaryData(profile_pic)
                    val = (name, profile)
                else:
                    val = (name, None)
                
                mycursor = self.mydb.cursor()
                mycursor.execute(sql, val)
                self.mydb.commit()
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False
        
    def check_username_if_exists(self, username_str):
        mycursor = self.mydb.cursor(buffered=True)
        sql = 'SELECT name FROM user where name = %s'
        val = (username_str,)
        mycursor.execute(sql, val)

        for (name, ) in mycursor:
            if name == username_str:
                return True
        return False

    def change_username(self, old_name: str, new_name: str):
        #check if new_name is already used
        found = self.check_username_if_exists(new_name)

        if not found:
            mycursor = self.mydb.cursor()
            sql = 'UPDATE user SET name = %s WHERE name = %s'
            val = (new_name, old_name)
            mycursor.execute(sql, val)
            self.mydb.commit()
            return True
        else:
            return False
    
    def get_profile(self, name:str):
        cursor = self.mydb.cursor()
        sql = 'SELECT name, profile_pic FROM user WHERE name = %s'
        val = (name,)
        cursor.execute(sql,val)
        
        for (name, profile) in cursor:
            profile_pic = profile
        return profile_pic

    
    def change_profile(self, name: str, new_profile):
        try:
            mycursor = self.mydb.cursor()
            # profile = self.convertToBinaryData(new_profile)
            sql = 'UPDATE user SET profile_pic = %s WHERE name = %s'
            val = (new_profile, name)

            mycursor.execute(sql, val)
            self.mydb.commit()
            return True
        except Exception as e:
            log.exception(e)
            return False

    def add_friend(self, user_name:str, friend_name:str):
        #check user_id and friend_id
        sql = 'SELECT name, user_id FROM user WHERE name = %s'
        val =(user_name,)
        mycursor = self.mydb.cursor()
        mycursor.execute(sql, val)

        for (name, id) in mycursor:
            user_id = id

        val =(friend_name,)
        mycursor.execute(sql, val)

        friend_id = None
        for (name, users_id) in mycursor:
            friend_id = users_id

        if friend_id not in ['', None]:
            # check if they are already added
            sql = 'SELECT COUNT(*) from friends where user_id = %s AND friend_id = %s'
            val = (user_id, friend_id)
            mycursor.execute(sql,val)
            result = mycursor.fetchone()

            if result[0] < 1 and friend_id != user_id:
                sql = 'INSERT IGNORE INTO friends(user_id, friend_id) values (%s, %s)'
                val = (user_id, friend_id)
                mycursor.execute(sql,val)
                val = (friend_id, user_id)
                mycursor.execute(sql,val)
                self.mydb.commit()

            return True
        
        else:
            return False

    def list_friend(self, name:str):
        sql = 'SELECT name, user_id FROM user WHERE name = %s'
        val = (name,)
        cursor = self.mydb.cursor()
        cursor.execute(sql,val)

        for (name, id) in cursor:
            user_id = id
        
        sql = '''SELECT user.name, friends.friend_id from friends INNER JOIN user ON 
        friends.friend_id = user.user_id WHERE friends.user_id = %s
        '''
        val = (user_id, )
        cursor.execute(sql,val)

        ls = []
        for (name, id) in cursor:
            ls.append(name)
        
        return ls

    def create_chatroom(self, chatroom_name: str, room_type: int, participants: list):
        #check if chatroom already exist
        sql = 'SELECT * FROM chatroom WHERE '

        mycursor = self.mydb.cursor()
        sql = 'INSERT INTO chatroom (room_name, room_type) values (%s, %s)'
        val = (chatroom_name, room_type)
        mycursor.execute(sql, val)
        self.mydb.commit()

    def get_room_list(self, name:str):
        cursor = self.mydb.cursor()
        sql = 'SELECT room_id FROM user where name = %s JOIN participants ON user.user_id = participants.user_id'
        cursor.execute(sql, (name, ))
        pass

    def send_message(self, message: str, room_name: str, user_name: str):
        mycursor = self.mydb.cursor()
        sql = 'SELECT name, user_id FROM user'
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        foundUser = False
        foundChat = False

        for tuples in myresult:
            if user_name in tuples[0]:
                user_id, name = tuples
                foundUser = True

        myresult  = self.get_room_name()
        for tuples in myresult:
            if room_name in tuples[1]:
                room_id, room_name = tuples 
                foundChat = True

        if foundUser and foundChat:
            mycursor = self.mydb.cursor()
            sql = 'INSERT INTO message(message, message_id, room_id, user_id) values (%s, %s, %s, %s)'
            val = (message, room_id, user_id)
            mycursor.execute(sql, val)
            self.mydb.commit()
            return 'Success'

        elif not foundUser:
            return 'User doesn\'t exist'
        else:
            return 'Chat doesn\'t exist'

    def show_message(self, chat_room_id: int):
        mycursor = self.mydb.cursor()
        sql = 'SELECT message FROM messages WHERE room_id = %s'
        val = (chat_room_id, )
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()

        for x in myresult:
            pass

    def add_participants(self, room_id: int, user_id: int):
        mycursor = self.mydb.cursor()
        sql = 'INSERT INTO participants(room_id, user_id) values (%s, %s)'
        val = (room_id, user_id)
        mycursor.execute(sql, val)
        self.mydb.commit()

    def show_participants_in_chat_room(self, room_id: int):
        mycursor = self.mydb.cursor()
        sql = 'SELECT user_id FROM participants WHERE room_id = %s'
        val = (room_id, )
        
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()

        for x in myresult:
            print(x)


    def delete(self,):
        sql = 'DELETE FROM friends'
        cursor = self.mydb.cursor()
        cursor.execute(sql)
        self.mydb.commit()

log = logging.getLogger()
if __name__ == '__main__':
    mydb = DB()
    print(mydb.check_username_if_exists('jotin'))
    # # mydb.create_user('lix', 'Resources/profile.png')
    # res = mydb.create_user('Juan', '')
    # print('create user', res)
    # res = mydb.add_friend('Felix', 'Juan')
    
    # # print('adding friend', res)
    # ls = mydb.list_friend('Felix')
    # print(ls)
'''
chatroom = (room_id auto_increment, room_type, creator_id)
user = (user_id, name, profile_pic)
friends = (friend_id, user_id)
messages = (message, message_id auto_increment, room_id, user_id)
participants = (room_id, user_id)

room_type = 1 = group chat
room_type = 0 = private chat / one on one
room_id primary key, creator_id foreign key references user(user_id) ->chatroom
user_id, friend_id foreign key reference user(user_id) -> friends
room_id foreign key references chatroom(room_id), user_id foreign key references user(user_id) -> messages
room_id foreign key references chatroom(room_id),  user_id foreign key reference user(user_id) -> participants

'''
