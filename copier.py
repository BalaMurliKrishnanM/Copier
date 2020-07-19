#copier_v1.py
'''Import modules'''
import os
import sys
import shutil
import gc
import portalocker
import json
import PySimpleGUI as sg
'''Global variables. Try to avoid'''


'''Class Declarations'''
class gui(sg.Window):
	'''GUI subclass for copier'''
	def __init__(self, Title='Copier', layout="Default"):

		'''
		Declaring the basic layout of the main window and initializing with PySimpleGUI super class
		'''
		if layout == "Default":
			self.layout = [	[sg.Text('')],
					[sg.Text('Enter the Source Adress(es):')],
			  		[sg.Text('Eg: \n/media/bmk/alpha/Program Files (x86)/Citrix/ICA Client/\n/media/bmk/alpha/Program Files (x86)/Audacity/',
			  			font=("Helvetica1", 9))],
					[sg.Multiline(default_text='Paste all the directory path in each line.',key='-IN-',
						size=(75, 5)),sg.Button('Sync')],
					[sg.Text('Dest. Address'),sg.Input(key='-dest-',size=(70, 2))],
					[sg.Button('Go'), sg.Button('Clear Source Path'),sg.Button('Clear Input'),
						sg.Button('Clear Output'), sg.Button('Exit')],
			  		[sg.Text('List of Files:                                                                                          OUTPUT:')],
					[sg.Multiline(key='-INput-',default_text='Paste the list of files\nEach file in each line.\nEg:\nCitrix.exe\ndata.txt\nlog\n',
						size=(50, 20)),sg.Output(size=(50,20), key='-OUTPUT-')]
				]
		else:
			self.layout = layout
		#Initializing super class with Requrire Title and layout
		sg.Window.__init__(self, Title, self.layout)

	def gui_button_process(self):
		'''
		The following events are processed here:
			1. Exiting from the GUI when the Exit button or (x) is pressed.
			2. Clearing the data present in the Input path textbox
			3. Clearing the data present in the Output path textbox
			4. Clearing the data present in the List of Files textbox
			5. Invoke the Syncloop when Sync button is pressed
			6. Invoke the Findloop when Go button is pressed
		'''
		event, values = self.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			sg.popup('Thanks for using Copier@BMK\nClosing...',auto_close=True,auto_close_duration=1)
			self.layout = None
			return 0
		if event == 'Clear Source Path':
			self['-IN-'].update('')
			return 1
		if event == 'Clear Input':
			self['-INput-'].update('')
			return 1
		if event == 'Clear Output':
			self['-OUTPUT-'].update('')
			return 1
		if event == 'Go':
			findloop = file_lib()
			if findloop.findloop(values['-INput-'],values['-dest-']):
				print(chr(9785), chr(8227),"ERROR: Copying Stopped my user")
			del(findloop)
			return 1
		if event == 'Sync':
			sync_file = file_lib()
			if sync_file.syncloop(values['-IN-']):
				print(chr(9785), chr(8227),"ERROR: Suncing stopped by user")
			del(sync_file)
			return 1

