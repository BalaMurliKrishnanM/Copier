import PySimpleGUI as sg
from pathlib import Path,PureWindowsPath
import os
import shutil
import time
#print(os.path.isdir("Paste the dir path where the <dir>/BPC and <dir>/SSM/Source and present:"))

count = 0
onlyfiles = {}
def all_subfolder(a,path, arr):
	global count
	ret = 0
	event,value = a.read(timeout=0)
	if (event ==sg.WIN_CLOSED) or ret ==-1:
		return -1
	for f in os.scandir(path):
		if f.is_file():
			event,value = a.read(timeout=0)
			if (event ==sg.WIN_CLOSED) or ret ==-1:
				return -1
			if f.name not in arr:
				arr[f.name] = f.path
			else:
				print("ERROR:Multiple instance found for "+f.name )
			count+=1
			a['progbar'].update_bar(count)
		elif(ret!=-1):
			ret = all_subfolder(a,f.path,arr)
	return ret


def mainloop(dirl):
	global count
	global onlyfiles
	dirlist = dirl.rstrip().split('\n')
	ret = 0
	if len(dirlist)>0:
		for mypath in dirlist:
			if os.path.isdir(mypath):
				total = 0
				count = 0
				for root, dirs, files in os.walk(mypath):
					total += len(files)
				layout1 = [[sg.ProgressBar(total, orientation='h', size=(50, 20), key='progbar')]]
				window_p = sg.Window('Loading', layout1)
				ret = all_subfolder(window_p, mypath, onlyfiles)
				window_p.close()
				if ret ==-1:
					print("ERROR:Force stopped.")
					continue
				print("LOG:"+mypath+" is synced")
			else:
				print("ERROR:Invalid path "+mypath)


def findloop(inputlist,dest):
	global onlyfiles
	inputlist = inputlist.rstrip().split('\n')
	dest = dest.rstrip().split('\n')
	if os.path.isdir(dest[0]):
		if len(inputlist)>0:
			for file in inputlist:
				if file in onlyfiles:
					print("LOG:Copying file "+onlyfiles[file])
					shutil.copy2(onlyfiles[file], dest[0])
					os.chmod(os.path.join(dest[0],file), 0o777)
				else:
					print("ERROR:Cannot find "+file+" in synced path.")
	else:
		print("ERROR:Invalid dest. path "+dest[0])
	
"""
sg.Print('Re-routing the stdout', do_not_reroute_stdout=False)
print('This is a normal print that has been re-routed.')


/media/bmk/alpha/Program Files (x86)/Audacity/

LICENSE.txt
wxstd.mo
wine ~/.wine/drive_c/Python37/Scripts/pyinstaller.exe ~/.wine/drive_c/Python37/temp/main.py
mainloop("/media/bmk/alpha/Program Files (x86)/Citrix/ICA Client/\n/media/bmk/alpha/Program Files (x86)/Audacity/")

find "/media/bmk/alpha/Program Files (x86)/Audacity/" -type f | wc -l
"""

layout = [[sg.Text('                                                                                                                                                                                                  Copier@BMK')],[sg.Text('Enter the Source Adress(es):')],
		  [sg.Text('Eg: \n/media/bmk/alpha/Program Files (x86)/Citrix/ICA Client/\n/media/bmk/alpha/Program Files (x86)/Audacity/',font=("Helvetica1", 9))],
		[sg.Multiline(default_text='Paste all the directory path in each line.',key='-IN-',size=(75, 5)),sg.Button('Sync')],
		[sg.Text('Dest. Address'),sg.Input(key='-dest-',size=(70, 2))],
		[sg.Button('Go'), sg.Button('Clear Path'),sg.Button('Clear Input'),sg.Button('Clear Output'), sg.Button('Exit')],
		  [sg.Text('List of Files:                                                                                         OUTPUT:')],
		[sg.Multiline(key='-INput-',default_text='Paste the list of files\nEach file in each line.\nEg:\nBPC_INIT_01.ice\nBPC_INIT_05.ice\nSSM_INIT_01.c\n',size=(50, 20)),sg.Output(size=(50,20), key='-OUTPUT-')]
		]

window = sg.Window('Copier', layout)


while True:
	#print(filename)
	event, values = window.read()
	if event == 'Clear Path':
		window['-IN-'].update('')
		continue
	if event == 'Clear Input':
		window['-INput-'].update('')
		continue
	if event == 'Clear Output':
		window['-OUTPUT-'].update('')
		continue
	#print(event, values['-IN-'])
	#a = PureWindowsPath(values['-IN-'])
	#a = Path(values['-IN-'])
	#print(os.path.isdir(a))
	if event in (sg.WIN_CLOSED, 'Exit'):
		sg.popup('Thanks for using Copier@BMK\nClosing...',auto_close=True,auto_close_duration=1)
		break
	if event == 'Go':
		findloop(values['-INput-'],values['-dest-'])
		continue
	if event == 'Sync':
		mainloop(values['-IN-'])
		continue
window.close()
