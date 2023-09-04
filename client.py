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
        if self.e.get() in ['Enter your username', 'Enter new username']:
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
        username = self.e.get()
        if username not in ['Enter your username', '']:
            if len(username) <= 11:
                self.name = username
                self.e.destroy()
                self.b.destroy()
                self.label.destroy()
                self.logo_label.destroy()
                self.frame.destroy()
                self.initialize_socket()
            else:
                messagebox.showerror("Error", "Username must be less than 12 characters")
        else:
            messagebox.showerror("Error", "Username cannot be empty")

    
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
        menu = Frame(self.root)
        menu.pack(side='left', padx=10, pady=10, fill='y')

        #Profile Picture

        self.profile_pic_path="data/"+self.name+"/profile.jpg"

        if not os.path.exists(self.profile_pic_path):#checking for existing profile picture, if not found switch to defult photo
           self.profile_pic_path="Resources/profile.png"

        self.profile_image=Image.open(self.profile_pic_path)
        self.profile_image=self.profile_image.resize((40,40))
        self.profile_img = ImageTk.PhotoImage(self.profile_image)
        self.profile_photo=Label(menu,image=self.profile_img)
        self.profile_photo.pack()



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
        def change_label_text():
            settings_username.config(text=self.name,  font="oswald")
            self.e.pack_forget()


        def move_button_and_add_entry():
            if self.flag==0:
                # Hide the button
                self.flag=1
                change_username_button.pack_forget()
                change_photo_button.pack_forget()
                    
                # Create a new entry widget and pack it below the button
                self.e = tk.Entry(settings_window)
                self.e.insert(0, 'Enter new username')
                self.e.bind("<FocusIn>", self.on_entry_click)
                self.e.pack(pady=5)
                    
                # Pack the button below the entry
                change_username_button.pack(pady=5)
                change_photo_button.pack(pady=5)
            else:
                self.e.pack_forget()
                self.flag=0
                if self.e.get() not in ["", "Enter new username"]:
                    self.name=self.e.get()
                    change_label_text()

        def change_photo():
             file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ppm *.pgm")])
             if file_path:
                image = Image.open(file_path)
                image=image.resize((40,40))
                self.profile_image=image
                photo = ImageTk.PhotoImage(self.profile_image)
                self.profile_photo.config(image=photo)
                self.profile_photo.image=photo
                image2=Image.open(file_path)
                image2=image2.resize((80,80))
                photo2 = ImageTk.PhotoImage(image2)
                self.settings_profile_img=photo2
                self.settings_profile_photo.config(image=self.settings_profile_img)
                self.settings_profile_photo.image=self.settings_profile_img
        

        self.flag=0
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")

        self.settings_profile_image=self.profile_image.resize((80,80))
        self.settings_profile_img = ImageTk.PhotoImage(self.settings_profile_image)
        self.settings_profile_photo=Label(settings_window,image=self.settings_profile_img)
        self.settings_profile_photo.pack(anchor="center")

        settings_username=Label(settings_window, text=self.name, font="oswald")
        settings_username.pack(pady=5)

        change_username_button = Button(settings_window, text="Change Username", command=move_button_and_add_entry)
        change_username_button.pack(pady=10)

        change_photo_button = Button(settings_window, text="Change Profile Picture", command=change_photo)
        change_photo_button.pack(pady=10)

        #change_profile_button = Button(settings_window, text="Change Profile", command=self.show_change_profile_window)
        #change_profile_button.pack(pady=10)


    '''
    def show_change_profile_window(self):
        change_profile_window = tk.Toplevel(self.root)
        change_profile_window.title("Change Username")

        new_name_label = Label(change_profile_window, text="Enter new username:")
        new_name_label.pack()
        
        self.e = Entry(change_profile_window)
        self.e.pack()
        
        change_button = Button(change_profile_window, text="Change", command=self.change_profile)
        change_button.pack()
    ''' 
        
    # def on_enter(event):
    #     b.config(bg="#C4C4C4", fg="white")

    # def on_leave(event):
    #     b.config(bg="white", fg="black")

    def submit(self):
        name = self.e.get()
        if name.strip():
            if len(name) > 11:
                messagebox.showerror("Error", "username does not exist")
            else:
                self.save_friend(name)
                self.e.delete(0, END)
                self.e.pack_forget()
                self.b.pack_forget()
                self.add_friend_button['state'] = tk.NORMAL

                # Add the new friend to the friend list without refreshing
                self.friend_list.append(name)

                # Create a new friend button
                truncated_name = name[:11] 
                new_friend_button = Button(self.friends_frame, text=truncated_name, command=partial(self.show_chat, name),
                                        padding=(20, 8, 20, 8), style="Custom.TButton", image=self.add_contact_photo,
                                        compound=LEFT)
                new_friend_button.image = self.add_contact_photo

                # Place the new friend button at the top of the friend list
                self.pack_before(new_friend_button, self.friend_list_button[0] if self.friend_list_button else None)
                self.friend_list_button.insert(0, new_friend_button) 
    
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