class file_lib:
	'''All the file operations are done inside the class'''

	db_file = None
	dict_file = None
	filename2path = []
	filename = {}

	def __init__(self):
		self.COUNT = 0



	def syncer(func):
		'''
		Decorator to make sure the Database file is opened and closed.
		'''
		db_name = "database_path.db"
		db_dict = "database_dict.db"
		def wrapper(*args, **kwagrs):
			if func.__name__ == "write_2_file":
				with open(db_name,"wb") as file_lib.db_file:
					with open(db_dict, "w") as file_lib.dict_file:
						func(*args, **kwagrs)
				return
			try:
				with open(db_name,"r") as file_lib.db_file:
						with open(db_dict, "r") as file_lib.dict_file:
							func(*args, **kwagrs)
			except:
				print(chr(9785), chr(8227),"ERROR: No files are synced.")
		return wrapper

	def dict_context(func):
		'''
		Decorator to make sure the filename and filename2path variables are initialized
		while invoking syncloop.
		'''
		def inner(*args, **kwagrs):
			file_lib.filename = {}
			file_lib.filename2path = []
			func(*args, **kwagrs)
			del(file_lib.filename2path)
			del(file_lib.filename)
			file_lib.filename = {}
		return inner

	@syncer
	def write_2_file(self):
		'''
		Writes the sorted File name to Path list to the database.
		'''
		for i in file_lib.filename2path:
			pos = i.find(":::")
			if pos != -1:
				file_lib.filename[i[:pos]] = (file_lib.db_file.tell())
				file_lib.db_file.write((i+"\n").encode(encoding='UTF-8'))
				continue
			print(chr(9785), chr(8227),"ERROR:Writing to db "+i)
		json.dump(file_lib.filename, file_lib.dict_file)


	def read_4m_file(self,file,dest):
		'''
		Reads the File name to path entry by seeking in the particular offset of 
		the database.
		'''
		position = file_lib.filename[file]
		file_lib.db_file.seek(position,0)
		path = file_lib.db_file.readline()[:-1]
		position = path.find(":::")
		path = str(path[position+3:])
		shutil.copy2(path, dest)
		os.chmod(os.path.join(dest,file), 0o777)


	def all_subfolder(self,window,path):
		'''
		Add the File entry to Filename and Filename2path variables by recursively walking through 
		all the directory paths.
		'''
		ret = 0
		event,value = window.read(timeout=0)
		if (event ==sg.WIN_CLOSED) or ret ==-1:
			return -1
		try:
			path = os.scandir(path)
		except:
			print(chr(9785), chr(8227),"ERROR: '"+path+"' is not Supported.")
			return ret
		for f in path:
			if f.is_file():
				event,value = window.read(timeout=0)
				if (event ==sg.WIN_CLOSED) or ret ==-1:
					return -1
				if f.name not in file_lib.filename:
					file_lib.filename[f.name] = None
					file_lib.filename2path.append(f.name+":::"+f.path)
				else:
					print(chr(9785), chr(8227),"ERROR:Multiple instance found for '"+f.name+"'" )
				self.COUNT+=1
				window['progbar'].update_bar(self.COUNT)
			elif(ret!=-1):
				if f.is_dir():
					ret = self.all_subfolder(window,f.path)
				else:
					print(chr(9785), chr(8227),"ERROR:Not a Directory '"+f.name+"'")
		return ret

	@dict_context
	def syncloop(self,dirl):
		'''
		Syncs all the directories mentioned in the input directory list and make a sorted list.
		Stores the list to the database.
		'''
		dirlist = dirl.rstrip().split('\n')
		ret = 0
		if len(dirlist)>0:
			for mypath in dirlist:
				if os.path.isdir(mypath):
					Layout1 = [[sg.ProgressBar(100, orientation='h', size=(50, 20), key='progbar')]]
					window_p = gui( 'Calculating time for "'+mypath+"'",Layout1)
					total = 0
					self.COUNT = 0
					i = 0
					for root, directory, files in os.walk(mypath):
						event,value = window_p.read(timeout=0)
						if (event ==sg.WIN_CLOSED):
							return
						window_p['progbar'].update_bar(self.COUNT)
						total += len(files)
						if i == 0:
							self.COUNT += 1
						i +=1
						i%=10
						self.COUNT = self.COUNT%100
					self.COUNT = 0
					window_p.close()
					Layout1 =None
					window_p =None
					Layout1 = [[sg.ProgressBar(total, orientation='h', size=(50, 20), key='progbar')]]
					window_p = gui( 'Loading '+mypath,Layout1)
					ret = self.all_subfolder(window_p, mypath)
					window_p.close()
					Layout1 =None
					window_p =None
					gc.collect()
					if ret ==-1:
						print(chr(9785), chr(8227),"ERROR:Force stopped.")
						continue
					print("LOG:"+mypath+" is synced")
					file_lib.filename2path.sort()
					self.write_2_file()
				else:
					print(chr(9785), chr(8227),"ERROR:Invalid path '"+mypath+"'")

	@syncer
	def findloop(self,inputlist,dest):
		'''
		Loop through the file names mentioned in the List of Files textbox.
		Checks the database file for the path.
		If entry is identified, then the file is copied to the destination address.		
		'''
		inputlist = inputlist.rstrip().split('\n')
		dest = dest.rstrip().split('\n')
		self.COUNT = 0
		if os.path.isdir(dest[0]):
			if len(inputlist)>0:
				Layout1 = [[sg.ProgressBar(len(inputlist), orientation='h', size=(50, 20), key='progbar')]]
				window_p = gui( 'Coping to '+dest[0],Layout1)
				file_lib.filename = json.load(file_lib.dict_file)
				for file in inputlist:
					if file == "":
						continue
					event,value = window_p.read(timeout=0)
					if (event ==sg.WIN_CLOSED):
						return -1
					window_p['progbar'].update_bar(self.COUNT)
					while(file[len(file)-1]==" "):
						file = file[:-1]
					while(file[0]==" "):
						file = file[1:]
					if file in file_lib.filename:
						source = self.read_4m_file(file,dest[0])
						print("LOG:"+file+" is copied")
					else:
						print(chr(9785), chr(8227),"ERROR:Cannot find '"+file+"' in synced path.")
					self.COUNT+=1
				window_p.close()
				Layout1 =None
				window_p =None
				gc.collect()
		else:
			print(chr(9785), chr(8227),"ERROR:Invalid dest. path '"+dest[0]+"'")
		return 1

		
'''Function Declarations'''
def syncing_stat(pos):
	pos = pos % 4
	if(pos == 0):
		print("\rSyncing...|",end="")
	elif(pos == 1):
		print("\rSyncing.../",end="")
	elif(pos == 2):
		print("\rSyncing...-",end="")
	elif(pos == 3):
		print("\rSyncing...\\",end="")
def instance_already_running(func):
	"""
	Detect if an an instance with the label is already running, globally
	at the operating system level.
	The lock will be released when the program exits, or could be
	released if the file pointer were closed.
	"""
	def main_call():
		'''
		Decorator for main_loop()
			To avoid malfunctioning of .lock file.
			The following order should be followed strictly:
				1. Open the lock file with exclusive and non blocking key
				2. Run main_loop()
				3. Release the lock
		'''
		try:
			instance = open("instance_copier.lock", "w+")
			portalocker.lock(instance, portalocker.LOCK_EX | portalocker.LOCK_NB)
		except:
			sg.popup('One more Instance of Copier is already running.',title="Copier")
			return
		func()
		portalocker.unlock(instance)
	return main_call



@instance_already_running
def main_loop():
	'''Main function call'''
	'''Creating layout of the GUI'''
	'''Initializing the main gui class'''
	window = gui()
	status = 1
	while status:
		'''GUI windows will be displayed until the exit button or (X) is clicked'''
		status = window.gui_button_process()

	window.close()			# Close the main GUI 		9785 ☹ 8227 ‣
	window =None			# Clearing the link to the GUI class to optimize the memory
	gc.collect()			# To reduce the memory used by clearing the unreferenced objects


'''Main loop'''
if __name__ == "__main__":
	main_loop()			# Calling the Main function
	sys.exit("Bye.\nThanks for using Copier@BMK.")