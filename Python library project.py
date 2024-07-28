""" 
Author: Tyrece Denton
Date Written: 7/27/24
Assingment: Final Project
This program is a library managment system that tracks books inputed by the user as well as check out and check in.
The program is supposed to have a second tab that tracks members of the library as well. However that part 
was not functional in time.
"""
# All imports
import sqlite3

from tkinter import *
import tkinter.ttk as ttk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd

# Database
connector = sqlite3.connect('library.db')
cursor = connector.cursor()

connector.execute(
'CREATE TABLE IF NOT EXISTS Library (BK_NAME TEXT, BK_ID TEXT PRIMARY KEY NOT NULL, AUTHOR_NAME TEXT, BK_STATUS TEXT, CARD_ID TEXT)'
)

# Functions
def issuer_card():
	Cid = sd.askstring('Issuer Card ID', 'What is the Issuer\'s Card ID?\t\t\t')

	if not Cid:
		mb.showerror('Issuer ID cannot be zero!', 'Can\'t keep Issuer ID empty, it must have a value')
	else:
		return Cid
# Giving whomever checked out the book an ID and inputing into the system

def display_records():
	global connector, cursor
	global tree

	tree.delete(*tree.get_children())

	curr = connector.execute('SELECT * FROM Library')
	data = curr.fetchall()

	for records in data:
		tree.insert('', END, values=records)
# Displays books that are input into the system

def clear_fields():
	global bk_status, bk_id, bk_name, author_name, card_id

	bk_status.set('Available')
	for i in ['bk_id', 'bk_name', 'author_name', 'card_id']:
		exec(f"{i}.set('')")
		bk_id_entry.config(state='normal')
	try:
		tree.selection_remove(tree.selection()[0])
	except:
		pass
#Allows the user to delete a record they are currently adding

def clear_and_display():
	clear_fields()
	display_records()


def add_record():
	global connector
	global bk_name, bk_id, author_name, bk_status

	if bk_status.get() == 'Issued':
		card_id.set(issuer_card())
	else:
		card_id.set('N/A')

	surety = mb.askyesno('Are you sure?',
	            'Are you sure this is the data you want to enter?\nPlease note that Book ID cannot be changed in the future')

	if surety:
		try:
			connector.execute(
			'INSERT INTO Library (BK_NAME, BK_ID, AUTHOR_NAME, BK_STATUS, CARD_ID) VALUES (?, ?, ?, ?, ?)',
				(bk_name.get(), bk_id.get(), author_name.get(), bk_status.get(), card_id.get()))
			connector.commit()

			clear_and_display()

			mb.showinfo('Record added', 'The new record was successfully added to your database')
		except sqlite3.IntegrityError:
			mb.showerror('Book ID currently in use.',
			             'The Book ID you are trying to enter is already in the database, please alter that book\'s record or check personal input.')
# Defines how the user can add a book to the inverntory

def view_record():
	global bk_name, bk_id, bk_status, author_name, card_id
	global tree

	if not tree.focus():
		mb.showerror('Select a record. ', 'To view a record, you must select it in the table. Please do so before continuing.')
		return

	current_item_selected = tree.focus()
	values_in_selected_item = tree.item(current_item_selected)
	selection = values_in_selected_item['values']

	bk_name.set(selection[0])   ;   bk_id.set(selection[1]) ; bk_status.set(selection[3])
	author_name.set(selection[2])
	try:
		card_id.set(selection[4])
	except:
		card_id.set('')
# Defines the users ability to click on input records and further manipulate them

def update_record():
	def update():
		global bk_status, bk_name, bk_id, author_name, card_id
		global connector, tree

		if bk_status.get() == 'Issued':
			card_id.set(issuer_card())
		else:
			card_id.set('N/A')

		cursor.execute('UPDATE Library SET BK_NAME=?, BK_STATUS=?, AUTHOR_NAME=?, CARD_ID=? WHERE BK_ID=?',
		               (bk_name.get(), bk_status.get(), author_name.get(), card_id.get(), bk_id.get()))
		connector.commit()
		
		clear_and_display()

		edit.destroy()
		bk_id_entry.config(state='normal')
		clear.config(state='normal')

	view_record()

	bk_id_entry.config(state='disable')
	clear.config(state='disable')

	edit = Button(left_frame, text='Update Record', font=btn_font, bg=label_button, width=20, command=update)
	edit.place(x=50, y=375)
# Allows the user to change details of a chosen record

