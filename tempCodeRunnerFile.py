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
            new_friend_button.pack(anchor='n', before=self.friend_list_button[0] if self.friend_list_button else None)
            self.friend_list_button.insert(0, new_friend_button)  # Update the friend list button list