import sublime_plugin, os, subprocess, re, sublime, sys#, commands \\ Traceback (most recent call last): ... line 1, in <module> ... ImportError: No module named 'commands'

class Update(sublime_plugin.EventListener):
	def on_post_save(self, view):
		if "ifilter.github.io" in view.file_name():
			os.chdir(os.path.dirname(view.file_name()))
			#os.system('git commit -a --allow-empty-message -m ""', nowindow=True)
			print("saved" if subprocess.call('git commit -a --allow-empty-message -m ""', shell=True) == 0 else "NOT SAVED")
			return

		sys.path.append(os.path.dirname(__file__))
		import commands #(вообще импорта быть не должно, так как я на это отвлекаюсь)
		if view.file_name().endswith('.py'):
			pqi = view.file_name().find("pqmarkup")
			if pqi != -1:
				cwd = os.getcwd()
				os.chdir(view.file_name()[:pqi] + "pqmarkup")
				os.system('python runtests.py & pause')
				os.chdir(cwd)
				return

			def process(py_name, relative_dir, extension, cmdline_pars):
				if os.path.basename(view.file_name()) == py_name:
					for root, dirs, files in os.walk(os.path.join(os.path.dirname(view.file_name()), *(relative_dir + ["histori"]))):
						for name in files:
							if name.endswith(extension):
								print('PROCESSING ' + name)
								commands.exec_command(r'pythonw ' + view.file_name() + ' ' + cmdline_pars(os.path.join(root, name)))
			process('pq.txt2html.py', [".."], '.pq.txt', lambda fname : '"' + fname + '" "' + fname[:-7] + '\\index.html"')
			process('build.py', ["..", ".."], '.flac.txt', lambda fname : '"' + fname[:-4] + '"')
			return

		#for c in regex.finditer(R'\nЗАПИСАТЬ_В_ФАЙЛ\(‘(.*?)’,[ \n]*‘‘‘(?>[^‘’]*(?R)?)*\n’’’\)', view.substr(sublime.Region(0, view.size())), re.DOTALL):
		for c in re.finditer(R'(?:^|\n)ЗАПИСАТЬ_В_ФАЙЛ\(‘(.*?)’,[ \n]*‘‘‘(.*?\n)’’’\)', view.substr(sublime.Region(0, view.size())), re.DOTALL):
			fname = c.group(1)
			spos = 0
			for dropbox_possible_dir in ["\\Dropbox\\", "B:\\"]:
				i = view.file_name().find(dropbox_possible_dir)
				if i != -1:
					spos = i + len(dropbox_possible_dir)
					break
			file_contents = '[[[ИЗ '+view.file_name()[spos:]+']]]\n' + c.group(2)
			if os.path.exists(fname) and open(fname, "r", encoding="utf-8-sig").read() == file_contents:
				continue # file is not changed
			open(fname, "w", encoding="utf-8-sig").write(file_contents)
			if fname.endswith('.pq.txt'):
				subprocess.call(r'pythonw C:\!GIT-HUB\adamaveli.name\tools\pq.txt2html.py "' + fname + '" "' + fname[:-7] + '\\index.html"')
			#	subprocess.call( ‘pythonw C:\!GIT-HUB\adamaveli.name\tools\pq.txt2html.py "’fname‘" "’fname.last(7)‘\index.html"’)
			elif fname.endswith('.flac.txt'):
				subprocess.call(r'pythonw C:\!GIT-HUB\adamaveli.name\ge\verbao\build.py "' + fname[:-4] + '"') #, stderr = open(fname+'.log',"w"))
		return
