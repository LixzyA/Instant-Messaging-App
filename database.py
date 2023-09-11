import pymysql
import sqlalchemy
import sqlalchemy.orm
from sqlalchemy import Column, Integer, String, BLOB, TEXT
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from google.cloud.sql.connector import Connector, IPTypes
from google.oauth2 import service_account


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

class Base(sqlalchemy.orm.DeclarativeBase):
    pass

class user(Base):
    __tablename__ = 'user'
    user_id :Mapped[int]= mapped_column(Integer, autoincrement=True, nullable= False,primary_key= True)
    name: Mapped[str] = mapped_column(String)
    profile_pic: Mapped[BLOB] = mapped_column(BLOB)

class chatroom(Base):
    __tablename__= 'chatroom'
    room_id : Mapped[int] = mapped_column(Integer, autoincrement=True, nullable= False, primary_key=True)
    room_type :Mapped[int] = mapped_column(Integer)
    creator_id :Mapped[int] = mapped_column(sqlalchemy.ForeignKey(user.user_id))

class friends(Base):
    __tablename__ = 'friends'
    friend_id : Mapped[int] = mapped_column(sqlalchemy.ForeignKey(user.user_id), primary_key=True)
    user_id : Mapped[int] = mapped_column(sqlalchemy.ForeignKey(user.user_id), primary_key=True)

class messages(Base):
    __tablename__ = 'messages'
    message : Mapped[TEXT] = mapped_column(TEXT)
    message_id : Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True, autoincrement=True)
    room_id : Mapped[int] = mapped_column(sqlalchemy.ForeignKey(chatroom.room_id))
    user_id : Mapped[int] = mapped_column(sqlalchemy.ForeignKey(user.user_id))
    
class participants(Base):
    __tablename__ = 'participants'
    room_id : Mapped[int] = mapped_column(sqlalchemy.ForeignKey(chatroom.room_id), primary_key=True)
    user_id : Mapped[int] = mapped_column(sqlalchemy.ForeignKey(user.user_id), primary_key=True)

class DB:

    def __init__(self) -> None:
        self.mydb = connect_with_connector()
        try:
            self.connection = self.mydb.connect()
            print('success connecting')
        except:
            print('failed to connect')

    def create_user(self, name: str, profile_pic:str) -> str:
        result = self.check_username_if_exists(name)
        profile = open(profile_pic, 'rb').read()
        # new username doesn't exist, can make new account
        if not result:
            stmt = sqlalchemy.insert(user).values(name =name, profile_pic =profile)
            res = self.connection.execute(stmt)
            self.connection.commit()
            return 'Success creating account'
        # else username already exist
        else:
            return 'Username already exist'
        
    def get_id_name_from_user(self, name:str):
        session = sqlalchemy.orm.Session(self.mydb)
        result = session.query(user).where(user.name.in_([name])).first()
        return result
        
        #False = username doesn't exist
        #True  = username exist
    def check_username_if_exists(self, username_str) -> bool:
        session = sqlalchemy.orm.Session(self.mydb)
        result = session.query(user).where(user.name.in_([username_str])).first() is not None
        return result

    def change_username(self, old_name: str, new_name: str):
        exist = self.check_username_if_exists(new_name)
        
        if not exist:
            id = self.get_id_name_from_user(old_name).user_id
            stmt = sqlalchemy.update(user).where(user.user_id == id).values(name = new_name)
            self.connection.execute(stmt)
            self.connection.commit()
            return 'Success'
        else:
            return 'Username already exist'

    def change_profile(self, name: str, new_profile:str):
        exist = self.check_username_if_exists(name)

        profile = open(new_profile, 'rb').read()
        if exist:
            id = self.get_id_name_from_user(name).user_id
            stmt = sqlalchemy.update(user).where(user.user_id == id).values(profile_pic = profile)
            self.connection.execute(stmt)
            self.connection.commit()
            return 'Success'
        else:
            return 'Account doesn\'t exists'


    def create_chatroom(self, chatroom_name: str, room_type: int, creator_id: int):
        stmt = sqlalchemy.insert(chatroom).values(chatroom_name = chatroom_name, room_type = room_type, creator_id = creator_id)
        self.connection.execute(stmt)
        self.connection.commit()
        return 'success'
    
    def list_friend(self, name:str) -> list:
        session = sqlalchemy.orm.Session(self.mydb)
        result = session.query(user).where(user.name.in_([name])).first()
        user_id = result.user_id

        result = session.query(friends).where(friends.user_id.in_([user_id])).all()
        return result

    def add_friend(self, user_name: str, friend_name: str):
        session = sqlalchemy.orm.Session(self.mydb)
        result = session.query(user).where(user.name.in_([user_name])).first()
        user_id = result.user_id
        
        result = session.query(user).where(user.name.in_([friend_name])).first()
        if result is not None:
            friend_id = result.user_id
        else:
            return 'Friend doesn\'t exist'

        try:
            stmt1 = sqlalchemy.insert(friends).values(user_id = user_id, friend_id =  friend_id)
            stmt2 = sqlalchemy.insert(friends).values(user_id = friend_id, friend_id =  user_id)
            self.connection.execute(stmt1)
            self.connection.execute(stmt2)
            self.connection.commit()
            return 'Success adding friend'
        except:
            return 'Error adding friend'


        
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



if __name__ == '__main__':
    mydb = DB()
    # mydb.add_friend('lixzy', 'Felix')
    # mydb.create_user('', '')
    # res = mydb.change_username('lix', 'lixzy')

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
