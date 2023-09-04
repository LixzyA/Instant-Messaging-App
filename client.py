import socket #Sockets for network connection
import threading # for multiple proccess 
from tkinter import * #Tkinter Python Module for GUI 
from tkinter.ttk import * #Tkinter Python Module for GUI 
from tkinter import messagebox
import tkinter as tk
from tkinter import filedialog 
from functools import partial
from PIL import Image, ImageTk
from os import mkdir, stat, error
from os.path import join
import logging
import os

def read_csv(name:str):
    file = open(name, 'r').read()
    if len(file) > 0:
        return file.split('\n')
    else:
        return []

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
        self.friend_list_button = []
        self.login_form()
        self.friend_list = []  # Initialize the friend_list as an empty list
        self.add_contact_photo = None  # Initialize the add_contact_photo as None
    
        
    def on_entry_click(self, event): # Function to Clear the background text when clicked
        if self.e.get() == 'Enter your username':
            self.e.delete(0, tk.END)
            self.e.config(fg='black')


    def login_form(self):
        self.root.title("Socket Chat") 
        self.root.resizable(0, 0)
        self.root.geometry('300x420')
        self.root.configure(bg="white")

        label_font = ("ubuntu", 30)
        self.label = tk.Label(root, text="BARUDAK CHAT", bg="white", font = label_font)
        self.label.place(relx=0.5, rely=0.12, anchor='center')

        self.logo_image = Image.open('Resources/logo.png') 
        self.logo_image = self.logo_image.resize((130, 130))  
        self.logo_photo = ImageTk.PhotoImage(self.logo_image) 
        self.logo_label = tk.Label(root, image=self.logo_photo, bg="white")
        self.logo_label.place(relx=0.5, rely=0.385, anchor='center')

        
        self.frame = tk.Frame(self.root, bg="white")
        self.frame.place(relx=0.5, rely=0.7, anchor='center')
        self.e = tk.Entry(self.frame)
        self.e.insert(0, 'Enter your username')
        self.e.bind("<FocusIn>", self.on_entry_click)
        self.e.pack(pady=30)
        button_font = ("Times New Roman", 20)
        self.b = tk.Button(self.frame, text='Login', fg="white", padx=50, pady=1, font=button_font, command = self.login, bg="#4DD913")
        self.b.pack()
        

    def login(self):
        if self.e.get() not in ['Enter your username', '']:
            self.name = self.e.get()
            self.e.destroy()
            self.b.destroy()
            self.label.destroy()
            self.logo_label.destroy()
            self.frame.destroy()
            self.initialize_socket()
        else:
            Label(text='Username has to be unique!')

    
    def change_profile(self):
        new_name = self.e.get()
        if new_name.strip() == '':
            messagebox.showerror("Invalid Name", "Please enter a valid name.")
            return

        try:
            # Rename the user profile
            self.rename_profile(new_name)
            self.change_profile_image()  # Call the method to change profile image
        except Exception as e:
            logger.exception(str(e))
            messagebox.showerror("Profile Change Error", "An error occurred while changing the profile name.")
            
    def change_profile_image(self):
        # Implement logic to allow the user to select an image and save it
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        
    def rename_profile(self, new_name: str):
        try:
            old_profile_path = join('data/', self.name)
            new_profile_path = join('data/', new_name)
            
            os.rename(old_profile_path, new_profile_path)
            
            self.name = new_name
            self.root.title(f"Socket Chat - {self.name}")
            
            messagebox.showinfo("Profile Changed", f"Your profile has been changed to {new_name}.")
        except Exception as e:
            logger.exception(str(e))
            raise
        
    def initialize_socket(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # initialazing socket with TCP and IPv4
            global_ip = '34.64.225.225' # IP address
            remote_ip = '127.0.0.1' 
            global_port = 3389 #TCP port
            remote_port = 10319
            self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server
            self.initialize_gui()
            self.listen_for_incoming_messages_in_a_thread()
        except Exception as e:
            logger.exception(str(e))
            frame = Frame().place(relx=0.5, rely=0.5, anchor='center')
            Label(frame, text='Failed to connect to server!').pack()
            Button(frame, text='Quit', command=self.quit).pack()
            

    def quit(self):
        self.root.destroy()
        self.client_socket.close()
        exit(0)

    def initialize_gui(self): # GUI initializer
        self.root.geometry('800x400')
        self.show_menu()
        self.show_friend(0)
        if self.friend_list not in [None, []]:
            self.display_chat_box(self.friend_list[0])
            self.display_chat_entry_box()
        else:
            f = Frame()
            Label(f, text='Welcome to Barudak Chat!').pack()
            Label(f, text='Add a friend now to start Chatting!').pack()
            f.pack(expand=True)
        
    def show_menu(self):
        #Profile
        menu = Frame(self.root)
        menu.pack(side='left', padx=10, pady=10, fill='y')
        default_profile_image = Image.open('Resources/default_profile.png')  
        default_profile_image = default_profile_image.resize((40, 40))  
        self.profile_photo = ImageTk.PhotoImage(default_profile_image)
        profile_label = Label(menu, image=self.profile_photo)
        profile_label.pack()
        
        #Add friend Button
        add_friend_image = Image.open('Resources/addfriend.png')  
        add_friend_image = add_friend_image.resize((40, 40))  
        add_friend_photo = ImageTk.PhotoImage(add_friend_image)
        self.add_friend_button = Button(menu, image=add_friend_photo, command=partial(self.add_friend, menu))
        style = Style()
        style.configure("Gray.TButton", background="gray")  # Define a new style with gray background
        self.add_friend_button.configure(style="Gray.TButton")
        self.add_friend_button.photo = add_friend_photo  
        self.add_friend_button.pack(anchor='w')

        #Add Friend entry
        self.e = Entry(menu)
        self.b = tk.Button(menu, text='add', command=self.submit)


        # Setting Button
        setting_image = Image.open('Resources/setting button.png')
        setting_image = setting_image.resize((40, 40))
        setting_photo = ImageTk.PhotoImage(setting_image)
        setting_button = Button(menu, image=setting_photo, command=self.open_settings)
        style = Style()
        style.configure("Gray.TButton", background="gray")
        setting_button.configure(style="Gray.TButton")
        setting_button.image = setting_photo
        setting_button.pack(anchor='w')

        #Exit Button
        exit_image = Image.open('Resources/log out button white.png')  
        exit_image = exit_image.resize((40, 40))
        exit_photo = ImageTk.PhotoImage(exit_image)
        exit_button = Button(menu, image=exit_photo, command=self.on_close_window)
        style = Style()
        style.configure("Gray.TButton", background="gray", padding=(-3, -3, -3, -3))  # Define a new style with gray background
        exit_button.configure(style="Gray.TButton")
        exit_button.image = exit_photo 
        exit_button.pack(side='bottom', anchor='sw', pady=(0, 10))

        def on_button_hover(event):
            self.root.config(cursor='hand2')

        def on_button_leave(event):
            self.root.config(cursor='')  

        self.add_friend_button.bind("<Enter>", on_button_hover) 
        self.add_friend_button.bind("<Leave>", on_button_leave) 

        setting_button.bind("<Enter>", on_button_hover)  
        setting_button.bind("<Leave>", on_button_leave)  

        exit_button.bind("<Enter>", on_button_hover) 
        exit_button.bind("<Leave>", on_button_leave) 
        
    def add_friend(self, menu):
        self.add_friend_button['state'] = tk.DISABLED
        self.e.pack(side=TOP)
        self.b.pack(side=TOP)
        self.e.focus_set()
            
    def change_profile_image(self):
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        
        if file_path:
            new_image = Image.open(file_path)
            new_image = new_image.resize((40, 40))  # Resize to match the profile image size
            self.profile_photo = ImageTk.PhotoImage(new_image)
            profile_label = Label(self.root, image=self.profile_photo)
            profile_label.pack()

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        change_profile_button = Button(settings_window, text="Change Username", command=self.show_change_profile_window)
        change_profile_button.pack()
        
        change_image_button = Button(settings_window, text="Change Profile Image", command=self.change_profile_image)
        change_image_button.pack()

    def show_change_profile_window(self):
        change_profile_window = tk.Toplevel(self.root)
        change_profile_window.title("Change Username")

        new_name_label = Label(change_profile_window, text="Enter new username:")
        new_name_label.pack()
        
        self.e = Entry(change_profile_window)
        self.e.pack()
        
        change_button = Button(change_profile_window, text="Change", command=self.change_profile)
        change_button.pack()
        os._exit()
        
    # def on_enter(event):
    #     b.config(bg="#C4C4C4", fg="white")

    # def on_leave(event):
    #     b.config(bg="white", fg="black")

    def submit(self):
        name = self.e.get()
        if name.strip():  # Check if name is not empty or just spaces
            self.save_friend(name)
            self.e.delete(0, END)
            self.e.pack_forget()
            self.b.pack_forget()
            self.add_friend_button['state'] = tk.NORMAL

            # Add the new friend to the friend list without refreshing
            self.friend_list.append(name)

            # Create a new button for the new friend and add it to the GUI using pack
            new_friend_button = Button(self.friends_frame, text=name, command=partial(self.show_chat, name),
                                    padding=(20, 8, 20, 8), style="Custom.TButton", image=self.add_contact_photo,
                                    compound=LEFT)
            new_friend_button.image = self.add_contact_photo

            # Place the new friend button at the top of the friend list
            self.pack_before(new_friend_button, self.friend_list_button[0] if self.friend_list_button else None)
            self.friend_list_button.insert(0, new_friend_button)  # Update the friend list button list
    
    def save_friend(self, name:str):
        file = open('data/'+ self.name +'/friends.data', 'a')
        file.write(name + '\n')
        file.close()  
        
    def pack_before(self, widget, before_widget):
        # Function to pack a widget before another widget
        if before_widget is None:
            widget.pack(side='top', anchor='n')
        else:
            widget.pack(in_=before_widget.master, before=before_widget)
          
        
    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)
            
    def show_chat(self, friend_name):
        pass
    

    def show_friend(self, refresh: int):
        #refresh the friends frame
        if not hasattr(self, 'friends_frame'):
            self.friends_frame = Frame(self.root)
            self.friends_frame.pack(side='left', fill='both')

        style = Style()
        style.configure("Custom.TButton", font=("Verdana"), anchor='w')
        add_contact_image = Image.open("Resources\profile.png")
        add_contact_image = add_contact_image.resize((30, 30))
        self.add_contact_photo = ImageTk.PhotoImage(add_contact_image)

        # Clear existing friend buttons
        for button in self.friends_frame.winfo_children():
            button.destroy()

        if refresh == 0:
            try:
                if stat('data/' + self.name + '/friends.data').st_size != 0:
                    self.friend_list = read_csv('data/' + str(self.name) + '/friends.data')

                for friend in self.friend_list:
                    self.create_friend_button(friend)

            except FileNotFoundError as e:
                parent_dir = 'data/'
                dir = self.name
                path = join(parent_dir, dir)
                mkdir(path)
                open(path + '/friends.data', 'w')

            except:
                pass

        else:  # Refresh friend list based on updated data
            self.friend_list = read_csv('data/' + str(self.name) + '/friends.data')
            for friend in self.friend_list:
                self.create_friend_button(friend)
                
    def display_chat_box(self, friend_name):      
        pass
                
    def display_chat_entry_box(self):
        frame = Frame()
        Label(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w')
        self.enter_text_widget = Text(frame, width=60, height=3, font=("Serif", 12))
        self.enter_text_widget.pack(side='left', pady=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')
        
    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,))
        thread.start()

    def create_friend_button(self, friend_name):
        # Create a friend button based on the given name and add it to the friends_frame
        friend_button = Button(self.friends_frame, text=friend_name, command=partial(self.show_chat, friend_name),
                            padding=(20, 8, 20, 8), style="Custom.TButton", image=self.add_contact_photo,
                            compound=LEFT)
        friend_button.image = self.add_contact_photo
        friend_button.pack(anchor='n')
    

    def show_chat(self, name: str):
        chat_history = None
        try:
            file = open('data/' + self.name + '/' + name + '.chat')
            chat_history= file.readlines()
            file.close()
            print(chat_history)
            for chat in chat_history:
                self.chat_transcript_area.insert(INSERT, chat + '\n')
                self.chat_transcript_area.yview(END)

        except FileNotFoundError as e:
            logger.exception(str(e))
            path = 'data/' + self.name + '/' + name
            open(path +'.chat', 'x')
            self.show_chat(name)

    def save_chat(self):
        pass
        
    def display_chat_box(self, name:str): 
        self.chat_selected = name
        frame = Frame()
        Label(frame, text=self.chat_selected).pack(side='top', anchor='w')
        self.chat_transcript_area = Text(frame, width=60, height=10, font=("Serif", 12))
        scrollbar = Scrollbar(frame, command=self.chat_transcript_area.yview, orient=VERTICAL)
        self.chat_transcript_area.config(yscrollcommand=scrollbar.set)
        self.chat_transcript_area.bind('<KeyPress>', lambda e: 'break')
        self.chat_transcript_area.pack(side='left', padx=10)
        scrollbar.pack(side='right', fill='y')
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
                # user = message.split(":")[1]
                # message = user + " has joined"
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
    
logger = logging.getLogger() # for error logging
#the mail function 
if __name__ == '__main__':
    root = Tk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()