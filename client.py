import socket #Sockets for network connection
import threading # for multiple proccess 
from tkinter import * #Tkinter Python Module for GUI 
from tkinter.ttk import * #Tkinter Python Module for GUI 
from tkinter import messagebox
from functools import partial
from PIL import Image, ImageTk

def read_csv(name:str):
    file = open(name, 'r').readline()
    return file.split(',')

class GUI:
    client_socket = None
    last_received_message = None
    
    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.name = None
        self.enter_text_widget = None
        self.join_button = None
        self.chat_selected = None
        self.friend_list = None
        self.login_form()
        

    def login_form(self):
        self.root.title("Socket Chat") 
        self.root.resizable(0, 0)
        self.root.geometry('700x350')

        self.frame = Frame(self.root)
        self.frame.place(relx=0.5, rely=0.5, anchor='center')
        self.e = Entry(self.frame)
        self.e.insert(0, 'Enter your username')
        self.e.pack()
        self.b = Button(self.frame, text='Login', command = self.login)
        self.b.pack()
        

    def login(self):
        if self.e.get() != 'Enter your username':
            self.name = self.e.get()
            self.e.destroy()
            self.b.destroy()
            self.frame.destroy()
            self.initialize_socket()
        else:
            Label(text='Username has to be unique!')

    def initialize_socket(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
            remote_ip = '127.0.0.1' # IP address 
            remote_port = 10319 #TCP port
            self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server
            self.initialize_gui()
            self.listen_for_incoming_messages_in_a_thread()
        except:
            frame = Frame().place(relx=0.5, rely=0.5, anchor='center')
            Label(frame, text='Failed to connect to server!').pack()
            Button(frame, text='Ok', command=self.quit).pack()
            

    def quit(self):
        self.root.destroy()
        self.client_socket.close()
        exit(0)

    def initialize_gui(self): # GUI initializer
        self.show_menu()
        self.show_friend()
        self.display_chat_box('Jisoo')
        self.display_chat_entry_box()
        
    def show_menu(self):
        menu = Frame(self.root)
        menu.pack(side='left')
        add_friend_image = Image.open('Resources/addfriend.png')  
        add_friend_image = add_friend_image.resize((30, 30))  
        add_friend_photo = ImageTk.PhotoImage(add_friend_image)
        add_friend_button = Button(menu, image=add_friend_photo, command=partial(self.add_friend, menu))
        add_friend_button.photo = add_friend_photo  
        add_friend_button.pack()
        #Exit Button
        exit_image = Image.open('Resources/log out button white.png')  
        exit_image = exit_image.resize((30, 30))
        exit_photo = ImageTk.PhotoImage(exit_image)
        exit_button = Button(menu, image=exit_photo, command=self.on_close_window)
        exit_button.image = exit_photo 
        exit_button.pack()



    def add_friend(self, menu):
        # Create a frame widget with a blue background
        frame1 = Frame(menu)
        frame1.pack(padx=20, pady=20)
        # Create an entry widget and assign it to a variable
        e = Entry(frame1)
        # Add the entry widget to the frame widget
        e.pack()

        name = []
        # Create a button widget and assign it to a variable
        b = Button(frame1, text='search', command=partial (self.submit, e, name))
        # Add the button widget to the frame widget
        b.pack()

        print(name)


    def submit(self, ent, var):
        var += ent.get()


    def save_friend(self, name:str):
        try:
            file = open('Data/friends.data', 'a')
            file.write('\n')
            file.write(name)
            file.close()
        except:
            file = open('Data/friends.data', 'a')
            file.write(name)
            file.close()
     

    def show_friend(self):
        friends = Frame(self.root)
        friends.pack(side='left', fill='both')

        try:
            self.friend_list = read_csv('data/friends.data')
            for friend in self.friend_list:
                button = Button(friends, text= friend, command=self.show_chat(friend))
                button.pack(anchor='n')
        except:
            friends.pack(side='left', fill='none')
            label = Label(friends, text = 'Add a friend').pack()

    def show_chat(self, name: str):
        pass
        
    def display_chat_box(self, name:str):
        self.chat_selected = name
        frame = Frame()
        Label(frame).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
        frame.pack(side='top')

        chat_history = None
        try:
            chat_history = open('data/Chat/' + name + '.data', 'r')
        except:
            pass
        

    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')
        
        
    
    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,)) # Create a thread for the send and receive in same time 
        thread.start()
    #function to recieve msg
    def receive_message_from_server(self, so):
        while True:
            buffer = so.recv(256)
            if not buffer:
                break
            message = buffer.decode('utf-8')
         
            if "joined" in message:
                user = message.split(":")[1]
                message = user + " has joined"
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)

        so.close()
    

    def on_join(self):
        # if len(self.name_widget.get()) == 0:
        #     messagebox.showerror(
        #         "Enter your name", "Enter your name to send a message")
        #     return
        # self.name_widget.config(state='disabled')
        self.client_socket.send(("joined:" + self.name).encode('utf-8'))

    def on_enter_key_pressed(self, event):
        # if len(self.name_widget.get()) == 0:
        #     messagebox.showerror("Enter your name", "Enter your name to send a message")
        #     return
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name + ": "
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data).encode('utf-8')
        self.chat_transcript_area.insert('end', message.decode('utf-8') + '\n')
        self.chat_transcript_area.yview(END)
        self.client_socket.send(message)
        self.enter_text_widget.delete(1.0, 'end')
        return 'break'

    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)
    

#the mail function 
if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