def remove_record():
	if not tree.selection():
		mb.showerror('Error!', 'Please select an item from the database')
		return

	current_item = tree.focus()
	values = tree.item(current_item)
	selection = values["values"]

	cursor.execute('DELETE FROM Library WHERE BK_ID=?', (selection[1], ))
	connector.commit()

	tree.delete(current_item)

	mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')

	clear_and_display()
# Allows the user to delete a slected record

def delete_inventory():
	if mb.askyesno('Are you sure?', 'Are you sure you want to delete the entire inventory?\n\nThis command cannot be reversed'):
		tree.delete(*tree.get_children())

		cursor.execute('DELETE FROM Library')
		connector.commit()
	else:
		return
# Deletes all inputed records in the current inventory

def change_availability():
	global card_id, tree, connector

	if not tree.selection():
		mb.showerror('Error:', 'Please select a book from the database')
		return

	current_item = tree.focus()
	values = tree.item(current_item)
	BK_id = values['values'][1]
	BK_status = values["values"][3]

	if BK_status == 'Issued':
		surety = mb.askyesno('Is return confirmed?', 'Has the book been returned to you?')
		if surety:
			cursor.execute('UPDATE Library SET bk_status=?, card_id=? WHERE bk_id=?', ('Available', 'N/A', BK_id))
			connector.commit()
		else: mb.showinfo(
			'Cannot be returned', 'The book status cannot be set to Available unless it has been returned')
	else:
		cursor.execute('UPDATE Library SET bk_status=?, card_id=? where bk_id=?', ('Issued', issuer_card(), BK_id))
		connector.commit()

	clear_and_display()
# Allows the user to display whether a book has been issued out or is currently in stock

# Variables
lf_color = 'Gold'  # Left frame color
tfr_color = 'RoyalBlue'  # Top right frame color
bfr_color = 'DarkGoldenRod'  # Bottom right frame color
label_button = 'CornFlowerBlue'  # Header and button color

lbl_font = ('Georgia', 13)  # Label font
entry_font = ('Times New Roman', 12)  # Entry widget font
btn_font = ('Gill Sans MT', 13)

# Initializing the main GUI window
main = Tk()
notebook = ttk.Notebook(main)#Widget that manages windows
tab1 = Frame(notebook)
tab2 = Frame(notebook)
notebook.add(tab1,text="Books")
notebook.add(tab2,text="Members")
notebook.pack()
main.title('Outsource: A digital library')
main.geometry('1010x530')
main.resizable(0, 0)

Label(main, text='Outsource', font=("Noto Sans CJK TC", 15, 'bold'), bg=label_button, fg='White').pack(side=TOP, fill=X)

# StringVars
bk_status = StringVar()
bk_name = StringVar()
bk_id = StringVar()
author_name = StringVar()
card_id = StringVar()

# Frames
left_frame = Frame(main, bg=lf_color) # frame defition and color
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96) # frame dimensions

tfr_frame = Frame(main, bg=tfr_color)
tfr_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

bfr_frame = Frame(main)
bfr_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Left Frame
Label(left_frame, text='Book Name', bg=lf_color, font=lbl_font).place(x=98, y=25) #Entry box name
Entry(left_frame, width=25, font=entry_font, text=bk_name).place(x=45, y=55) # Entry box

Label(left_frame, text='Book ID', bg=lf_color, font=lbl_font).place(x=110, y=105)
bk_id_entry = Entry(left_frame, width=25, font=entry_font, text=bk_id)
bk_id_entry.place(x=45, y=135)

Label(left_frame, text='Author Name', bg=lf_color, font=lbl_font).place(x=90, y=185)
Entry(left_frame, width=25, font=entry_font, text=author_name).place(x=45, y=215)

Label(left_frame, text='Book Status', bg=lf_color, font=lbl_font).place(x=95, y=265)
dd = OptionMenu(left_frame, bk_status, *['Available', 'Issued']) # Applied when adding records
dd.configure(font=entry_font, width=12)
dd.place(x=75, y=300)

submit = Button(left_frame, text='Add new record', font=btn_font, bg=label_button, width=20, command=add_record)
submit.place(x=50, y=375)

clear = Button(left_frame, text='Clear fields', font=btn_font, bg=label_button, width=20, command=clear_fields)
clear.place(x=50, y=435)

# Right Top Frame
Button(tfr_frame, text='Delete book record', font=btn_font, bg=label_button, width=17, command=remove_record).place(x=8, y=30)
Button(tfr_frame, text='Delete full inventory', font=btn_font, bg=label_button, width=17, command=delete_inventory).place(x=178, y=30)
Button(tfr_frame, text='Update book details', font=btn_font, bg=label_button, width=17,
       command=update_record).place(x=348, y=30)
