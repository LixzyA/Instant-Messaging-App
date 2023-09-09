import mysql.connector
import pymysql
import sqlalchemy
from google.cloud.sql.connector import Connector, IPTypes

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = 'barudak-chat:asia-northeast2:barudak'
    db_user = 'root'
    db_pass = 'barudak123'
    db_name = 'barudak'

    ip_type = IPTypes.PUBLIC

    connector = Connector(ip_type)

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    pool = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        # [START_EXCLUDE]
        # Pool size is the maximum number of permanent connections to keep.
        pool_size=5,
        # Temporarily exceeds the set pool_size if no connections are available.
        max_overflow=2,
        # The total number of concurrent connections for your application will be
        # a total of pool_size and max_overflow.
        # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
        # new connection from the pool. After the specified amount of time, an
        # exception will be thrown.
        pool_timeout=30,  # 30 seconds
        # 'pool_recycle' is the maximum number of seconds a connection can persist.
        # Connections that live longer than the specified amount of time will be
        # re-established
        pool_recycle=1800,  # 30 minutes
        # [END_EXCLUDE]
    )
    return pool


class DB:

    def __init__(self) -> None:
        self.mydb = connect_with_connector()

    def convertToBinaryData(self, filename):
    # Convert digital data to binary format
        with open(filename, 'rb') as file:
            binaryData = file.read()
        return binaryData

    def create_user(self, name: str, profile_pic:str):
        mycursor = self.mydb.cursor()
        sql = 'SELECT user_id, name from user'
        mycursor.execute(sql)
        myresult = mycursor.fetchall()

        found = False
        try:
            for tuple in myresult:
                if name in tuple:
                    found = True
            if not found:
                #need to check if name already exists
                sql = 'INSERT INTO user (name, profile_pic) values (%s, %s)'
                
                if profile_pic:
                    profile = self.convertToBinaryData(profile_pic)
                    val = (name, profile)
                else:
                    val = (name, None)
                    
                mycursor.execute(sql, val)
                self.mydb.commit()
                return 'success'
            else:
                return 'username already exists'
        except Exception as e:
            print(str(e))
            return 'error'
        
    def check_username_if_exists(self, username_str):
        sql = 'SELECT name FROM user'
        mycursor = self.mydb.cursor()
        mycursor.execute(sql)
        self.mydb.commit()

        myresult = mycursor.fetchall()
        if username_str in myresult:
            return True
        else:
            return False

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

    def add_friend(self, user_id: int, friend_name: str):
        mycursor = self.mydb.cursor()
        sql = 'SELECT user_id, name from user'
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        found = False

        for tuples in myresult:
            if friend_name in tuples[0]:
                mycursor = self.mydb.cursor()
                friend_id, name = tuples
                sql = 'INSERT INTO friends(user_id, friend_id) values (%s, %s)'
                val = (user_id, friend_id)
                mycursor.execute(sql, val)
                myresult = mycursor.fetchall()
                self.mydb.commit()
                found = True
        
        if not found:
            return 'Error'

    def get_room_name(self):
        mycursor = self.mydb.cursor()
        sql = 'SELECT room_id, room_name FROM chatroom'
        mycursor.execute(sql)
        my_result = mycursor.fetchall()
        return my_result

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
    mydb.print_table('user')

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
