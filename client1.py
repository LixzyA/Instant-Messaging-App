import socket #Sockets for network connection
import threading # for multiple proccess 
from tkinter import * #Tkinter Python Module for GUI 
from tkinter.ttk import * #Tkinter Python Module for GUI 
from tkinter import messagebox
import tkinter as tk
from functools import partial
from PIL import Image, ImageTk
from os import mkdir, stat, error
from os.path import join
from tkinter import filedialog 
import logging
import os
from database import *
import customtkinter as ctk
from customtkinter import CTk
from copy import *
import io

CREATE_USER = 'CREATE USER '
LOGIN = 'LOGIN '
CHANGE_USERNAME = 'CHANGE USERNAME '
CHANGE_PROFILE = 'CHANGE PROFILE '
INIT_FRIEND = 'INIT FRIEND '
ADD_FRIEND = 'ADD FRIEND '
GET_PROFILE = 'GET PROFILE '
CREATE_GROUP = 'CREATE GROUP '
SEND_MESSAGE = 'SEND MESSAGE '
LIST_CHATROOM = 'LIST CHATROOM '


class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


        
    def show_chat(self):
        pass
        

class GUI:
    client_socket = None
    last_received_message = None
    
    def __init__(self, master):
        self.root = master
        self.chat_transcript_area = None
        self.name = None
        self.enter_text_widget = None
        self.join_button = None
        self.add_contact_photo = None  # Initialize the add_contact_photo as None
        self.settings_window = None
        self.chatroom_list = []
        ctk.set_appearance_mode('light')
        state = self.initialize_socket()
        if state.lower() == 'success':
            self.login_form()
        
    def on_entry_click(self, event): # Function to Clear the background text when clicked
        if self.e.get() == 'Enter your username':
            self.e.delete(0, tk.END)


    def login_form(self):
        self.root.title("Socket Chat") 
        self.root.resizable(0, 0)
        self.root.geometry('300x420')
        self.root.configure()

        label_font = ("Oswald", 30)
        self.label = ctk.CTkLabel(root, text="BARUDAK CHAT", font = label_font)
        self.label.place(relx=0.5, rely=0.12, anchor='center')

        self.logo_image = ctk.CTkImage(Image.open('Resources/logo.png'), size = (130,130))
        self.logo_label = ctk.CTkLabel(root, image=self.logo_image, text= '')
        self.logo_label.place(relx=0.5, rely=0.385, anchor='center')
        
        self.frame = ctk.CTkFrame(self.root, fg_color='transparent')
        self.frame.place(relx=0.5, rely=0.7, anchor='center')
        
        button_font = ("Times New Roman", 20)
        self.signup_button = ctk.CTkButton(self.frame, text='Signup', font=button_font, command = self.signup)
        self.signup_button.pack(padx=50, pady=1)
        self.login_button = ctk.CTkButton(self.frame, text='Login', font=button_font, command = self.login)
        self.login_button.pack(padx=50, pady=1)


    def signup(self):
        button_font = ("Times New Roman", 20)
        self.login_button.destroy()
        self.signup_button.destroy()
        self.e = ctk.CTkEntry(self.frame)
        self.e.insert(0, 'Enter your username')
        self.e.bind("<FocusIn>", self.on_entry_click)
        self.e.pack(pady=30)
        self.signup_button = ctk.CTkButton(self.frame, text='Sign up', font=button_font, command = self.sign_up)
        self.signup_button.pack(padx=50, pady=1)
    
    def sign_up(self):
            if self.e.get() not in ['Enter your username', '']:
                self.name = self.e.get()
                self.e.destroy()
                self.label.destroy()
                self.logo_label.destroy()
                self.frame.destroy()
                create_user_command = CREATE_USER + self.name
                self.client_socket.send(create_user_command.encode('utf-8'))

                wait = True
                while wait:
                    buffer = self.client_socket.recv(256)
                    message = buffer.decode('utf-8')
                    if message:
                        wait = False
                if 'SUCCESS' in message.upper():
                    self.initialize_gui()
                else:
                    messagebox.showerror(title='Error',message='Something went wrong\nRestart the app')
                    self.quit()
        
            else:
                ctk.CTkLabel(text='Username has to be unique!') 

    def login(self):
        button_font = ("Times New Roman", 20)
        self.signup_button.destroy()
        self.login_button.destroy()
        self.e = ctk.CTkEntry(self.frame)
        self.e.insert(0, 'Enter your username')
        self.e.bind("<FocusIn>", self.on_entry_click)
        self.e.pack(pady=30)
        self.login_button = ctk.CTkButton(self.frame, text='Login', font=button_font, command = self.log_in)
        self.login_button.pack(padx=50, pady=1)


    def log_in(self):
        if self.e.get() not in ['Enter your username', '']:
            self.name = self.e.get()
            self.e.destroy()
            self.label.destroy()
            self.logo_label.destroy()
            self.frame.destroy()
            login_user_command = LOGIN + self.name
            self.client_socket.sendall(login_user_command.encode('utf-8'))

            wait = True
            while wait:
                buffer = self.client_socket.recv(256)
                message = buffer.decode('utf-8')
                if message is not None:
                    wait = False
            if 'SUCCESS' in message.upper():
                self.initialize_gui()
            else:
                messagebox.showerror(title='Error',message='Something went wrong\nRestart the app')
                self.quit()

        else:
            ctk.CTkLabel(text='Username has to be unique!')

    
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
            
    def change_profile_image(self): # masih ada yang salah
        file_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg")])

        if file_path:
            new_image = ctk.CTkImage(Image.open(file_path), size = (40,40))
            # new_image = new_image.resize((40, 40))  # Resize to match the profile image size
            self.profile_photo = new_image
            profile_label = ctk.CTkLabel(self.root, image=self.profile_photo)
            profile_label.pack()
            image = open(file_path, 'rb').read()
            
            self.client_socket.sendall((self.name + ' ' + image).encode('utf-8'))
            
        
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
            remote_ip = '127.0.0.1' # IP address 
            remote_port = 10319 #TCP port
            self.client_socket.connect((remote_ip, remote_port)) #connect to the remote server
            return 'success'

        except Exception as e:
            logger.exception(str(e))
            frame = Frame().place(relx=0.5, rely=0.5, anchor='center')
            ctk.CTkLabel(frame, text='Failed to connect to server!').pack()
            ctk.CTkButton(frame, text='Quit', command=self.quit).pack()
            return 'failed'


    def quit(self):
        self.client_socket.close()
        self.root.destroy()
        exit(0)

    def initialize_gui(self): # GUI initializer
        
        self.chat_selected = None
        self.friend_list = None
        self.chatroom_list_button = []
        self.group_chat_button_list = []

        self.list_chatroom()
        init_friend_command = INIT_FRIEND + self.name
        self.client_socket.sendall(init_friend_command.encode('utf-8'))
        wait = True
        while wait:
            buffer = self.client_socket.recv(2048)
            message = buffer.decode('utf-8')
            if message:
                wait = False
        
        if message not in ['empty', ' ', None]:
            self.friend_list = message.split()
        else:
            self.friend_list = []
        print(self.friend_list)
        

        self.root.geometry('800x400')
        self.show_menu()
        self.show_friend(0)
        if self.chatroom_list not in [None, []]:
            self.display_chat_box(self.chatroom_list[0])
            self.display_chat_entry_box()
            self.listen_for_incoming_messages_in_a_thread()

        else:
            f = ctk.CTkFrame(self.root, fg_color= 'transparent', bg_color= 'transparent')
            ctk.CTkLabel(f, text='Welcome to Barudak Chat!', fg_color= 'transparent', bg_color= 'transparent').pack()
            ctk.CTkLabel(f, text='Add a friend now to start Chatting!', fg_color= 'transparent', bg_color= 'transparent').pack()
            f.pack(expand=True)
        
    def show_menu(self):
        #Profile
        menu = ctk.CTkFrame(self.root, fg_color='#575353')
        menu.pack(side='left', padx=10, pady=10, fill='y')
        
        get_profile_command = GET_PROFILE + self.name
        self.client_socket.sendall(get_profile_command.encode('utf-8'))

        wait = True
        while wait:
            buffer = self.client_socket.recv(16777215)
            message = buffer
            if message:
                wait = False
         
        if message not in [b'None', None, ' ', 'None']:
            image =  message
            default_profile_image = ctk.CTkImage(Image.open(io.BytesIO(image)), size=(40, 40))  
        else:
            image = 'Resources/default_profile.png'
            default_profile_image = ctk.CTkImage(Image.open(image), size=(40, 40))  

        
        self.profile_photo = default_profile_image
        profile_label = ctk.CTkLabel(menu, image=self.profile_photo, text= ' ', pady=5)
        profile_label.pack()
        
        #contact button
        contact_image = ctk.CTkImage(Image.open('Resources/contact button.png'),  size=(40, 40))   
        contact_photo = contact_image
        self.contact_button = ctk.CTkButton(menu, image=contact_photo, command=self.open_contact,text = '', fg_color= 'transparent', width=50,  hover_color="#B9B9B9")
        self.contact_button.photo = contact_photo  
        self.contact_button.pack(anchor='w')
        
        #Add friend Button
        add_friend_image = ctk.CTkImage(Image.open('Resources/addfriend.png'), size=(40, 40))   
        add_friend_photo = add_friend_image
        self.add_friend_button = ctk.CTkButton(menu, image=add_friend_photo, command=self.add_friend, text = '', fg_color= 'transparent', width=50,  hover_color="#B9B9B9")
        self.add_friend_button.photo = add_friend_photo  
        self.add_friend_button.pack(anchor='w')
        

        #Add Friend entry
        self.add_friend_entry = ctk.CTkEntry(menu)
        self.add_friend_button2 = ctk.CTkButton(menu, text='add', command=self.submit)


        # Setting Button
        setting_image = ctk.CTkImage(Image.open('Resources/setting button.png'), size=(40, 40))
        setting_photo = setting_image
        self.setting_button = ctk.CTkButton(menu, image=setting_photo, command=self.open_settings, fg_color='transparent', text='', width=50, hover_color="#B9B9B9")
        self.setting_button.image = setting_photo
        self.setting_button.pack(anchor='w')

        #Exit Button
        exit_image = ctk.CTkImage(Image.open('Resources/newexit.png'), size=(40, 40))
        exit_photo = exit_image
        self.exit_button = ctk.CTkButton(menu, image=exit_photo, command=self.on_close_window, fg_color='transparent', text='', width=50,  hover_color="#B9B9B9")
       
        self.exit_button.image = exit_photo 
        self.exit_button.pack(side='bottom', anchor='sw', pady=(0, 10))

        #Back Button
        back_image = ctk.CTkImage(Image.open('Resources/back.png'), size=(40, 40))
        back_photo = back_image
        self.back_button = ctk.CTkButton(menu, image=back_photo, command=self.back, fg_color='transparent', text='', width=50,  hover_color="#B9B9B9")
        self.back_button.pack(side='bottom', anchor='sw')


        def on_button_hover(event):
            self.root.config(cursor='hand2')

        def on_button_leave(event):
            self.root.config(cursor='')  

        self.add_friend_button.bind("<Enter>", on_button_hover) 
        self.add_friend_button.bind("<Leave>", on_button_leave) 

        self.setting_button.bind("<Enter>", on_button_hover)  
        self.setting_button.bind("<Leave>", on_button_leave)  

        self.exit_button.bind("<Enter>", on_button_hover) 
        self.exit_button.bind("<Leave>", on_button_leave) 

    def list_chatroom(self):
        chatroom_list_command = LIST_CHATROOM + self.name
        self.client_socket.sendall(chatroom_list_command.encode('utf-8'))

        wait = True
        while wait:
            buffer = self.client_socket.recv(2048)
            message = buffer.decode('utf-8')
            if message:
                wait = False

        if message.lower() not in ['empty']:
            self.chatroom_list += message.split(',')
            self.chat_selected = self.chatroom_list[0]

        else:
            self.chatroom_list = []
        
        print(self.chatroom_list)

    def back(self):
        self.flag=0
        self.add_group_flag=0
        self.scrollable_frame_clear()
        self.show_friend(1)

    def add_friend(self):
        self.add_group_flag=0
        self.scrollable_frame_clear()

        addfriend_image = ctk.CTkImage(Image.open('Resources/addfriend.png'), size=(100, 100))   
        addfriend_photo = addfriend_image

        self.add_friend_entry = ctk.CTkEntry(self.scrollable_frame)
        self.add_friend_button2 = ctk.CTkButton(self.scrollable_frame, text='add', command=self.submit)
        self.addfriendphoto_label = ctk.CTkLabel(self.scrollable_frame, image=addfriend_photo, corner_radius = 40, text= '', pady=5)
        self.addfriend_label = ctk.CTkLabel(self.scrollable_frame, text= "Find a New Friend!", corner_radius = 10, font = ("oswald", 14), text_color = "white", pady=5, fg_color="#575353")

        self.addfriend_label.pack(pady= 30)
        self.addfriendphoto_label.pack(pady= 30)
        self.add_friend_entry.pack(pady = 15)
        self.add_friend_button2.pack(side=TOP)
        self.add_friend_entry.focus_set()
        
    def add_group(self):
        if self.add_group_flag==0:
            self.add_group_flag=1
            self.group_member_list_checkbox = []
            self.member_list = []
            self.contact_window_clear()

            self.create_group_button = ctk.CTkButton(self.change_contact_window, text="Add to Group", text_color = "white", fg_color="#575353", font=("oswald", 20), width= 250, height=35, corner_radius=5, command=self.enter_group_name)
            self.create_group_button.pack()
            checked = StringVar()
            for x in range (len(self.friend_list)):
                friend = self.friend_list[x]
                self.checkbox = ctk.CTkCheckBox(self.change_contact_window, text=friend, command=lambda: self.add_group_member(checked.get()), variable = checked, onvalue=friend, offvalue="del "+friend)
                self.checkbox.pack()
                self.group_member_list_checkbox.append(self.checkbox)
            #self.create_group_button= ctk.CTkButton(self.scrollable_frame, text="Create New Group",anchor="s", command=self.enter_group_name)
            #self.create_group_button.pack(side='bottom', anchor = 'sw')

    def add_group_member(self, name:str):
        if "del " in name:
            self.member_list.remove(name.split(' ')[1])
        else:
            self.member_list.append(name)

    def enter_group_name(self):

        self.enter_group_name_window = ctk.CTkToplevel(self.change_contact_window)
        self.enter_group_name_window.geometry('240x336')
        self.enter_group_name_window.wm_transient(self.change_contact_window)

        enter_group_name_image = ctk.CTkImage(Image.open('Resources/addgroup.png'), size=(100, 100))   
        enter_group_name_photo = enter_group_name_image

        self.enter_group_name_entry = ctk.CTkEntry(self.enter_group_name_window)
        self.enter_group_name_button2 = ctk.CTkButton(self.enter_group_name_window, text='Create Group', command=self.create_group)
        self.enter_group_name_photo_label = ctk.CTkLabel(self.enter_group_name_window, image=enter_group_name_photo, corner_radius = 40, text= '', pady=5)
        self.enter_group_name_label = ctk.CTkLabel(self.enter_group_name_window, text= "Enter Group Name!", corner_radius = 10, font = ("oswald", 14), text_color = "white", pady=5, fg_color="#575353")

        self.enter_group_name_label.pack(pady= 20)
        self.enter_group_name_photo_label.pack(pady= 20)
        self.enter_group_name_entry.pack(pady = 10)
        self.enter_group_name_button2.pack(pady=10)
        self.enter_group_name_entry.focus_set()

    def create_group(self):
        self.add_group_flag=0
        group_name = self.enter_group_name_entry.get()
        display_group_name = group_name + ' (' + str(len(self.member_list)) +')'
        create_group_command = CREATE_GROUP + group_name + ' ' + ' '.join(self.member_list)
        self.client_socket.sendall(create_group_command.encode('utf-8'))
        self.scrollable_frame_clear()
        group_button = ctk.CTkButton(self.scrollable_frame, text= display_group_name, command=partial(self.show_chat, display_group_name), image = self.add_contact_photo,anchor='w' ,fg_color="transparent", text_color="black", hover_color="#B9B9B9")
        group_button.pack()
        self.group_chat_button_list.append(group_button)
        self.enter_group_name_window.destroy()
        self.change_contact_window.destroy()
        self.show_friend(1)
    
    def scrollable_frame_clear(self):
        _list = self.scrollable_frame.winfo_children()
        for item in _list :
            if item.winfo_children() :
                _list.extend(item.winfo_children())
        for item in _list:
            item.pack_forget() 

    def contact_window_clear(self):
        _list = self.change_contact_window.winfo_children()
        for item in _list :
            if item.winfo_children() :
                _list.extend(item.winfo_children())
        for item in _list:
            item.pack_forget() 
        
    def open_settings(self):
        
        old_name = self.name
        def change_label_text():
            self.settings_username.configure(text=self.name,  font=('Oswald',14))
            self.e.pack_forget()
            change_username_command = CHANGE_USERNAME + old_name + ' ' + self.name
            self.client_socket.send(change_username_command.encode('utf-8'))
            
        def move_button_and_add_entry():
            if self.flag==0:
                # Hide the button
                self.flag=1
                self.change_username_button.pack_forget()
                self.change_photo_button.pack_forget()

                # Create a new entry widget and pack it below the button
                self.e = ctk.CTkEntry(self.settings_window)
                self.e.insert(0, 'Enter new username')
                self.e.bind("<FocusIn>", self.on_entry_click)
                self.e.pack(pady=5)

                # Pack the button below the entry
                self.change_username_button.pack(pady=5)
                self.change_photo_button.pack(pady=5)
            else:
                self.e.pack_forget()
                self.flag=0
                if self.e.get() not in ["", "Enter new username"]:
                    self.name=self.e.get()
                    change_label_text()

        def change_photo():
             file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ppm *.pgm")])
             if file_path:
                compressed_image = Image.open(file_path)
                compressed_image = compressed_image.resize((100,100), inplace=True)
                compressed_image.save('profile_images/' + self.name + '.jpg', optimize=True, quality = 20)
                
                image = ctk.CTkImage(compressed_image)
                image.configure(size =(40,40))
                self.profile_photo=image
                photo = copy(self.profile_photo)
                self.profile_photo.configure(image=photo)
                self.profile_photo.image=photo

                photo2 = ctk.CTkImage(compressed_image)
                photo2.configure(size = (80,80))
                # photo2 = ctk.CTkImage(Image.open(file_path), size=(80,80))
                settings_profile_image=photo2
                self.settings_profile_photo.configure(image=settings_profile_image)
                self.settings_profile_photo.image=self.settings_profile_image

                binary = open('profile_images/' + self.name + '.jpg', 'rb').read()
                change_profile_command = (CHANGE_PROFILE + self.name)
                self.client_socket.sendall(change_profile_command.encode('utf-8'))
                self.client_socket.sendall(binary)

        self.flag=0
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = ctk.CTkToplevel(self.root)
            self.settings_window.title("Settings")
            self.settings_window.wm_transient(self.root)
            self.settings_window.protocol('WM_DELETE_WINDOW', self.close)
        else:
            self.settings_window.focus()  # if window exists focus it
        

        self.settings_profile_image=copy(self.profile_photo)
        self.settings_profile_image.configure(size = (80,80))
        self.settings_profile_photo=ctk.CTkLabel(self.settings_window,image=self.settings_profile_image, text = ' ')
        self.settings_profile_photo.pack(anchor="center")

        self.settings_username=ctk.CTkLabel(self.settings_window, text=self.name)
        self.settings_username.pack(pady=5)

        self.change_username_button = ctk.CTkButton(self.settings_window, text="Change Username", command=move_button_and_add_entry)
        self.change_username_button.pack(pady=10)

        self.change_photo_button = ctk.CTkButton(self.settings_window, text="Change Profile Picture", command=change_photo)
        self.change_photo_button.pack(pady=10)

    def show_change_profile_window(self):
        change_profile_window = ctk.CTkToplevel(self.root)
        change_profile_window.title("")
        change_profile_window.geometry("175x85")

        new_name_label = ctk.CTkLabel(change_profile_window, text="Enter new username:", text_color="#3d3938")
        new_name_label.pack()
        
        self.e = ctk.CTkEntry(change_profile_window)
        self.e.pack()
        
        change_button = ctk.CTkButton(change_profile_window, text="Change",text_color="#3d3938", command=self.change_profile, fg_color='transparent')
        change_button.pack()

    def submit(self):
        name = self.add_friend_entry.get()
        if name.strip():
            if len(name) > 11:
                messagebox.showerror("Error", "username does not exist")
            else:
                add_friend_command = (ADD_FRIEND + self.name + ' ' + name).encode('utf-8')
                self.client_socket.sendall(add_friend_command)

                wait = True
                while wait:
                    try:
                        if 'Friend add' in self.last_received_message:
                            wait = False
                            break
                    except:
                        pass
                print('add friend ', self.last_received_message)
                self.add_friend_entry.delete(0, END)
                self.add_friend_entry.pack_forget()
                self.add_friend_button2.pack_forget()
                self.addfriend_label.pack_forget()
                self.addfriendphoto_label.pack_forget()
                self.add_friend_button.configure(state='normal')

                if 'success' in self.last_received_message:
                    # perlu add semua button          
                    friend_button1 = ctk.CTkButton(self.scrollable_frame, text=name, command=partial(self.show_chat, name), image = self.add_contact_photo,anchor='w' ,fg_color="transparent", text_color="black", hover_color="#B9B9B9")
                    friend_button1.pack()
                self.chatroom_list_button = []

                for x in range (len(self.chatroom_list)):
                    friend=self.chatroom_list[x]
                    friend_button = ctk.CTkButton(self.scrollable_frame, text=friend, command=partial(self.show_chat, friend), image = self.add_contact_photo,anchor='w' ,fg_color="transparent", text_color="black", hover_color="#B9B9B9")
                    friend_button.pack()
                    self.chatroom_list_button.append(friend_button)
                
                if 'success' in self.last_received_message:
                    self.chatroom_list_button.append(friend_button1)
                    self.chatroom_list.append(name)
                
                self.last_received_message = ''


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

    def show_friend(self, refresh: int):
        # Create or refresh the friends frame
        add_contact_image = Image.open("Resources\profile.png")
        add_contact_image = add_contact_image.resize((30, 30))
        self.add_contact_photo = ImageTk.PhotoImage(add_contact_image)


        # Load the add_contact_image only once
        if not hasattr(self, 'add_contact_photo'):
            add_contact_image = Image.open("Resources\profile.png")
            add_contact_image = add_contact_image.resize((30, 30))
            self.add_contact_photo = ImageTk.PhotoImage(add_contact_image)


        if refresh == 0:
            try:
                self.scrollable_frame = ScrollableFrame(self.root, height = 400, width =150)
                self.scrollable_frame.pack(side = 'left')
                add_contact_image = Image.open("Resources\profile.png")
                add_contact_image = add_contact_image.resize((30, 30))
                self.add_contact_photo = ImageTk.PhotoImage(add_contact_image)

                for x in range (len(self.chatroom_list)):
                    friend=self.chatroom_list[x]
                    friend_button = ctk.CTkButton(self.scrollable_frame, text=friend, command=partial(self.show_chat, friend), image = self.add_contact_photo,anchor='w' ,fg_color="transparent", text_color="black", hover_color="#B9B9B9")
                    friend_button.pack()
                    self.chatroom_list_button.append(friend_button)
            except:
                pass

        else:  # Refresh friend list based on updated data
            for x in range(len(self.group_chat_button_list)):
                self.group_chat_button_list[x].pack()
            for x in range(len(self.chatroom_list_button)):
                self.chatroom_list_button[x].pack()

    

    def show_chat(self, name: str):
        chat_history = None
        self.chat_selected_label.pack_forget()
        self.chat_selected_label.configure(text = 'name')
        self.chat_selected_label.pack(side='top', anchor='w', padx=5)


    def open_contact(self):
        self.change_contact_window = ctk.CTkToplevel(self.root)
        self.change_contact_window.title("Friend List")
        self.change_contact_window.geometry("300x400")  
        self.change_contact_window.wm_transient(self.root)

        add_group_image = ctk.CTkImage(Image.open('Resources/addgroup.png'),  size=(40, 40))   
        add_group_photo = add_group_image
        self.add_group_button = ctk.CTkButton(self.change_contact_window, image=add_group_photo, command=self.add_group,text = '', fg_color= 'transparent', width=50,  hover_color="#B9B9B9")
        self.add_group_button.photo = add_group_photo  
        self.add_group_button.pack(anchor='w')
        self.add_group_flag = 0

        friend_list_frame = ctk.CTkFrame(self.change_contact_window)
        friend_list_frame.pack(fill="both", expand=True)

        self.create_friend_list(friend_list_frame)
           
    def create_friend_list(self, frame):
        friendlist_contact_image = Image.open("Resources\profile.png")
        friendlist_contact_image = friendlist_contact_image.resize((100, 100))
        self.friendlist_contact_photo = ImageTk.PhotoImage(friendlist_contact_image)

        if not hasattr(self, 'add_contact_photo'):
            add_contact_image = Image.open("Resources\profile.png")
            add_contact_image = add_contact_image.resize((30, 30))
            self.add_contact_photo = ImageTk.PhotoImage(add_contact_image)

        try:
            for friend in self.friend_list:
                friend_button = ctk.CTkButton(frame, text=friend, command=partial(self.show_chat, friend),
                                            image=self.friendlist_contact_photo, anchor='w', fg_color="transparent",
                                            text_color="black", hover_color="#B9B9B9")
                friend_button.pack()
        except:
            pass
        
    def display_chat_box(self, name:str): 
        frame = ctk.CTkFrame(self.root, fg_color='transparent')
        self.chat_selected_label = ctk.CTkLabel(frame, text= name)
        self.chat_selected_label.pack(side='top', anchor='w', padx=5)
        self.chat_transcript_area = ctk.CTkTextbox(frame, width=550, height=200, font=("Serif", 12))
        self.chat_transcript_area.pack(side='left', padx=5)
        frame.pack(side='top')


    def display_chat_entry_box(self):
        frame = ctk.CTkFrame(self.root, fg_color='transparent')
        ctk.CTkLabel(frame, text='Enter message:', font=("Serif", 12)).pack(side='top', anchor='w',padx=15)
        self.enter_text_widget = ctk.CTkTextbox(frame, width=550, font=("Serif", 12), height= 50)
        self.enter_text_widget.pack(side='left', pady=10, padx=15)
        self.enter_text_widget.bind('<Return>', self.on_enter_key_pressed)
        frame.pack(side='top')
        
        
    
    def listen_for_incoming_messages_in_a_thread(self):
        thread = threading.Thread(target=self.receive_message_from_server, args=(self.client_socket,)) # Create a thread for the send and receive in same time 
        thread.start()
    
    def create_friend_button(self, friend_name):
        # Create a friend button based on the given name and add it to the friends_frame
        friend_button = ctk.CTkButton(self.friends_frame, text=friend_name, command=partial(self.show_chat, friend_name), padding=(10, 8, 20, 8), style="Custom.TButton", image=self.add_contact_photo, compound=LEFT)
        friend_button.image = self.add_contact_photo(anchor='w')
    
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
            elif 'CHANGE PROFILE' in message:
                if message.split()[2].lower() in ['success']:
                    messagebox.showinfo('Success', 'Success changing profile photo')
                else:
                    messagebox.showerror('Error', 'An error occured during changing profile')
            elif 'Friend add' in message:
                self.last_received_message = message
                if message.split()[2].lower() in ['success']:
                    messagebox.showinfo('Success', 'Success adding friend')
                else:
                    messagebox.showerror('Error', 'Friend doesn\'t exist')
            elif 'CREATE GROUP' in message:
                self.last_received_message = message
                if 'success' in message:
                    messagebox.showinfo('Success', 'Success creating group')
                else:
                    messagebox.showerror('Error', 'Something happened when creating group')
            else:
                self.chat_transcript_area.insert('end', message + '\n')
                self.chat_transcript_area.yview(END)
        so.close()

    def on_enter_key_pressed(self, event):
        self.send_chat()
        self.clear_text()

    def clear_text(self):
        self.enter_text_widget.delete(1.0, 'end')

    def send_chat(self):
        senders_name = self.name + " "
        target_name = self.chat_selected
        data = self.enter_text_widget.get(1.0, 'end').strip()
        message = (senders_name + data)
        self.chat_transcript_area.insert('end', message + '\n')
        self.chat_transcript_area.yview(END)
        message = (message + ' ' + target_name).encode('utf-8')
        self.enter_text_widget.delete(1.0, 'end')
        self.client_socket.send(message)

    def close(self):
        self.settings_profile_photo.pack_forget()
        self.settings_username.pack_forget()
        self.change_username_button.pack_forget()
        self.change_photo_button.pack_forget()
        self.settings_window.destroy()


    def on_close_window(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
            self.client_socket.close()
            exit(0)
    

logger = logging.getLogger() # for error logging
#the mail function 
if __name__ == '__main__':
    root = ctk.CTk()
    gui = GUI(root)
    root.protocol("WM_DELETE_WINDOW", gui.on_close_window)
    root.mainloop()