Button(tfr_frame, text='Change Book Availability', font=btn_font, bg=label_button, width=19,
       command=change_availability).place(x=518, y=30)

# Right Bottom Frame
Label(bfr_frame, text='INVENTORY', bg=bfr_color, font=("Noto Sans CJK TC", 15, 'bold')).pack(side=TOP, fill=X)

tree = ttk.Treeview(bfr_frame, selectmode=BROWSE, columns=('Book Name', 'Book ID', 'Author', 'Status', 'Issuer Card ID'))

XScrollbar = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview) # Allows user to scroll through records
YScrollbar = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
XScrollbar.pack(side=BOTTOM, fill=X)
YScrollbar.pack(side=RIGHT, fill=Y)

tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)

tree.heading('Book Name', text='Book Name', anchor=CENTER)
tree.heading('Book ID', text='Book ID', anchor=CENTER)
tree.heading('Author', text='Author', anchor=CENTER)
tree.heading('Status', text='Status of the Book', anchor=CENTER)
tree.heading('Issuer Card ID', text='Issuer Card ID', anchor=CENTER)

tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=225, stretch=NO)
tree.column('#2', width=70, stretch=NO)
tree.column('#3', width=150, stretch=NO)
tree.column('#4', width=105, stretch=NO)
tree.column('#5', width=132, stretch=NO)

tree.place(y=30, x=0, relheight=0.9, relwidth=1)

clear_and_display()

# Finalizing the window
tab1.update()
tab1.mainloop()

left_frame = Frame(main, bg=lf_color) # frame defition and color
left_frame.place(x=0, y=30, relwidth=0.3, relheight=0.96) # frame dimensions

tfr_frame = Frame(main, bg=tfr_color)
tfr_frame.place(relx=0.3, y=30, relheight=0.2, relwidth=0.7)

bfr_frame = Frame(main)
bfr_frame.place(relx=0.3, rely=0.24, relheight=0.785, relwidth=0.7)

# Left Frame
Label(left_frame, text='Member First Name', bg=lf_color, font=lbl_font).place(x=98, y=25) #Entry box name
Entry(left_frame, width=25, font=entry_font, text=bk_name).place(x=45, y=55) # Entry box

Label(left_frame, text='Member Last Name', bg=lf_color, font=lbl_font).place(x=110, y=105)
bk_id_entry = Entry(left_frame, width=25, font=entry_font, text=bk_id)
bk_id_entry.place(x=45, y=135)

Label(left_frame, text='Issuer ID', bg=lf_color, font=lbl_font).place(x=90, y=185)
Entry(left_frame, width=25, font=entry_font, text=author_name).place(x=45, y=215)

submit = Button(left_frame, text='Add new member', font=btn_font, bg=label_button, width=20, command=add_record)
submit.place(x=50, y=375)

clear = Button(left_frame, text='Clear fields', font=btn_font, bg=label_button, width=20, command=clear_fields)
clear.place(x=50, y=435)

# Right Top Frame
Button(tfr_frame, text='Delete member record', font=btn_font, bg=label_button, width=17, command=remove_record).place(x=8, y=30)
Button(tfr_frame, text='Delete full inventory', font=btn_font, bg=label_button, width=17, command=delete_inventory).place(x=178, y=30)
Button(tfr_frame, text='Update member details', font=btn_font, bg=label_button, width=17,
       command=update_record).place(x=348, y=30)

Label(bfr_frame, text='INVENTORY', bg=bfr_color, font=("Noto Sans CJK TC", 15, 'bold')).pack(side=TOP, fill=X)

tree = ttk.Treeview(bfr_frame, selectmode=BROWSE, columns=('Member First Name', 'Member Last Name', 'Issuer ID'))

XScrollbar = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview) # Allows user to scroll through records
YScrollbar = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
XScrollbar.pack(side=BOTTOM, fill=X)
YScrollbar.pack(side=RIGHT, fill=Y)

tree.config(xscrollcommand=XScrollbar.set, yscrollcommand=YScrollbar.set)

tree.heading('Book Name', text='Member First Name', anchor=CENTER)
tree.heading('Book ID', text='Member Last Name', anchor=CENTER)
tree.heading('Author', text='Issuer ID', anchor=CENTER)


tree.column('#0', width=0, stretch=NO)
tree.column('#1', width=225, stretch=NO)
tree.column('#2', width=70, stretch=NO)
tree.column('#3', width=150, stretch=NO)
tree.column('#4', width=105, stretch=NO)
tree.column('#5', width=132, stretch=NO)

tree.place(y=30, x=0, relheight=0.9, relwidth=1)


clear_and_display()

tab2.update()
tab2.mainloop()
