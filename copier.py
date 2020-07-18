#copier_v1.py
'''Import modules'''
import os
import sys
import shutil
import gc
import portalocker
import PySimpleGUI as sg
'''Global variables. Try to avoid'''


'''Class Declarations'''
class gui(sg.Window):
	'''GUI for copier'''
	''''''
	def __init__(self, Title='Copier', layout="Default"):
		if layout == "Default":
			self.layout = [	[sg.Text('')],
					[sg.Text('Enter the Source Adress(es):')],
			  		[sg.Text('Eg: \n/media/bmk/alpha/Program Files (x86)/Citrix/ICA Client/\n/media/bmk/alpha/Program Files (x86)/Audacity/',
			  			font=("Helvetica1", 9))],
					[sg.Multiline(default_text='Paste all the directory path in each line.',key='-IN-',
						size=(75, 5)),sg.Button('Sync')],
					[sg.Text('Dest. Address'),sg.Input(key='-dest-',size=(70, 2))],
					[sg.Button('Go'), sg.Button('Clear Path'),sg.Button('Clear Input'),
						sg.Button('Clear Output'), sg.Button('Exit')],
			  		[sg.Text('List of Files:                                                                                          OUTPUT:')],
					[sg.Multiline(key='-INput-',default_text='Paste the list of files\nEach file in each line.\nEg:\nBPC_INIT_01.ice\nBPC_INIT_05.ice\nSSM_INIT_01.c\n',
						size=(50, 20)),sg.Output(size=(50,20), key='-OUTPUT-')]
				]
		else:
			self.layout = layout
		#Initializing super class with Requrire Title and layout
		sg.Window.__init__(self, Title, self.layout)

	def gui_button_process(self):
		event, values = self.read()
		if event in (sg.WIN_CLOSED, 'Exit'):
			sg.popup('Thanks for using Copier@BMK\nClosing...',auto_close=True,auto_close_duration=1)
			self.layout = None
			return 0
		if event == 'Clear Path':
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
				print("ERROR: Copying Stopped my user")
			del(findloop)
			return 1
		if event == 'Sync':
			sync_file = file_lib()
			if sync_file.syncloop(values['-IN-']):
				print("ERROR: Suncing stopped by user")
			del(sync_file)
			return 1

class file_lib:
	'''All the file operations'''

	dict_file = None
	filename2path = []
	filename = {}

	def __init__(self):
		self.COUNT = 0

	def syncer(func):
		db_name = "database_path.db"
		def wrapper(*args, **kwagrs):
			if func.__name__ == "write_2_file":
				with open(db_name,"wb") as file_lib.dict_file:
					func(*args, **kwagrs)
				return
			with open(db_name,"r") as file_lib.dict_file:
				func(*args, **kwagrs)
		return wrapper

	def dict_context(func):
		def inner(*args, **kwagrs):
			file_lib.filename = {}
			file_lib.filename2path = []
			func(*args, **kwagrs)
			del(file_lib.filename2path)
		return inner

	@syncer
	def write_2_file(self):
		for i in file_lib.filename2path:
			pos = i.find(":::")
			if pos != -1:
				file_lib.filename[i[:pos]] = (file_lib.dict_file.tell())
				file_lib.dict_file.write((i+"\n").encode(encoding='UTF-8'))
				continue
			print("ERROR:Writing to db "+i)

	@syncer
	def read_4m_file(self,file,dest):
		position = file_lib.filename[file]
		file_lib.dict_file.seek(position,0)
		path = file_lib.dict_file.readline()[:-1]
		position = path.find(":::")
		path = str(path[position+3:])
		shutil.copy2(path, dest)
		os.chmod(os.path.join(dest,file), 0o777)


	def all_subfolder(self,window,path):
		ret = 0
		event,value = window.read(timeout=0)
		if (event ==sg.WIN_CLOSED) or ret ==-1:
			return -1
		for f in os.scandir(path):
			if f.is_file():
				event = window.read(timeout=0)
				if (event ==sg.WIN_CLOSED) or ret ==-1:
					return 0
				if f.name not in file_lib.filename:
					file_lib.filename[f.name] = None
					file_lib.filename2path.append(f.name+":::"+f.path)
				else:
					print("ERROR:Multiple instance found for '"+f.name+"'" )
				self.COUNT+=1
				window['progbar'].update_bar(self.COUNT)
			elif(ret!=-1):
				if f.is_dir():
					ret = self.all_subfolder(window,f.path)
				else:
					print("ERROR:Not a Directory '"+f.name+"'")
		return ret

	@dict_context
	def syncloop(self,dirl):
		dirlist = dirl.rstrip().split('\n')
		ret = 0
		if len(dirlist)>0:
			for mypath in dirlist:
				if os.path.isdir(mypath):
					total = 0
					self.COUNT = 0
					for root, directory, files in os.walk(mypath):
						total += len(files)
					Layout1 = [[sg.ProgressBar(total, orientation='h', size=(50, 20), key='progbar')]]
					window_p = gui( 'Loading '+mypath,Layout1)
					ret = self.all_subfolder(window_p, mypath)
					window_p.close()
					Layout1 =None
					window_p =None
					gc.collect()
					if ret ==-1:
						print("ERROR:Force stopped.")
						continue
					print("LOG:"+mypath+" is synced")
				else:
					print("ERROR:Invalid path '"+mypath+"'")
		file_lib.filename2path.sort()
		self.write_2_file()

	@syncer
	def findloop(self,inputlist,dest):
		'''
		
		
		'''
		inputlist = inputlist.rstrip().split('\n')
		dest = dest.rstrip().split('\n')
		self.COUNT = 0
		if os.path.isdir(dest[0]):
			if len(inputlist)>0:
				Layout1 = [[sg.ProgressBar(len(inputlist), orientation='h', size=(50, 20), key='progbar')]]
				window_p = gui( 'Coping to '+dest[0],Layout1)
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
						print("ERROR:Cannot find '"+file+"' in synced path.")
					self.COUNT+=1
				window_p.close()
				Layout1 =None
				window_p =None
				gc.collect()
		else:
			print("ERROR:Invalid dest. path '"+dest[0]+"'")
		return 1
'''Function Declarations'''
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
	##################################################################################
	# For testing
	# sync_file = file_lib()
	# sync_file.syncloop("/home/bmk/Downloads/")
	# del(sync_file)
	# findloop = file_lib()
	# findloop.findloop("main.exe\nmain.py","/home/bmk/Downloads/build/")
	# del(findloop)
	# sync_file = file_lib()
	# sync_file.syncloop("/media/bmk/alpha/Program Files (x86)/Audacity/")
	# del(sync_file)
	# findloop = file_lib()
	# findloop.findloop("main.exe\nmain.py","/home/bmk/Downloads/build/")
	# del(findloop)
	# return
	##################################################################################
	'''Initializing the main gui class'''
	window = gui()
	status = 1
	while status:
		'''GUI windows will be displayed until the exit button or (X) is clicked'''
		status = window.gui_button_process()
	window.close()			# Close the main gui
	window =None			# Clearing the link to the GUI class to optimize the memory
	gc.collect()			# To reduce the memory used by clearing the unreferenced objects


'''Main loop'''
if __name__ == "__main__":
	main_loop()			# Calling the Main function
	sys.exit("Bye.\nThanks for using Copier@BMK.")