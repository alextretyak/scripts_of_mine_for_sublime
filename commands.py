import sublime, sublime_plugin, os, re, sys, binascii, urllib, subprocess, calendar, time, copy, unicodedata, inspect, math

#ИЗ http://stackoverflow.com/questions/11879481/can-i-add-date-time-for-sublime-snippet
import datetime, getpass
class AddDateTimeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        ms = ""
        pq = find_matching_paired_quotes(self.view.sel()[0])
        if pq != None:
            if self.view.substr(sublime.Region(pq.a-2, pq.a)) in ('TC', 'ТС'): # если курсор находится в блоке[/области] точки синхронизации, то повышаем точность вставляемого времени до миллисекунд
                ms = ("%.3f" % math.modf(time.time())[0])[1:]
        self.view.run_command("insert_snippet", { "contents": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S" + ms) })#({# БЫЛО: "("+str(int(time.time()))+"±X)" } )
    	# [-!{писал в pq.pq, вставил из [./м.txt]:‘...23:33 02.09.2016...’ и задумался: а почему такой формат то? где я это писал, в блокноте, что ли? псевдографику в блокноте? seriously?} проанализировать историю [изменений/]правок предыдущей строки кода {на основе ‘полной[!] истории [изменений/]правок данного файла’[https://www.dropbox.com/sh/bfz3ctnvq0db24t/AACyfEH87Zw2lvNfyY1PLs0ga]} и найти все форматы, в которых вставлялась дата посредством AddDateTimeCommand {скорее всего, также как и сейчас просто сломался box_drawing из-за чего сломался F5 из-за чего пришлось вставлять текущее датавремя через блокнот}-]
        #self.view.run_command("insert_snippet", { "contents": "("+str(int(time.time()))+"±?)" })
class AddEndDateTimeCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command("insert_snippet", { "contents": "(X±"+str(int(time.time()))+")" })# заменил `?±` на `х±` так как в имя файла `?` включать нельзя (пример: [._-'c.txt‘(1477051184±х)’][‘слишком много гордыни’])

def format_time(t):
	return time.strftime("%Y.%m.%d %H:%M:%S", time.gmtime(t))

def sassert(str1, str2, hard = True): # string [smart] assert
	import os, tempfile
	if str1 != str2:
		str1 = str(str1)
		str2 = str(str2)
		print("sassert FAILED!")
		for envvar in ['ProgramFiles', 'ProgramFiles(x86)', 'ProgramW6432']:
			os.environ["PATH"] += os.pathsep + os.getenv(envvar, '') + r'\KDiff3'
		command = 'kdiff3'
		for file in [('wrong', str1), ('right', str2)]:
			full_fname = os.path.join(tempfile.gettempdir(), file[0])
			command += ' "' + full_fname + '"'
			open(full_fname, "wt", encoding='utf-8-sig').write(file[1])
		os.system(command)
		if hard:
			assert(False)
		return False
	return True
def _sassert(str1, str2):
	return 0
def soft_assert(str1, str2):
	return sassert(str1, str2, False)
def hard_assert(str1, str2):
	return sassert(str1, str2, True)

import tempfile, webbrowser
def exec_command(cmd, output = None):
	tmpfile, fname = tempfile.mkstemp(text=True)
	tmpfile = open(tmpfile) #(#, "r+t", encoding = "utf-8")
	pc_start = time.perf_counter()
	r = subprocess.call(cmd, stdout = tmpfile, stderr = tmpfile)
	print('Execution time: %.2f [for command `%s`]' % (time.perf_counter() - pc_start, cmd))
	tmpfile.seek(0)
	s = tmpfile.read()
	print(s, end = '')
	if output != None:
		output.append(s)
	tmpfile.close()
	os.remove(fname)
	return r

def khrono_log_ready():
	khlog_view = sublime.active_window().find_open_file("B:\\х.лог.txt")
	if khlog_view:
		sublime.active_window().focus_view(khlog_view) # ред:переключи[_вид_на]_файл(‘B:\х.лог.txt’) или ред:покажи_файл(‘B:\х.лог.txt’)
		if khlog_view.is_dirty():
			sublime.error_message("Пожалуйста, приведите файл в порядок!\n(К состоянию/виду `х`)!")
			return None
	else:
		khlog_view = sublime.active_window().open_file("B:\\х.лог.txt")#(#, sublime.TRANSIENT) # ред:открой(‘B:\х.лог.txt’)
	return khlog_view

def khrono_log(text):
	khlog_view = khrono_log_ready()
	assert(khlog_view)
	khlog_view.sel().clear()
	khlog_view.sel().add(sublime.Region(khlog_view.size(), khlog_view.size())) # khlog_view.caret_pos = @-0 \ ред:каретка = @-0 \\ ред:каретки для много-курсорного редактирования
	if khlog_view.substr(sublime.Region(khlog_view.size()-1, khlog_view.size())) != "\n": # khlog_view.str[@-1] # ред:текст[@-1]
		khlog_view.run_command("append", { "characters": "\n" } ) # ред:вставь("\н")
	khlog_view.run_command("append", { "characters": "\n" } )
	khlog_view.run_command("add_date_time")
	khlog_view.run_command("append", { "characters": "\n" + text } )
	khlog_view.show(khlog_view.size())
	khlog_view.run_command("save")

def view():
	return sublime.active_window().active_view()

def find_line_with_date(direction, return_date=False):
	"""
	Ищет строку с датой в заданном направлении.
	"""
	line = view().full_line(view().sel()[0].begin()) # получаем диапазон (начало и конец) строки под курсором.
	while True:
		date_time = parse_date_time(view().substr(line).rstrip("\n"))
		if date_time:
			return date_time if return_date else line
		if direction < 0:
			if line.begin() == 0:
				return sublime.Region(0, 0)
			line = view().full_line(line.begin() - 1)
		else:
			if line.end() == view().size():
				return sublime.Region(view().size(), view().size())
			line = view().full_line(line.end() + 1)

def split_len(seq, length):
    return [seq[i:i+length] for i in range(0, len(seq), length)]

def rotate_2d_array_clockwise_by_90_deg(original):
	return [list(a) for a in zip(*original[::-1])] # from [http://stackoverflow.com/questions/8421337/rotating-a-two-dimensional-array-in-python]

class replace_selection_with_command(sublime_plugin.TextCommand):
	def run(self, edit, characters):
		self.view.replace(edit, self.view.sel()[0], characters)

def replace_selection_with(characters):
	view().run_command("replace_selection_with", { "characters": characters } )

box_drawing_chars_1 = '─│─│ ┌┐┘└ ├┬┤┴ ┼ └'
box_drawing_chars_2 = '═║═║ ╔╗╝╚ ╠╦╣╩ ╬ └'
box_drawing_chars_DEFAULT = box_drawing_chars_1
def box_drawing(text, box_drawing_chars = box_drawing_chars_DEFAULT):
	box_drawing_chars_iter = iter(box_drawing_chars.split(" "))
	patterns_str = """
 ●●  x   xx ●●● xxx xxx ●●●  ● \n\
●─● ●─● ●─x ●─● ●─● ●─● ●─● ●─●
 ●●  x   xx  x  x●● ●●x  ●  ●●●

xx  ●●● ●xx --- +--
x┌● x┌● ●┌● -┌+ +┌+
x●  x●x ●●x ++- -+-

 ●   ●x
х├● х├●
 ●x  ●

x●x
●┼●
x●x

|| \n\
.└.
\..
"""
	patterns = [] # массив со всеми возможными [раскрытыми (повёрнутыми)] паттернами

	for pattern_str in patterns_str.strip("\n").split("\n\n"):
		# pattern_str is like this:
		# xxx xxx ●●●
		# ●─● ●─x ●─●
		# xxx xxx xxx
		box_drawing_c = next(box_drawing_chars_iter) # example: "─│"
		pattern = {}
		for line_str in pattern_str.split("\n"):
			# line_str is
			# xxx xxx xxx ●●● xxx
			for pattern_index, line in enumerate(split_len(line_str, 4)):
				# line is like ‘xxx ’
				line = line[:3] # обрезаем строку до 3 символов
				line += ' ' * (3-len(line)) # дополняем строку пробелами ровно до 3 штук
				pattern[pattern_index] = pattern.get(pattern_index, []) + [list(line)]
		# now pattern should be filled with:
		# {0: ["xxx", "●─●", "xxx"],
		#  1: ["xxx", "●─x", "xxx"],
		#  2: ["●●●", "●─●", "xxx"]}

		if box_drawing_chars.startswith('─'): # для второго набора паттернов ("═...") проверка ниже корректно работать не будет [ложное срабатывание]
			for i, p in pattern.items():
				assert(p[1][1] == box_drawing_c[0]) # проверяем, что в середине паттерна всегда находится правильный символ

		for oriented_box_drawing_c in box_drawing_c:
			for i in pattern:
				pattern[i][1][1] = oriented_box_drawing_c
			patterns += pattern.values() # добавляем все повёрнутые паттерны из pattern в patterns
			for i in pattern:
				pattern[i] = rotate_2d_array_clockwise_by_90_deg(pattern[i])

	lines = text.split('\n')

	def get(x, y):
		if (not y in range(len(lines))) or (not x in range(len(lines[y]))):
			return '\0'
		return lines[y][x]

	def need_box_drawing(c):
	    return c in "*─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"

	def check_pattern(pattern, x, y):
		for dy in [-1,0,1]:
			for dx in [-1,0,1]:
				if not (dx == 0 and dy == 0):
					c = pattern[1+dy][1+dx]
					if c == ' ': # в этом случае значение безразлично
						continue
					bd = need_box_drawing(get(x+dx, y+dy))
					if c in 'xхХX-': # здесь не должно быть box-drawing-элемента
						if bd:
							return None
					elif c in 'oOоО●+': # здесь должен быть box-drawing-элемент
						if not bd:
							return None
		return pattern[1][1] # прошли все тесты - паттерн подходит - возвращаем символ для замены (всегда в середине паттерна)

	result = ''
	for y, line in enumerate(lines):
		for x, c in enumerate(line):
			if not need_box_drawing(c):
				result += c
				continue

			r = '?'
			for pattern in patterns:
				cp_res = check_pattern(pattern, x, y)
				if cp_res:
					r = cp_res
					break

			result += r
		result += "\n"
	return result[:-1] # `[:-1]` чтобы убрать последний \n

# Some tests:
def check_box_drawing(s):
	sassert(box_drawing(s), s, False)
check_box_drawing("""
           ┌─────┐
         │ └─────┘
         │
         │ ┌─────┐
         │ │     │
         │ │     │
 ─────┐  │ └─────┘
      │  │
      │  │
  ────┘  └────────

  ────────────────
""")
check_box_drawing("""
┌┐
└┘
""")
check_box_drawing("""
┌─┐
│ │
└─┘
""")
check_box_drawing("""
┌─┬─┐
│ │ │
└─┴─┘
""")
check_box_drawing("""
   377
   S E
B   │   L
U ──┼── L
 T  │  E \n\
  TON C
""")
sassert(box_drawing("""
B   *   L
U ──┼── L
 T  *  E \n\
"""),"""
B   │   L
U ──┼── L
 T  │  E \n\
""")
'''sassert(box_drawing("""
 │
***─────┬──────────────────────────────┐""" # раньше было `???` вместо `***`
"""
│$│СЛОВО│ПОЧЕМУ ЗАПРЕЩЕНО              │
"""),"""
 │
┌┴┬─────┬──────────────────────────────┐
│$│СЛОВО│ПОЧЕМУ ЗАПРЕЩЕНО              │
"""
)'''
check_box_drawing( # раньше было два `?`
"""
1⣀3──ЭТО──┐ИЛИ┌┐1
         ││ИЛИ││2
         └┘ИЛИ└┘3
""")
check_box_drawing( # раньше было два `?`
"""
1⣀3──ЭТО─┬─ИЛИ──1
         │
         ├─ИЛИ──2
         │
         └─ИЛИ──3
""")
#1..3──ЭТО─┬─ИЛИ══1
#          ├─ИЛИ══2
#          └─ИЛИ══3
check_box_drawing("""
┌───────────────┐
│ ┌───────────┐ │
│ │ ┌───────┐ │ │
│ │ │       │ │ │
│ │ │       │ │ │
│ │ │       │ │ │
│ │ └───────┘ │ │
│ └───────────┘ │
└───────────────┘
""")
# soft_assert(box_drawing("""
#   ||
#   ... Wперёд
#   \..
# """),"""
#   ││
#   │└─ Wперёд
#   └──
# """)
'''
check_box_drawing("""
┌──────────────┐
│ ┌────┐       │
│ │|   │       │
│ └────┘       │
├──────────────┤
│ ┌───┐        │
│ │ 1 │        │
│ └───┘        │
│       ┌────┐ │
│       │1|  │ │
│       └────┘ │
├──────────────┤
│ ┌───┐        │
│ │ 2 │        │
│ └───┘        │
│       ┌────┐ │
│       │12| │ │
│       └────┘ │
├──────────────┤
│ ┌──────┐     │
│ │Ctrl+Z│     │
│ └──────┘     │
│       ┌────┐ │
│       │1|  │ │
│       └────┘ │
└──────────────┘
""")
'''
check_box_drawing("""
───┐
   ├─ РАЗРЫВ
───┘
""")
check_box_drawing( # {[
"""
┌─────┐ ┌─────────┐
│ }   │ │         │
│ ] Ъ │ │         │
└─────┘ └─┐ ENTER │
  ┌─────┐ │       │
  │ | / │ │       │
  │ \   │ │       │
  └─────┘ └───────┘
""")
'''check_box_drawing("""
        │ Enter◄-/      │
        │               │
        └───────────────┘
   ┌────────────┐ ┌─────┐
   │ △ Shift    │ │ |   │
   │            │ │ \   │
   └────────────┘ └─────┘
""")'''

temp_edit_view = None
class OnPreCloseListener(sublime_plugin.EventListener):
	def on_pre_close(self, view):
		global temp_edit_view
		if view == temp_edit_view:
			temp_edit_view_prev_view.run_command("replace_selection_with", { "characters": view.substr(sublime.Region(0, view.size())) } )

class f4_command(sublime_plugin.TextCommand):
	def remove_all_balanced_chars_pairs(self, edit):
		text = self.view.substr(sublime.Region(0, self.view.size()))
		# line_end = -1
		erase_chars = []
		# while line_end < len(text):
		# 	line_start = line_end + 1
		# 	line_end = text.find("\n", line_start)
		# 	if line_end == -1:
		# 		line_end = len(text)
		# 	for pair in ['‘’', '()', '{}', '[]']:
		# 		cnt = text.count(pair[0], line_start, line_end)
		# 		if cnt > 0 and cnt == text.count(pair[1], line_start, line_end):
		# 			for c in re.compile("[" + pair[0] + ("\\" if pair == '[]' else '') + pair[1] + "]").finditer(text, line_start, line_end):
		# 				erase_chars.append(c.start())
		# выше написана вообще какая-то хрень :)(:
		i = 0
		while i < len(text):
			if text[i] in "‘({[": # ]})’
				end = find_ending_bracket(text, i, text[i], {"‘": "’", "(": ")", "{": "}", "[": "]"}[text[i]], None)
				if end != None: # если find_ending_bracket вернёт 0, то `if end:` сработает также как и с None (в данном случае, конечно, это не важно, так как find_ending_bracket не может вернуть 0, но вообще, если переменная может быть None, тогда её обязательно проверять на None, неявно преобразовывать не None в True — недопустимо, я считаю)
					erase_chars.extend([i, end])
			i += 1

		for pos in sorted(erase_chars, reverse = True):
			self.view.erase(edit, sublime.Region(pos, pos+1))

	def edit_selection_in_separate_buffer(self, edit):
		global temp_edit_view, temp_edit_view_sel, temp_edit_view_prev_view
		temp_edit_view = sublime.active_window().new_file()
		temp_edit_view.set_scratch(True)
		temp_edit_view.insert(edit, 0, self.view.substr(self.view.sel()[0]))
		temp_edit_view.set_name(" ")
		temp_edit_view_prev_view = self.view

	def hide_cursor(self, edit):
		self.view.sel().clear()

	def run(self, edit, shift_key_pressed = False, redirect_method = None):
		if redirect_method != None:
			getattr(self, redirect_method)(edit)
			return

		selected_text = self.view.substr(self.view.sel()[0])
		result = ''

		if not shift_key_pressed:
			if selected_text.startswith('C:\\'):
				subprocess.call('explorer "' + selected_text + '"')
				return

			if selected_text == "" and self.view.substr(sublime.Region(self.view.sel()[0].begin()-1, self.view.sel()[0].begin()+1)) == "[]":
				clip = sublime.get_clipboard(1000)
				for dropbox_possible_dir in ["\\Dropbox\\", "B:\\"]:
					i = clip.find(dropbox_possible_dir)
					if i != -1:
						self.view.run_command("insert_snippet", { "contents": "./"+clip[i+len(dropbox_possible_dir):].rstrip('"').replace("\\", "/") } )
						return

			# [[[balancing ‘]]]
			if len(selected_text) == 2 and selected_text[1] == '’':
				replace_selection_with(unicodedata.normalize('NFC', selected_text[0].replace('о','o').replace('а','a').replace('е','e') + "\u0301"))
				return
			if selected_text == "ae": replace_selection_with("æ") # This line of code is [-as ‘gracefully devoted to’ is not founded via context.reverso.net (see [http://context.reverso.net/перевод/английский-русский/gracefully+devoted+to]), I'd like to perform the following search in context.reverso.net: ‘#adjective# devoted to’-] devoted to [miss[is]] Deep Græy.

			try:
				if re.match(R"[\da-fA-F]+$", selected_text) and 2 <= len(selected_text) <= 5: # сдалал поддержку multiple selection для обработки файла cp866.txt
					for sel_region in self.view.sel():
						sel_str = self.view.substr(sel_region)
						if 2 <= len(sel_str) <= 5:
							self.view.replace(edit, sel_region, sel_str + ' ' + chr(int(sel_str, 16)))
					return

				result = (urllib.parse.unquote(selected_text).replace(' ', '%20') if selected_text.startswith('http') or selected_text.startswith('file:///') else
						  selected_text+' ' + datetime.datetime.fromtimestamp(int(selected_text)).strftime("%Y.%m.%d %H:%M:%S") if selected_text.isdigit() and 5<=len(selected_text)<=10 else
	#					  selected_text+' ' + str(ord(selected_text)) + '=' + hex(ord(selected_text)) if len(selected_text) == 1 else
	#					  selected_text+' ' + chr(int(selected_text, 16)) if 2 <= len(selected_text) <= 5 else
					#	  selected_text.replace('А','A').replace('В','B').replace('С','C').replace('Д','D').replace('Е','E').replace('Ф','F').replace(' ', '').replace("\n", '') if re.match(R"[0-9АВСДЕФ \n]+$", selected_text) else
					#	  selected_text.replace('A','А').replace('B','В').replace('C','С').replace('D','Д').replace('E','Е').replace('F','Ф').replace(' ', '').replace("\n", '') if re.match(R"[0-9ABCDEF \n]+$", selected_text) else
						  '')#(#selected_text+' ' + '?ЧТО ДЕЛАТЬ?')
			except:
				#result = selected_text + ' !EXCEPTION!'
				view().show_popup("!EXCEPTION!")
				return

			if result == '':
				m = re.match(r"(?:(?:БЕ|РА|НЕ)\.\d\d?\.)?(\d\d?):(\d\d?):(\d\d) ", selected_text)
				if m:
					t = parse_date_time(selected_text[m.end():])
					if t:
						start = t - (int(m.group(1))*3600 + int(m.group(2))*60 + int(m.group(3)))
						result = selected_text + "\n" + format_time(start) + "\n" + format_time(start + 21839)

		if result == '':
			if not shift_key_pressed:
			   #if len(selected_text) == 1 and len(self.view.sel()) == 1: # выбран только один символ — показываем информацию по нему\show character info
				if len(selected_text) == 1                              : # выбран только один символ — показываем информацию по нему\show character info
					jhjh = []
					for selected_text in self.view.sel():                          # (red:selection L(selected_text)
					   jhjh+=[(self.view.substr(selected_text),selected_text.b)]   #    [+] (|self.view.substr(selected_text), selected_text.b|)) L(selected_text)
					gdfgh = []                                                     #
					for selected_text in jhjh:                                     #       [+] selected_text[0]‘<br>’selected_text[0].code.dec‘<br>’selected_text[0].code.hex‘<br>’selected_text[0].code.oct‘<br>’unicodedata:name(selected_text[0], "!EXCEPTION!")
					   gdfgh += [selected_text[0].replace('&', '&amp;').replace('<', '&lt;') + "<br>" + str(ord(selected_text[0])) + "<br>" + hex(ord(selected_text[0])) + "<br>" + oct(ord(selected_text[0])) + "<br>" + unicodedata.name(selected_text[0], "!EXCEPTION!")]
					view().show_popup((3*"<br>").join(gdfgh), max_height=sys.maxsize)
					return
				"""	:view.show_popup(
	Char(selected_text).code‘<br>
	’hex(Char(selected_text).code)‘<br>
	’unicodedata:name(selected_text, "!EXCEPTION!"))
	"""

				#+(1476744520±?)'‘
				# Всплывающее окно по дате в таком формате: (1476744520±?)
				cu_brackets = self.view.sel()[0]
				for l in range(1):
					cu_brackets = find_matching_cu_brackets(cu_brackets)
					if cu_brackets == None:
						break
					cu_str = self.view.substr(sublime.Region(cu_brackets.begin(), cu_brackets.end()))
					r = re.match(R"^\((?:(\d+)±[?ХXхx]|[хxХX?]±(\d+))\)$", cu_str)
					if r:
						view().show_popup(datetime.datetime.fromtimestamp(int(r.group(1) or r.group(2))).strftime("%Y.%m.%d %H:%M:%S"))
						return
				#(‘’)’'

				#Этот код показывает разницу (количество секунд и минут[+ и часов+]) между двумя выделенными датами
				if len(self.view.sel()) == 2 and parse_date_time(self.view.substr(self.view.sel()[0])) and parse_date_time(self.view.substr(self.view.sel()[1])):
					s=(parse_date_time(self.view.substr(self.view.sel()[1]))
					 - parse_date_time(self.view.substr(self.view.sel()[0])))
					assert((s//60//60)*3600 + (s//60%60)*60 + (s%60) == s)
					view().show_popup(str(s)+"сек<br>"+str(s//60)+"мин "+str(s%60)+"сек<br>"+str(s//60//60)+"ч "+str(s//60%60)+"мин "+str(s%60)+"сек<br>"+str(round(s/(60*60*24), 3))+' дней')
					return

				# Если курсор/выделение находится внутри [-невыполненной-] задачи, то помечаем её как [+выполненную+]
				sq_brackets = None
				if selected_text.startswith('[-') and selected_text.endswith('-]'): # либо если задача выделена целиком (что происходит по нажатии F12 в списке ДЕЛА)
					sq_brackets = self.view.sel()[0]
				else: # if selected_text == '': # разрешаем/допускаем также случай, когда выделен текст внутри задачи (что происходит по нажатии F12 в списке дел под календарём)
					sq_brackets = find_matching_sq_brackets(self.view.sel()[0])
				if sq_brackets:
					sq_brackets.a += 1
					sq_brackets.b -= 1
					sq_str = self.view.substr(sq_brackets)
					if len(sq_str) > 1 and sq_str[0] == '-' and sq_str[-1] == '-': # проверка len(sq_str) > 1 нужна, чтобы запись [-] не считалась как задача
						if sublime.ok_cancel_dialog("Выполнили задачу?"):
							self.view.sel().clear()
						#	self.view.sel().add(sublime.Region(sq_brackets.a, sq_brackets.a+1))
							self.view.sel().add(sublime.Region(sq_brackets.b-1, sq_brackets.b))
							self.view.replace(edit, sublime.Region(sq_brackets.a, sq_brackets.a+1), '+')
							self.view.replace(edit, sublime.Region(sq_brackets.b-1, sq_brackets.b), '+')
							return

			def pq_to_html(habr_html = False, comment = False, to_bbcode = False):
				pq_text = selected_text
				whole_file = False
				if pq_text == "": # находим всю запись в том месте, где стоит курсор
					if view().file_name() and view().file_name().endswith('.pq'): # в файлах .pq всегда берём весь текст (дневники будут в формате .txt или .pq.txt)
						if view().file_name().startswith(r'C:\!GIT-HUB\alextretyak.ru\comm\compiler.su'):
							for fmt_char in '*"=/_-.':
								for fmt in ('(' + fmt_char*2, fmt_char*2 + ')'):
									r = view().find(fmt, 0, sublime.LITERAL)
									if r != sublime.Region(-1) \
									   and view().substr(r.begin() + (3 if fmt[0] == '(' else -1)) != '.': # ) # for `(...)` in `фн внешняя_функция(...)`
										if fmt == '(--' and view().substr(sublime.Region(r.begin()-3, r.begin())) == 'if ': # for `if (--nesting_level == 0)` # )
											continue
										view().sel().clear()
										view().sel().add(r)
										view().show(r)
										return
						pq_text = view().substr(sublime.Region(0, view().size()))
						whole_file = True
					else:
						pq_text = view().substr(sublime.Region(find_line_with_date(-1).end(), find_line_with_date(1).begin())).rstrip("\n")

				#try:
				if True:
					# from importlib.machinery import SourceFileLoader # https://stackoverflow.com/a/67692/2692494 <- google:‘python import py file as different module name’
					# pqmarkup = SourceFileLoader("pqmarkup", R"C:\!!BITBUCKET\pqmarkup\pqmarkup.py").load_module() # закомментировал так как встроенный в SublimeText Python 3.3.6 не поддерживает type hints
					# pq_html = pqmarkup.to_html(pq_text, ohd = 1 if not habr_html else 0, habr_html = habr_html)
					# if habr_html:                      # // dirty hack
					#     sublime.set_clipboard(pq_html) # \\ (just left it as is)
					#     return

					if to_bbcode:
						pq_text = re.sub(r'\n(\d+\.) ', r'\n\1' + '\xA0', pq_text) # ordered lists

					def set_habr_html(html):
						if comment:
							html = html.replace('<br />', '').replace("</blockquote>\n", '</blockquote>').replace("</ol>\n", '</ol>').replace("</ul>\n", '</ul>')
						if to_bbcode:
							html = html.replace('<br />', '').replace('&quot;', '"').replace('&lt;', '<').replace('<li>', '').replace('</li>', '')
							html = re.sub(r'<!--[\s\S]+?-->', '', html) # remove comments
							simple_tags = {'b', 'i', 'u', 's', 'table', 'tr', 'td', 'ul', 'sup', 'sub'}
						#	closing_tags = {'a': 'url'}
							complex_tags = {'a':('url', 'href'), 'spoiler':('spoiler', 'title'), 'font':('color', 'color'), 'abbr':('abbr', 'title')}
							def repl(m):
								tag = m.group(1)
								if tag in simple_tags or (tag[0] == '/' and tag[1:] in simple_tags):
									return '[' + tag + ']'
								if tag ==  'blockquote': return  '[quote]'
								if tag == '/blockquote': return '[/quote]'
								if tag ==  'code': return  '[font=Courier New]'
								if tag == '/code': return '[/font]'
								if tag ==  'source': return  '[code]'
								if tag == '/source': return '[/code]'
								if tag[0] == '/' and tag[1:] in complex_tags:
									return '[/' + complex_tags[tag[1:]][0] + ']'
								if ' ' in tag:
									mm = re.match('([^ ]+) ([^=]+)=(.+)$', tag) # `re.fullmatch()` appeared in Python 3.4
									if mm is not None:
										if mm.group(1) == 'source':
											assert(mm.group(2) == 'lang')
											return '[code]'
										if mm.group(1) in complex_tags:
											bbtag, attribute = complex_tags[mm.group(1)]
											assert(mm.group(2) == attribute)
											return '[' + bbtag + '=' + mm.group(3) + ']'
										elif mm.group(1) == 'img':
											assert(mm.group(2) == 'src')
											return '[img]' + mm.group(3)[1:-3] + '[/img]'
								return m.group()
							html = re.sub(r'<([^>]+)>', repl, html)
						sublime.set_clipboard(html)

					fname = os.getenv('TEMP') + r'\pq_to_html'
					#with open(fname + '.html', 'w', encoding = 'utf-8') as f:
					#	f.write(pq_html)
					#webbrowser.open(fname + '.html')
					output = []

					with open(fname + '.pq.txt', 'w', encoding = 'utf-8') as f:
						f.write(pq_text)
					add_cmd_par = '--habr-html' if habr_html else '--output-html-document'
					if (whole_file # чтобы работали относительные ссылки на картинки и на другие страницы статических сайтов (пример статического сайта: [https://github.com/pqmarkup/pqmarkup.github.io])
					        and (os.path.isdir(os.path.splitext(view().file_name())[0]) # такая "залепская" проверка для файлов, которым не требуется создавать index.html, например: B:\Статьи\pq.pq\pq.pq
					          or os.path.basename(view().file_name()) == ".pq")): # для файлов `.pq` (например файл `.pq` в [https://github.com/pqmarkup/pqmarkup.github.io]) проверка в предыдущей строке не работает, поэтому учитываем их специально
						html_fname = view().file_name()
						if html_fname.endswith(".pq"):
							html_fname = html_fname[:-3]
						# if html_fname.endswith("/"): html_fname = html_fname[:-1] # это необязательно
						html_fname += "/index.html"
						if exec_command(r'pythonw C:\!!BITBUCKET\pqmarkup\pqmarkup.py ' + add_cmd_par + ' "' + fname + '.pq.txt" -f "' + html_fname + '"', output) == 0: # файл может быть не сохранён, поэтому используем `fname`, а не `view().file_name()`
							if habr_html:
								set_habr_html(open(html_fname, encoding = 'utf-8').read())
							else:
								webbrowser.open(html_fname)
					else:
						if exec_command(r'pythonw C:\!!BITBUCKET\pqmarkup\pqmarkup.py ' + add_cmd_par + ' "' + fname + '.pq.txt" -f "' + fname + '.html"', output) == 0:
							if habr_html:
								set_habr_html(open(fname + '.html', encoding = 'utf-8').read())
							else:
								webbrowser.open(fname + '.html')
						#else:
						#	sublime.message_dialog('ERROR (see console for details)')
				#except pqmarkup.Exception as e:
				if len(output) and len(output[0]):
					rer = re.match(R'(.+) at line (\d+), column (\d+)', output[0])
					start = (0 if rer.group(2) == '1' else [s.start(0) for s in re.finditer(R'\n', pq_text)][int(rer.group(2)) - 2] + 1) + int(rer.group(3)) - 1
					message = rer.group(1)
					if selected_text != '':
						start += self.view.sel()[0].begin()
					elif not whole_file:
						start = find_line_with_date(-1).end() + start
					r = sublime.Region(start, start+1)
					view().sel().clear()
					view().sel().add(r)
					view().show(r)
					sublime.message_dialog(message)
			def pq_remove_comments_and_copy_to_clipboard():
				#sublime.set_clipboard(re.sub(R'\[\[\[(.*?)]]]', '', selected_text))
				nonlocal selected_text
				while True:
					i = selected_text.find("[[[") # ]]]
					if i == -1: break
					selected_text = selected_text[0:i] + selected_text[find_ending_sq_bracket(selected_text, i)+1:]
				sublime.set_clipboard(selected_text)
			def pq_remove_deep_comments_and_copy_to_clipboard():
				#sublime.set_clipboard(re.sub(R'\[\[\[\[(.*?)]]]]', '', selected_text, flags=re.DOTALL))
				nonlocal selected_text
				while True:
					i = selected_text.find("[[[[") # ]]]]
					if i == -1: break
					selected_text = selected_text[0:i] + selected_text[find_ending_sq_bracket(selected_text, i)+1:]
				sublime.set_clipboard(selected_text)

			def compilersu_markup_to_pq():
				nonlocal selected_text
				pq = ''
				i = 0
				writepos = 0
				fmt_trans_dic = {'**':'*', '//':'~', '__':'_', '--':'-', '/\\':'/\\', '\\/':'\\/'}
				quotes_stack = []
				while i < len(selected_text):
					if selected_text[i] == '(' or (selected_text[i] == ')' and i-2 >= writepos):
						left_br = selected_text[i] == '('
						offset = 1 if left_br else -2
						fmt = selected_text[i+offset:i+offset+2]
						if fmt in fmt_trans_dic or fmt in ('""', '==', '..'):
							if not left_br:
								i -= 2
							pq += selected_text[writepos:i]
							i += 3
							writepos = i
							if left_br:
								if fmt in fmt_trans_dic:
									pq += fmt_trans_dic[fmt] + '‘' # ’
								elif fmt == '==':
									i = selected_text.find('==)', i)
									pq += '#‘' + selected_text[writepos:i] + '’' if selected_text[writepos] == "\n" else '`' + selected_text[writepos:i] + '`'
									i += 3
									writepos = i
								else:
									assert(fmt in ('""', '..'))
									pq += '>' if fmt == '""' else '.' # (
									j = selected_text.find(fmt + ')', i)
									need_quotes = "\n" in selected_text[i:j]
									pq += '‘' if need_quotes else ' '
									quotes_stack.append(need_quotes)
							else:
								if fmt in ('""', '..'):
									if not quotes_stack.pop():
										continue
								pq += '’'
							continue
					i += 1
				pq += selected_text[writepos:]
				sublime.set_clipboard(pq)

			def prev_versions():
				dir = view().file_name().replace("Dropbox\\", "Dropbox\\.-\\", 1).replace("B:\\", "B:\\.-\\", 1) + '-'
				os.startfile(os.path.join(dir, os.listdir(dir)[0]))
			def folder_of_that_day():
				date_time = find_line_with_date(-1, True)
				if date_time:
					stime = time.strftime("%Y.%m.%d", time.gmtime(date_time))
					dir = os.path.join(os.path.dirname(view().file_name()), "[" + os.path.basename(view().file_name() + "]"), stime[-7:] if int(stime[:4]) < 2020 else stime)

					if not os.path.isdir(dir):
						stime = time.strftime("%Y-%m-%d", time.gmtime(date_time))
						dir = os.path.join(os.path.dirname(view().file_name()), "[" + os.path.basename(view().file_name() + "]"), stime)

					if not os.path.isdir(dir):
						if not sublime.ok_cancel_dialog("Каталог '" + dir + "' не найден! Создать?"):
							return
						os.mkdir(dir)
					subprocess.call('explorer "' + dir + '"')

			def box_drawing_chars(box_drawing_chars):
				result = box_drawing(selected_text, box_drawing_chars)
				replace_selection_with(result) # insert и insert_snippet работают неправильно в случае выделения только первой строки (например: "           ┌─────┐\n").
				result = ''

			def find_first_non1251_char():
				try:
					view().substr(sublime.Region(0, view().size())).encode('latin-1') #(#'cp1251')
				except UnicodeEncodeError as e:
					view().sel().clear()
					r = sublime.Region(e.start, e.end)
					view().sel().add(r)
					view().show_at_center(r)

			def find_differences_between_encodings():
				for i in range(256):
					codecs.decode()
					# chr(i).encode('latin-1')
					# chr(i).encode('ascii')

			def reverse_order():
				replace_selection_with("".join(reversed(selected_text)))

			def split_selection_into_characters():
				newsel = []
				for r in self.view.sel(): # [-$Добавить такую возможность: copy($$‘2*3*"прошу прощения"’)-]
				   #for x in range(r.a, r.b): # ТАК НЕ РАБОТАЕТ если выделять символы справа налево!!!
					for x in range(r.begin(), r.end()):
						newsel += [sublime.Region(x, x+1)]
				self.view.sel().clear()
				self.view.sel().add_all(newsel)

			def remain_in_selection_this_characters(chars):
				newsel = []
				for r in self.view.sel():
					for x in range(r.begin(), r.end()):
						if self.view.substr(x).upper() in chars:
							newsel += [sublime.Region(x, x+1)]
				self.view.sel().clear()
				self.view.sel().add_all(newsel)

			def beautify_table():
				lines = selected_text[:-1].split("\n")
				column_separator = ".?─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬"
				columns_count = 0
				# Считаем количество столбцов
				for c in lines[1][1:]: # во второй строке должен быть заголовок таблицы (`[1:]` — чтобы пропустить/‘не учитывать’ первый символ строки)
					if c in column_separator:
						columns_count += 1
				sassert(columns_count, len(re.split('['+column_separator+']', lines[1]))-2)
				# Считаем ширину каждого столбца (максимальное количество символов в каждом столбце среди всех строк)
				columns_w = [0 for _ in range(columns_count)]
				for line in lines:
					if line[1:2] in column_separator: # это либо первая строка, либо строка-сплошная_линия, отделяющая заголовок — пропускаем такие строки
						continue
					сс = re.split('['+column_separator+']', line)
					for c in range(len(сс)-2):
						columns_w[c] = max(columns_w[c], 1 + len(сс[c+1].strip()) + 1)
				# Пишем красиво отформатированную таблицу
				res = ''
				for line in lines:
					res += "."
					if line[1:2] in column_separator: # это либо первая строка, либо строка-сплошная_линия, отделяющая заголовок — заполняем такие строки по ширине таблицы
						res += "."*(sum(columns_w)+len(columns_w))
					else:
						сс = re.split('['+column_separator+']', line)
						for c in range(len(сс)-2):
							res += ("{:"+str(columns_w[c])+"}").format(" " + сс[c+1].strip() + " ") + "."
					res += "\n"
				replace_selection_with(res)

			def count_total_expenses():
				extractions = []
				self.view.find_all("(\d+)Р", 0, R"\1", extractions)
				self.view.show_popup(str(sum([int(e) for e in extractions])))

			def check_balance_of_all_char_pairs(): # [-[[[FIX TO ]]]CORRECT https://s.mail.ru/Hyii/M6iAbpmM4-]
				text = self.view.substr(sublime.Region(0, self.view.size()))
				class IntException(Exception):
					def __init__(self, i):
						self.i = i
				try:
					for pair in ['‘’', '()', '{}', '[]']: # \\\ #L(pair) [‘‘’’, ‘()’, ‘{}’, ‘[]’] \\ либо признак compile-time-unroll, короче, это должно быть явно/чётко видно по исходному коду, что цикл разворачивается в compile-time или нет (если не указать разворачивать цикл, а компилятор посчитает что с >66.6% вероятностью целесообразно его развернуть, тогда компилятор будет предлагать поставить указание для разворачивания цикла)
						i = 0
						while i < len(text):
							if text[i] == pair[0]:
								start_i = i
								nesting_level = 1
								i += 1
								while True:
									if i == len(text):
										raise IntException(start_i)
									ch = text[i]
									i += 1
									if ch == pair[0]:
										nesting_level += 1
									elif ch == pair[1]:
										if pair[0] == '(': # это должна быть compile-time (а не run-time) проверка # \\\ I pair[0] == ‘(’
											assert(pair[1] == ')')                                                 # \\\    #assert(pair[1] == ‘)’)
											if text[i-1:i] == ':' and text[i+1:i+3] == '(:':                       # \\\    I text[(i-1, i+1..+2)] == (‘:’, ‘(:’)
												assert(text[i] == ')')                                             # \\\       #assert(text[i] == ‘)’)
												i += 2 # пропускаем, чтобы смайлы :)(: не [ломали/]портили баланс
												continue
										nesting_level -= 1
										if nesting_level == 0:
											break
							elif text[i] == pair[1]:
								if pair[0] == '(': # это должна быть compile-time (а не run-time) проверка # \\\ I pair[0] == ‘(’
									assert(pair[1] == ')')                                                 # \\\    #assert(pair[1] == ‘)’)
									if text[i-1:i] == ':' and text[i+1:i+3] == '(:':                       # \\\    I text[(i-1, i+1..+2)] == (‘:’, ‘(:’)
										assert(text[i] == ')')                                             # \\\       #assert(text[i] == ‘)’)
										i += 2 # пропускаем, чтобы смайлы :)(: не [ломали/]портили баланс
										continue
								raise IntException(i)
							else:
								i += 1
					self.view.show_popup("Balance is observed")
				except IntException as i:
					self.view.sel().clear()
					self.view.sel().add(sublime.Region(i.i, i.i+1))
					self.view.show_at_center(i.i)

			def commit_current_file():
				os.chdir(os.path.dirname(self.view.file_name()))
				os.system("git difftool --no-prompt")
				if sublime.ok_cancel_dialog(""):
					os.system('git commit -a --allow-empty-message -m "" & pause')
					os.system('git push & pause')

			def show_tablets(): # показывает сколько пустых ячеечек в упаковке таблеток Азалептина, который мне прописал психиатр, должно остаться на данный момент [а то я часто забываю, принимал уже таблетку или ещё нет]
				t = -1 + (datetime.date.today() - datetime.date(2024, 5, 2)).days * 3
				self.view.show_popup('После приёма должно остаться' +
				               '<br />пустых ячеек:' +
				               '<br />' +
				               '<br />Утром:         ' + str( t      % 10).rstrip('0').rstrip('.') +
				               '<br />В обед:         ' + str((t + 1) % 10).rstrip('0').rstrip('.') +
				               '<br />Перед сном: ' + str((t + 2) % 10).rstrip('0').rstrip('.'))

			actions = [
					#('Редактировать секретное сообщение', edit_secret_message),
					('pqmarkup:to_html', pq_to_html),
					('pqmarkup:to_habr_html', lambda: pq_to_html(True)),
				#	('pqmarkup:to_habr_html_comment', lambda: pq_to_html(True, True)),
					('pqmarkup:to_bbcode', lambda: pq_to_html(True, to_bbcode = True)),
				#	('pqmarkup:remove_[[[[comments]]]]_and_copy_to_clipboard', pq_remove_deep_comments_and_copy_to_clipboard),
					('pqmarkup:remove_[[[comments]]]_and_copy_to_clipboard', pq_remove_comments_and_copy_to_clipboard),
					('compiler.su markup to pq', compilersu_markup_to_pq),
					('Prev versions', prev_versions),
					('Файлы этого дня', folder_of_that_day),
					(box_drawing_chars_1, lambda: box_drawing_chars(box_drawing_chars_1)),
					(box_drawing_chars_2, lambda: box_drawing_chars(box_drawing_chars_2)),
					('Найти символ не представимый в кодировке cp1251', find_first_non1251_char),
					('Сравнить и показать, чем отличаются кодировки latin-1 и ascii', find_differences_between_encodings),
					('Оставить выделенными все глухие согласные буквы',  lambda: remain_in_selection_this_characters("СТПКХЧШЩЦФ")),
					('Оставить выделенными все звонкие согласные буквы', lambda: remain_in_selection_this_characters("МНГЛВРЗБЙЖД")),
					('Оставить выделенными все гласные буквы',           lambda: remain_in_selection_this_characters("АЕЁИОУЮЭЮЯ")),
					('Оставить выделенными все согласные буквы',         lambda: remain_in_selection_this_characters("СТПКХЧШЩЦФМНГЛВРЗБЙЖДЬЪ")),
					('Reverse order of selected text \ Обратить порядок букв в выделенном тексте', reverse_order),
					('split_selection_into_characters \ [Разбить/]разделить выделение на символы', split_selection_into_characters),
					('Beautify table \ Сделать таблицу красивой', beautify_table),
					('Count total cost/expenses \ Подсчитать сумму расходов', count_total_expenses),
					('Balance check of all paired spec symbols/characters ‘’(){}[]', check_balance_of_all_char_pairs),
				#	('Remove all balanced pairs of spec symbols ‘’(){}[]', self.remove_all_balanced_chars_pairs),
					('Commit\‘Отправить [коммит]’ current\текущий file\файл', commit_current_file),
					('Edit selection in separate tab/buffer \ Редактировать/‘хочу работать’ с текущим выделением в отдельной вкладке', self.edit_selection_in_separate_buffer),
					('‘Убрать/скрыть курсор’\‘Hide cursor’', self.hide_cursor),
					('Таблетки\Tablets', show_tablets),
				]
			# Условные\Conditional actions
			clipbrd = sublime.get_clipboard()
			if clipbrd[:1] == '"' and clipbrd[-1:] == '"' and clipbrd[2:4] == ":\\":
				def rename():
					if khrono_log_ready():
						def on_done(newname):
							os.rename(clipbrd[1:-1], newname)
							khrono_log("-'‘" + clipbrd[1:-1] + "’'\n+'‘" + newname + "’'")
						sublime.active_window().show_input_panel("RENAME", clipbrd[1:-1], on_done, None, None)
				#actions.insert(0, ("FileOps:RENAME", rename))

			sublime.active_window().show_quick_panel([it[0] for it in actions], lambda i: (self.view.run_command("f4", {"redirect_method": actions[i][1].__name__}) if inspect.ismethod(actions[i][1]) else actions[i][1]()) if i != -1 else None)
			#self.view.show_popup_menu([it[0] for it in actions], lambda i: actions[i][1]() if i != -1 else None)
			if result == '':
				return

		self.view.run_command("insert_snippet", { "contents": result } )

class ctrl_f5_command(sublime_plugin.TextCommand):
	def run(self, edit):
		self.view.run_command("save")
		cwd = os.getcwd()
		os.chdir(os.path.dirname(self.view.file_name()))
		if os.path.isfile(self.view.file_name() + ".cmd"):
			os.system('"' + self.view.file_name() + ".cmd" + '"')
		elif self.view.file_name().endswith(".py"):
			if "codechef.com" in self.view.file_name(): # данный py-файл из сборника задач сайта codechef.com
				os.chdir(os.path.dirname(self.view.file_name()))
				fname = os.path.basename(self.view.file_name())
				os.system('python "' + fname + '" < "' + fname + '.in" > out.txt & pause')
				outfile = open("out.txt", "rt")
				if soft_assert(outfile.read(), open(self.view.file_name() + ".out").read()):
					sublime.message_dialog("Result is correct!")
				outfile.close()
				os.remove("out.txt")
			else:
				exec_command('pythonw "' + self.view.file_name() + '"')
		os.chdir(cwd)

class ctrl_f10_command(sublime_plugin.TextCommand):
	def run(self, edit):
		sel = self.view.substr(self.view.sel()[0])
		self.view.run_command("insert_snippet", { "contents": sel + ' ' + (chr(int(sel, 16)) if len(sel)>1 else str(ord(sel)) + '=' + hex(ord(sel))) } )

class ctrl_f11_command(sublime_plugin.TextCommand):
	def run(self, edit):
		selected_text = self.view.substr(self.view.sel()[0])
		self.view.run_command("insert_snippet", { "contents": re.sub('.', R'_\b\g<0>', selected_text) } )

class shift_ctrl_f11_command(sublime_plugin.TextCommand):
	def run(self, edit):
		selected_text = self.view.substr(self.view.sel()[0])
		self.view.run_command("insert_snippet", { "contents": selected_text.replace('_\b', '') } )

class insert_pq_(sublime_plugin.TextCommand):
	def run(self, edit, prefix = '', postfix = ''):
	  # selected_text = self.view.substr(self.view.sel()[0])
	   #self.view.run_command("insert_snippet", { "contents": "‘${0:$SELECTION}’" if selected_text == '' else "${0:‘$SELECTION’}" } )
	  # replace_selection_with(balance_pq_string(selected_text))
		for ri, rgn in enumerate(self.view.sel()):
			self.view.replace(edit, rgn, prefix + balance_pq_string(self.view.substr(rgn)) + postfix)
			#ri = self.view.sel().index(rgn) # отказался от этой идеи, так как это требует наличия A ADDitiONS в sublime.py
			rgn = self.view.sel()[ri] # обновляем/актуализируем значение rgn, так как после -‘пред’предыдущей команды изменяется регион данного выделения и rgn уже становится не актуально
		#	self.view.sel().subtract(sublime.Region(rgn.a, rgn.a+1)) # убираем первый символ выделения
		#	self.view.sel().subtract(sublime.Region(rgn.b-1, rgn.b)) # убираем последний символ выделения
		##### почему-то так не работает :(): поэтому пришлось сделать по-другому: (:так даже понятнее получилось:)
			self.view.sel().subtract(rgn) ; self.view.sel().add(sublime.Region(rgn.a+1+len(prefix), rgn.b-1-len(postfix))) # странно, что это вообще работает (::) потому что вот так вот:
		   #with (self.view.sel()): subtract(rgn) ; add(sublime.Region(rgn.a+1, rgn.b-1)) не работает

class pq_format_delta(sublime_plugin.TextCommand):
	def run(self, edit, char):
	  # selected_text = self.view.substr(self.view.sel()[0])
	   #self.view.run_command("insert_snippet", { "contents": char+"'‘${0:$SELECTION}’'" } )
	  # replace_selection_with(char + "'" + balance_pq_string(selected_text) + "'")
		a = self.view.sel()[0].begin()
		self.view.run_command("insert_pq", {"prefix": char + "'", "postfix": "'"})
		self.view.sel().clear() # чтобы не делать отдельное сочетание клавиш для pq_format_delta(char=""), то есть чтобы заключить строку в '‘такие’' кавычки {а это очень редко используемая операция} достаточно было нажать ctrl+= или ctrl+- и затем backspace или delete
		self.view.sel().add(sublime.Region(a, a+1)) # :( хочу писать так: add(`[a, a+1]) ):

class pq_format_delta_with_timestamp(sublime_plugin.TextCommand):
	def run(self, edit, char):
	   #selected_text = self.view.substr(self.view.sel()[0])
	   #self.view.run_command("insert_snippet", { "contents": char if selected_text == ''+'+(1476746919±?)‘ and 0’' and 0 else "${0:"+char+"("+str(int(time.time()))+"±X)"+"'‘$SELECTION’'}" } )
		self.view.run_command("insert_pq", {"prefix": char+"("+str(int(time.time()))+"±X)'", "postfix": "'"})

class pq_format_superdelta(sublime_plugin.TextCommand):
	def run(self, edit, char):
	   #selected_text = self.view.substr(self.view.sel()[0])
	   #self.view.run_command("insert_snippet", { "contents": char+{'+':'(ОК)','-':'(К)'}[char]+"'‘${0:$SELECTION}’'" } )
		self.view.run_command("insert_pq", {"prefix": char+{'+':'(ОК)','-':'(К)'}[char] + "'", "postfix": "'"})


class sha3_ctrl_shift_i(sublime_plugin.TextCommand):
	def run(self, edit):
		sys.path.append(os.path.dirname(__file__))
		import CompactFIPS202

		def as_hex_str(bytearr):
			res = str(binascii.hexlify(bytearr), 'ascii').upper()
			return res[:len(res)//2] + '_' + res[len(res)//2:]

		selected_text = self.view.substr(self.view.sel()[0])

		new_text = selected_text
		dict = {}
		for en in ['utf-8']:#, '['*0+'UTF', 'cyrillic', 'maccyrillic', 'cyrillic-asian', 'koi8_u', 'IBM855', 'IBM866', 'windows-1251', 'koi8_r', 'utf8']: # TODO: ADD 'ruscii[=ibm1125|cp866u]'
			text_as_binary = selected_text.encode(en, errors = 'ignore')
			hash =(as_hex_str(CompactFIPS202.SHA3_512(text_as_binary)) +
			"\n" + as_hex_str(CompactFIPS202.Keccak(576, 1024, text_as_binary, 0x01, 512//8)) +
			"\n" + as_hex_str(CompactFIPS202.SHA3_512(text_as_binary + text_as_binary[::-1])))
		#	if len(selected_text) < len(hash):
		#		hash = hash[:len(selected_text)]
			if hash not in dict:
				dict[hash] = []
			dict[hash].append(en)

		for hash, encodings_array in dict.items():
			new_text = (new_text + '\n' + str(encodings_array) + '\n' + hash)

		self.view.run_command("insert_snippet", { "contents": new_text} )


date_time_formats = []
# Prepare date_time_formats
for format in ['%Y.%m.%d, %H:%M:%S',   # 2016.05.22, 10:22:47 — My previous standard timestamp by pressing F5 in SublimeText
			   '%Y-%m-%d %H:%M:%S',    # 2017-11-11 22:17:02 — My actual standard timestamp by pressing F5 in SublimeText [based on ISO 8601]
			   '%Y.%m.%d %H:%M:%S',    # 2017.11.11 22:17:02 — My previous standard timestamp by pressing F5 in SublimeText
			   '%Y.%m.%d %H:%M:%S',    # 2016.05.22 10:22:47 — My previous standard timestamp by pressing F5 in SublimeText
			   '%Y-%m-%d %H:%M',       # 2016-05-22 10:22 - for manually added datetime
			   '%Y.%m.%d %H:%M',       # 2016.05.22 10:22 - old
			   '%H:%M %d.%m.%Y',       # 8:23 10.05.2016 — Notepad.exe on Windows
			   '%m/%d/%Y %I:%M:%S %p', # 3/23/2016 9:32:25 AM — WPS (ex. Kingsoft) office for Android
			   '%d.%m.%Y %H:%M:%S']:   # 07.06.2016 14:16:04 — WordPad.exe on Windows
	date_time_formats.append((format,
	                          re.compile(re.sub(r'%[HIMSmd]', r'\d\d?',
										                          	    format.replace('.', r'\.')
										                          	          .replace('%Y', r'\d\d\d\d')
										                          	          .replace('%p', '[AP]M'))
	                                                                                                    + '$')))

def precheck_date_time(s, pos, end): # функция предварительной проверки для ускорения расчётов
	if pos + 1 >= end:#len(s):
		return False
	return s[pos].isdigit() or (
	    						 	s[pos] == '(' # balancing )
	    						and
	    							s[pos+1].isdigit()
	    					   )

def parse_date_time(str, precheck_already_made = False):
	if precheck_already_made:
		assert(precheck_date_time(str, 0, len(str)))
	else:
		if not precheck_date_time(str, 0, len(str)):
			return

	r = re.match(r'\((\d{9,10})±[?хxХX]\)$', str)
	if r:
		return int(r.group(1))

	for format, regexp in date_time_formats:
		if regexp.match(str):
			if str[-1] == "\n": # почему-то re.match("word$","word\n") возвращает match, поэтому исключаем явно такую ситуацию
				return
			return calendar.timegm(time.strptime(str, format))

def dropbox_dir():
	# Идём по списку открытых файлов, чтобы найти каталог Dropbox
	for v in sublime.active_window().views():
		if v.file_name():
			i = v.file_name().find("Dropbox\\") # \\ A i = v.file_name()?.find("Dropbox\\") ?? -1
			if i != -1:
				return v.file_name()[:i+8]
			if v.file_name().startswith("B:\\"):
				return "B:\\"

def find_ending_bracket(str, i, Lbr = '‘', rbR = '’', error = 'Unpaired `#`'):
	assert(str[i] == Lbr)
	nesting_level = 0
	while True:
		ch = str[i]
		if ch == Lbr:
			nesting_level += 1
		elif ch == rbR:
			nesting_level -= 1
			if nesting_level == 0:
				return i
		i += 1
		if i == len(str):
			if error:
				raise Exception(error.replace('#', Lbr))
			else:
				return None

def find_ending_sq_bracket(str, i):
	return find_ending_bracket(str, i, '[', ']')

class last_log_ctrl_shift_l(sublime_plugin.TextCommand):
	def run(self, edit):
		class TaskInfo:
			def __init__(self, priotity_level, desc_string, cstart, cend, fcontents, fname, date_time):
				sassert(desc_string, fcontents[cstart:cend])
				self.priotity_level = priotity_level
				self.desc_string = desc_string
				self.region = sublime.Region(cstart, cend)
				self.fname = fname
				self.date_time = date_time

		class FileIterator:
			def __init__(self, fname, fcontents):
				self.fname = fname
				self.fcontents = fcontents
				self.i = len(fcontents)
				self.next()
			def next(self):
				self.date_time = None
				self.end_of_this_part_of_text = self.i
				if self.i == 0:
					return

				self.i -= 1
				while self.i >= 0: # self.i = self.fcontents.rfind("\n", self.i - 1) DOES NOT WORK FOR SOME REASON... I've got it: rfind("\n", 0, self.i) should be used instead
					if self.fcontents[self.i] == "\n":
						break
					self.i -= 1

				if self.i == -1:
					return
				next_line_pos = self.i
				self.i -= 1
				while self.i > 0:
					if self.fcontents[self.i] == "\n":
						if self.fcontents[self.i - 1] == "\n" and precheck_date_time(self.fcontents, self.i + 1, next_line_pos):
							self.orig_date_time = self.fcontents[self.i + 1 : next_line_pos]
							self.date_time = parse_date_time(self.orig_date_time, precheck_already_made = True)
							if self.date_time != None:
								break
						next_line_pos = self.i
					self.i -= 1
			def log(self):
				content = self.fcontents[self.i + 1 : self.end_of_this_part_of_text]
				logr = '[./' + self.fname + ":‘" + self.orig_date_time + "’ " + format_time(self.date_time) + '] ' + \
						content.rstrip('\n') + "\n\n"
				tasks_list = []
				for found in re.finditer(R'\[-([!?]*)', content, re.DOTALL):
					# if found.group(2) != '-': #исправление\fix для\for `[[[-‘в API/формате’]]]`
					#	continue

					# Чуть не ошибся {проверял то [поведение] как было раньше, чтобы написать commit message} и не закоммитил:
					# end_sqb_pos = find_ending_bracket(content, found.start(0), '[', ']')
					# if end_sqb_pos == None:
					# Очевидно, должна быть ошибка компиляции: проверка на None переменной, которая в принципе не может быть None
					end_sqb_pos = find_ending_bracket(content, found.start(0), '[', ']', None)
					if end_sqb_pos == None:
						print('ERROR in ' + self.fname + ' at position ' + str(self.i + 1 + found.start(0)))
						continue
					if content[end_sqb_pos-1] != '-':
						continue
					lvs = found.group(1)
					lv = len(lvs)
					if lv != 0 and lvs[0] != "!": # [-для чего это я делал?-]
						assert(lvs[0] == "?")
						lv = -lv
					if (content[found.start(0)+2:found.start(0)+3].isdigit() # заменил +4 на +3 так как должна работать запись вида [-6 15:10 D738 научно-практический семинар для аспирантов набора 2017-] — речь про 6 число текущего месяца
							or lvs.startswith("!")): # O‘ОТОБРАЖАТЬ ТОЛЬКО ВАЖНЫЕ[‘с символом ! вначале’] ЗАДАЧИ’ [[[О‘’ — ОПЦИЯ\OPTION]]]
						tasks_list.append(TaskInfo(lv, content[found.start(0):end_sqb_pos+1], self.i + 1 + found.start(0), self.i + 1 + end_sqb_pos+1, self.fcontents, self.fname, self.date_time))
				return logr, tasks_list

		# Обходим все однобуквенные файлы в каталоге Dropbox
		files = []
		DropboxDir = dropbox_dir()
		for fname in os.listdir(DropboxDir):
			#if len(fname) == 5 and fname.endswith(".txt") or fname == "to_alla.txt":
			if fname.endswith(".txt"):
				try:
					fcontents = open(DropboxDir + fname, "rt", encoding = "utf-8-sig").read()
				except UnicodeDecodeError:
					fcontents = open(DropboxDir + fname, "rt", encoding = "cp1251").read()
				files.append(FileIterator(fname, fcontents))

		# Собираем последние 300 записей, сортированные по дате (наиболее поздние)
		log = ""
		tasks_list = []
		for n in range(300):
			max_date_time = 0
			max_fi = None
			for fi in files: # Ищем запись с наибольшей датой
				if fi.date_time != None and fi.date_time > max_date_time:
					max_date_time = fi.date_time
					max_fi = fi
			# Добавляем её в log
			logr, tasks_listr = max_fi.log()
			log += logr
			tasks_list += tasks_listr
			# "Удаляем" её
			max_fi.next()

		metadata = {} #метаданные, соответствующие данному содержимому\buffer
		class Metadata:
			def __init__(self, task):
				self.fname = task.fname
				self.str = task.desc_string
				self.region = task.region

		# Календарь
		CALENDAR_WEAKS = 6 # SETTING
		calendarstr = " Пн  Вт  Ср  Чт  Пт  Сб  Вс\n"
		calendar_gr = ["┌───┬───┬───┬───┬───┬───┬───┐",
		               "│   │   │   │   │   │   │   │"]
		for i in range(CALENDAR_WEAKS-1):
			calendar_gr += ["├───┼───┼───┼───┼───┼───┼───┤",
			                "│   │   │   │   │   │   │   │"]
		calendar_gr+= ["└───┴───┴───┴───┴───┴───┴───┘"]
		days = {}
		new_tasks_list = []
		now = datetime.date.today()
		for t in tasks_list: # Обходим/фильтруем задачи
			taskstr = t.desc_string
			tasktm = time.gmtime(t.date_time)
			m = re.match(
			   #sho:‘[’-00?(.00(.0000)?)?‘ ’
			   #min:‘[’-(__0_______[.__00_____[.__2_0_1_6]]___[..]__‘ ’)|(___0:00__‘ ’)                      # сравните: ‘ ’‘]’
			   #max:‘[’-(__99______[.__99_____[.__2_0_1_7]]___[..]__‘ ’)|(__23:59__‘ ’)                      # сравните: ' '']'
	            R"""\[-(?:
	                     (\d\d?) #1
				                (?:\.(\d\d) #2
				                           (?:\.(\d\d\d\d))?)? #3
				                                             (\.\.)?\ |#4
				                                                       (\d\d?\:\d\d\ )? #5
				                                                                       )""", taskstr, re.VERBOSE)
			if m and (m.group(1) or m.group(5)):
				# view().show_popup(taskstr) # чтобы при исключении показался popup с данной задачей
				if m.group(1):
					year= int(m.group(3)) if m.group(3) else tasktm.tm_year
					mon = int(m.group(2)) if m.group(2) else tasktm.tm_mon
					day = int(m.group(1))
					t.desc_string = t.desc_string[m.end(0):-2]
					d = datetime.date(year, mon, day)
					if m.group(4) == '..':
						if d < now:
							d = now
				else:
					d = datetime.date.fromtimestamp(calendar.timegm(tasktm))
					assert(m.group(5))
					t.desc_string = t.desc_string[m.start(5):-2]
				if d < now: # пропускаем дни перед сегодняшним (вчера и ранее) {почему написал так, а не `if d >= now: \n days[d] = days.get(d, []) + [t]`: потому что так закомментировать будет проще: один `\` (`\I d < now {continue}` — `\` перед `I` комментирует весь блок условия) вместо двух (`\\I d >= now\\{days[d] = days.get(d, []) + [t]}`)}
					continue
				days[d] = days.get(d, []) + [t]
				continue
			new_tasks_list.append(t)
		tasks_list = new_tasks_list
		# Рисуем календарь
		startd = now + datetime.timedelta(days = -time.localtime().tm_wday) # находим начало недели
		def overwrite_calendar_gr(y, x, s):
			calendar_gr[y] = calendar_gr[y][:x] + s + calendar_gr[y][x+len(s):]
		month_strs = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
		for i in range(7*CALENDAR_WEAKS):
			d = startd + datetime.timedelta(days = i)
			if d == now:
				overwrite_calendar_gr(i//7*2  , i%7*4, "╔═══╗")
				overwrite_calendar_gr(i//7*2+1, i%7*4, "║   ║")
				overwrite_calendar_gr(i//7*2+2, i%7*4, "╚═══╝")
			marker = ''
			if d in days:
				marker = '▒'
			overwrite_calendar_gr(i//7*2+1, i%7*4 + 1 + (1 if d.day < 10 else 0), str(d.day) + marker)
		for w in range(CALENDAR_WEAKS):
			d = startd + datetime.timedelta(weeks = w)
			calendar_gr[w*2+1] += " " + month_strs[d.month-1] + (" → " + month_strs[d.month % len(month_strs)] if (d + datetime.timedelta(days = 6)).month != d.month else "")
		calendarstr += "\n".join(calendar_gr) + "\n"
		# Добавляем дела, отмеченные на календаре
		for d, tasks in sorted(days.items(), key = lambda x: x[0]):
			if d >= startd + datetime.timedelta(weeks = CALENDAR_WEAKS): # задача ‘не отмечена символом `▒`’/отсутствует на календаре (не поместилась на календарь) — пропускаем
				break
			# print(format(2, "02")) #### WTF?????? Uncommenting this line cause "TypeError: 'str' object is not callable"
			if d == now:
				calendarstr += """
╔═══╗
║{:2}░║
╚═══╝""".format(d.day)
			else:
				calendarstr += """
┌───┐
│{:2}░│
└───┘""".format(d.day)
			for task in sorted(tasks, key = lambda t: t.desc_string): # L(task) sorted(tasks, key' . -> .desc_string)
				metadata[calendarstr.count("\n")+1] = Metadata(task) # \\\ metadata[calendarstr.count("\n")+1] = T {fname = task.fname; str = task.desc_string}
				calendarstr += "\n" + re.sub(R'^\d\d:\d\d ', R'\g<0>— ', task.desc_string)
			calendarstr += "\n"

		# Собираем все задачи {вынесено сюда, чтобы добавить метадату (для того, чтобы работал переход по F12 для задач, имеющих одинаковое текстовое описание {но разный смысл, который зависит от контекста — того места, где размещена задача})}
		tasks_str = "\n\nЗАДАЧИ:\n\n"
		current_task_line = calendarstr.count("\n") + tasks_str.count("\n")
		for t in sorted(tasks_list, key=lambda t:t.priotity_level, reverse=True):
			metadata[current_task_line] = Metadata(t)
			current_task_line += 1 + t.desc_string.count("\n")
			tasks_str += t.desc_string + "[./" + t.fname + "]\n"
		if not tasks_list:
			tasks_str += "[пусто]\n"

		# Открываем новый буфер/окно с результатами поиска
		newfile = sublime.active_window().new_file()
		newfile.set_scratch(True)
		newfile.insert(edit, 0, calendarstr + tasks_str
			+ "\n\nПОСЛЕДНИЕ ЗАПИСИ:\n\n" + (
			"[скрыто {O‘ПОКАЗЫВАТЬ ПОСЛЕДНИЕ ЗАПИСИ’}]" if
			0
			#+ 1 # O‘ПОКАЗЫВАТЬ\скрыть ПОСЛЕДНИЕ ЗАПИСИ’ [[[тег О[пция] работает таким образом, что строка с этим тегом комментируется при отключении опции, но если строка закомментирована, то опция отключена по умолчанию, то есть умолчания всегда хардкодятся]]]
			else log)
			)
		newfile.set_read_only(True)
		newfile.set_name("ДЕЛА") # ЗАДАЧИ ГРАФИК РАСПИСАНИЕ MYL TASKS_LIST SCHEDULE

		# Так как настоящих метаданных\metadata [как я понял] в SublimeText нет/‘не поддерживается’ {это[http://docs.sublimetext.info/en/latest/reference/metadata.html][-1] что-то другое совсем, а не то, что там написано >[-1]:‘Metadata are parameters that can be assigned to certain text sections using scope selectors.’},
		# то придётся эмулировать метаданные\metadata вручную:
		global metadatas
		if "metadatas" not in globals():
			metadatas = {}
		metadatas[newfile.buffer_id()] = metadata

class search_in_records(sublime_plugin.TextCommand):
	def run(self, edit, word):
		if word == "":
			return

		DropboxDir = dropbox_dir()

		# Обходим все однобуквенные файлы в каталоге Dropbox
		log = ""
		files = []
		for fname in os.listdir(DropboxDir):
			if """len(fname) == 5""" and fname.endswith(".txt"): #or fname == "to_alla.txt": #один из минусов `:` в конце строки для `if` в том, что при таком комментировании приходится добавлять `:` перед `#`
				try:
					fcontents = open(DropboxDir + fname, "rt", encoding = "utf-8-sig").read()
				except UnicodeDecodeError:
					fcontents = open(DropboxDir + fname, "rt", encoding = "cp1251").read()

				# Класс для разбивки содержимого файла на отдельные записи (разделителем является дата/время записи)
				class Record:
					def __init__(self):
						self.pos = 0
						self.next_line_pos = 0
					def next(self):
						self.pos = self.next_line_pos
						while self.pos < len(fcontents):
							self.next_line_pos = fcontents.find("\n", self.pos)
							if self.next_line_pos == -1:
								break
							self.date_time = fcontents[self.pos : self.next_line_pos]
							if parse_date_time(self.date_time):
								return True
							self.pos = self.next_line_pos + 1
						return False

				def process_fcontents(start, end):
					nonlocal log
					if fcontents[start:end].casefold().find(word) != -1:
						log += '[./' + fname + ':‘' + fcontents[prev.pos:prev.next_line_pos] + '’] ' + fcontents[start:end].rstrip('\n') + "\n\n"
				# Ищем word в файле fname [с содержимым fcontents]
				rec = Record()
				rec.next()
				prev = copy.copy(rec)
				while rec.next():
			# \\F process_fcontents(Range range) \\ функция видна на том уровне, на котором объявлена
					process_fcontents(prev.next_line_pos, rec.pos) # \\ (prev.next_line_pos..rec.pos)
					prev = copy.copy(rec)
				process_fcontents(prev.next_line_pos, 1000000000)

		# Открываем новый буфер/окно с результатами поиска
		newfile = sublime.active_window().new_file()
		newfile.set_scratch(True)
		newfile.insert(edit, 0, log)
		newfile.set_read_only(True)

class search_in_records_ctrl_alt_shift_f(sublime_plugin.TextCommand):
	def run(self, edit):
		def on_done(word):
			sublime.active_window().active_view().run_command("search_in_records", {"word": word.casefold()})

		sublime.active_window().show_input_panel("", "", on_done, None, None)

def find_ending_pair_quote(self, i): # ищет окончание ‘строки’
	assert(self.view.substr(i) == "‘")
	nesting_level = 0
	while True:
		ch = self.view.substr(i)
		if ch == "‘":
			nesting_level += 1
		elif ch == "’":
			nesting_level -= 1
			if nesting_level == 0:
				return i
		i += 1
		if i == self.view.size():
			raise 'Unpaired quote'

def find_beginning_pair_quote(str, i): # ищет начало ‘строки’
	assert(str[i] == "’")
	nesting_level = 0
	while True:
		ch = str[i]
		if ch == "‘":
			nesting_level -= 1
			if nesting_level == 0:
				return i
		elif ch == "’":
			nesting_level += 1
		if i == 0:
			raise 'Unpaired quote'
		i -= 1

target_view = None
target_text = ""
target_region = None
class LoadListener(sublime_plugin.EventListener): # https://forum.sublimetext.com/t/view-object-returned-by-window-open-file-solved/3461
	def on_load_async(self, view): # не знаю почему, но просто on_load не работает — не прокручивает до нужного места [поэтому on_load_async, а не on_load]
		if view == target_view:
			self.scroll_to_text(view)
	@staticmethod
	def scroll_to_text(view):
		global target_view, target_text, target_region
		if target_region:
			r = target_region
		elif target_text != "":
			r = sublime.Region(-1)
			while True:
				r = view.find(target_text, r.a+1, sublime.LITERAL)
				if r == sublime.Region(-1):
					break
				if view.substr(sublime.Region(r.a-2, r.a)) == ":‘": # ’
					continue # пропускаем все ссылки на файлы (:так проще {и это автоматически работает также для ссылок [:‘...’]}:), иначе не будут работать ссылки внутри файла (например: `[./этот_файл:‘текст’] ... текст` нажатие по ссылке выделит первый `текст`, а должно выделить второй)
				break
		else:
			return
		#r = sublime.Region(r.begin()) # если не хочется выделять весь текст задачи, тогда можно просто раскомментировать эту строку
		view.sel().clear()
		view.sel().add(r)
		view.show_at_center(r)
		target_view = None
		target_text = ""
		target_region = None

#+(1476747227±?)'‘
def find_matching_paired_quotes(region):
	return find_matching_brackets(region, '‘', '’')

def find_matching_cu_brackets(region):
	return find_matching_brackets(region, '(', ')')

def find_matching_sq_brackets(region):
	return find_matching_brackets(region, '[', ']')

def find_matching_brackets(region, Lbr, rbR, how_far = 2000):
	left, right = region.begin(), region.end()
	if left == right: # фикс для первого вызова (это условие выполняется только при пустом выделении = при первом вызове), чтобы можно было установить курсор перед `[` или после `]`
		if view().substr(left) == Lbr:
			left += 1
			right += 1
		elif view().substr(left-1) == rbR:
			left -= 1
			right -= 1
	if left == 0 or right == view().size():
		return None

	level = 0
	while True:
		left -= 1

		ch = view().substr(left)
		if ch == rbR:
			level += 1
		elif ch == Lbr:
			if level == 0:
				break
			level -= 1

		if left == 0 or  left < region.begin()-how_far:
			return None

	while True:
		right += 1

		ch = view().substr(right-1)
		if ch == Lbr:
			level += 1
		elif ch == rbR:
			if level == 0:
				break
			level -= 1

		if right == view().size() or  right > region.end()+how_far:
			return None

	return sublime.Region(left, right)
#’'

class f12_goto_definition_command(sublime_plugin.TextCommand):
	def run(self, edit):
		def open_dropbox_file_and_go_to_text(file_name, text, region = None):
			global target_view, target_text, target_region
			fname = None
			for dir in ([os.path.dirname(self.view.file_name())] if self.view.file_name() else []) + [os.path.dirname(dropbox_dir()), R"C:\cloud.mail.ru"]: # try dirs
				if os.path.isfile(dir +"/"+ file_name):
					fname = dir +"/"+ file_name
					break
			if fname == None:
				sublime.error_message('File '+file_name+' not found')
				return
			target_view = sublime.active_window().open_file(fname) # self.view.file_name() == None для файла ДЕЛА [ну а также для только что созданных несохранённых файлов]
			target_text = text
			target_region = region
			if not target_view.is_loading():
				LoadListener.scroll_to_text(target_view)

		if self.view.is_read_only(): # Если находимся в файле ДЕЛА, то ориентируемся просто по metadata
			assert(self.view.is_scratch())

			sel = self.view.sel()[0].begin()
			"""# Ищем строку под курсором во всех открытых файлах
			str_to_find = self.view.substr(self.view.line(sel))
			str_to_find += "-]" # чтобы не находились уже выполненные задачи, например: [+8.10.. Сходить на Луговая_26Б_ст2 за патроном-переходником для перфоратора (а также за буром 8мм)+]
			for w in sublime.windows(): # \\\ L(.) sublime.windows
				for view in w.views():    # \\\    L(view) .views
					if view.is_read_only(): # пропускаем ДЕЛА
						assert(view.is_scratch())
						continue
					r = view.find(str_to_find, 0, sublime.LITERAL)
					if r:
						#r = sublime.Region(r.begin()) # если не хочется выделять всю строку, тогда можно просто раскомментировать эту строку
						view.sel().clear()
						view.sel().add(r)
						view.show_at_center(r)
						w.focus_view(view)
						break # fix this!? \\\ L(.).break"""
			metadata = metadatas[self.view.buffer_id()]
			metadat = metadata.get(self.view.rowcol(sel)[0], None)
			if metadat:
				open_dropbox_file_and_go_to_text(metadat.fname, metadat.str, metadat.region)
				return # должно быть именно на этом уровне отступа! иначе не работают ссылки в сообщениях в блоке ‘ПОСЛЕДНИЕ ЗАПИСИ:’ в файле ДЕЛА

		#-(1476746702±?)'‘def find_matching_sq_brackets(region):...’'

		sq_brackets = self.view.sel()[0]
		for l in range(5):
			sq_brackets = find_matching_sq_brackets(sq_brackets)
			if sq_brackets == None:
				break
			if (self.view.substr(sublime.Region(sq_brackets.begin(), sq_brackets.begin()+2)) == "[-" and
			    self.view.substr(sublime.Region(sq_brackets.end()-2, sq_brackets.end()  +3)) == "-][./"): # this is task\это задача (обработка) \\ end() + -2..<3
				fname_brackets = find_matching_sq_brackets(sublime.Region(sq_brackets.end() + 1))
				if fname_brackets != None:
					open_dropbox_file_and_go_to_text(self.view.substr(fname_brackets)[1:-1], self.view.substr(sq_brackets))
				return
			if self.view.substr(sublime.Region(sq_brackets.begin()+1, sq_brackets.begin()+3)) in ("./", ":‘"): # this is file reference or task [[[’]]]
				if self.view.substr(sublime.Region(sq_brackets.begin()-2, sq_brackets.begin())) == "-]": # this is task\это задача (переход в обработку)
					sq_brackets = sublime.Region(sq_brackets.begin()-1)
					continue
				# This is file reference\Это ссылка на файл/‘место в файле’
				filename = self.view.substr(sq_brackets)[1:-1] # balancing ‘
				if filename[-1] == '’':
					begq = find_beginning_pair_quote(filename, len(filename)-1)
					if filename[begq-1] == ' ':
						filename = filename[:begq-1]#.rstrip(' ')
				file_ref = filename.split(':', 1)
				target_text = ""
				if len(file_ref) > 1:
					if file_ref[1].isdigit():
						sublime.active_window().open_file(dropbox_dir() +"/"+ filename, sublime.ENCODED_POSITION)
						# view.run_command("goto_line", {"line": file_ref[1]})
						break
					elif file_ref[1][0] == "‘":
						startqpos = sq_brackets.begin() + len(file_ref[0]) + 2
						target_text = self.view.substr(sublime.Region(startqpos+1, find_ending_pair_quote(self, startqpos)))
					else:
						sublime.message_dialog('Wrong format (should be [./fname:DIGITS] or [./fname:‘TEXT’] or [:‘TEXT’])')
						return
					#	target_text = ""
					filename = file_ref[0]
				open_dropbox_file_and_go_to_text(filename if filename else os.path.basename(self.view.file_name()), target_text) # filename пустой в случае ссылки вида [:‘...’]
				return
			if self.view.substr(sublime.Region(sq_brackets.begin()+1, sq_brackets.begin()+1+4)) == "http": # this is web/external link
				link = self.view.substr(sq_brackets)[1:-1]
				link = link.split(' ', 1)[0]
				#\if link[-1] == '’':
				#	begq = find_beginning_pair_quote(link, len(link)-1)
				#	if link[begq-1] == ' ':
				#		link = link[:begq-1]#.rstrip(' ')
				webbrowser.open(link)
				return
			if self.view.substr(sublime.Region(sq_brackets.begin()+1, sq_brackets.begin()+2)) == '"': # this is absolute path (which is copied to clipboard in Windows after click on context menu item ‘Копировать как путь’)
				sublime.active_window().open_file(self.view.substr(sq_brackets)[2:-2])
				return

		# Check for Markdown links
		cu_brackets = find_matching_cu_brackets(self.view.sel()[0])
		if cu_brackets is not None:
			if self.view.substr(sublime.Region(cu_brackets.begin()+1, cu_brackets.begin()+1+4)) == "http":
				webbrowser.open(self.view.substr(cu_brackets)[1:-1].split(' ', 1)[0])

"""
		left = right = cursor_pos = self.view.sel()[0].begin()
		while True:
			ch = self.view.substr(right)
			if ch == ']':
				right += 1
				while self.view.substr(right) == ']':
					right += 1
				if self.view.substr(right) == '[' and self.view.substr(right+1) == '.': #]# для перехода к задаче {из списка задач по Ctrl+Shift+L} под курсором по нажатии F12
					right += 1 # skip\пропустить '['
					start = right
					right += 1 # skip\пропустить '.'
					while True:
						ch = self.view.substr(right)
						if ch == ']':
							fname = between = self.view.substr(sublime.Region(start, right))
							colon_pos = between.find(':')
							if colon_pos != -1:
								fname = between[:colon_pos] # balancing ‘
#								if between[colon_pos+1] == "’":
							sublime.active_window().open_file(dropbox_dir() +"/"+ fname)
							break
						if ch == "\0":
							break
						right += 1
				break
			if ch == "\0":
				break
			right += 1
"""

""" # from here [https://github.com/SublimeTextIssues/Core/issues/1461#issuecomment-257859379] (left for historical purpose)
def are_all_selections_equal(view):
    first_sel_str = view.substr(view.sel()[0])
    for i in range(1, len(view.sel())):
        if view.substr(view.sel()[i]) != first_sel_str:
            return None
    return first_sel_str

class cut_copy_one_command(sublime_plugin.TextCommand):
    def run(self, edit, command):
        str = are_all_selections_equal(self.view)
        self.view.run_command(command)
        if str:
            sublime.set_clipboard(str)

class cut_copy_one_listener(sublime_plugin.EventListener):
    def on_text_command(self, view, command_name, args):
        if command_name in ["cut", "copy"]:
            return ("cut_copy_one", {"command": command_name})
"""

class punto_switcher_emulator_command(sublime_plugin.TextCommand):
	def run(self, edit):
		for sel in self.view.sel():
			selected_text = self.view.substr(sel)

			if len(selected_text) == 0: # red:selection.empty \\ ред:выделение.пусто
				return

		   #\/ — эта версия разрушает ("вyfxfkt" после двойного нажатия Shift+Pause/Break не возвращается само в себя)
		   #OT = ("""qwertyuiop[]asdfghjkl;'\zxcvbnm,./№"""
		   #      """QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<>?@#$%^&""")
		   #TO = ("""йцукенгшщзхъфывапролджэ\ячсмитьбю.#"""
		   #      """ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБЮ,"№;%:?""")
		   #napravlinie_vybrano = False
		   #
		   #newtext = ""
		   #for c in selected_text:
		   #	if not napravlinie_vybrano:
		   #		if OT.find(c) != -1:
		   #			napravlinie_vybrano = True
		   #		elif TO.find(c) != -1:
		   #			OT, TO = TO, OT
		   #			napravlinie_vybrano = True
		   #	i = OT.find(c)
		   #	newtext += TO[i] if i != -1 else c
		   #/\ — эта версия разрушает ("вyfxfkt" после двойного нажатия Shift+Pause/Break не возвращается само в себя)
			OT = ("""qwertyuiop[]asdfghjkl;'\zxcvbnm,№`""",
			      """QWERTYUIOP{}ASDFGHJKL:"|ZXCVBNM<@#%&""",
			      """ЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭ/ЯЧСМИТЬБ"№%?""",
			      """йцукенгшщзхъфывапролджэ\ячсмитьб#ё""")
			TO = OT[-1] + OT[-2] + OT[-3] + OT[-4]
			OT = ''.join(OT)
			newtext = ""
			for c in selected_text:
				i = OT.find(c)
				newtext += TO[i] if i != -1 else c

			self.view.replace(edit, sel, newtext)

class OnLoad(sublime_plugin.EventListener):
	def on_load(self, view):
		#assert(view.name() == os.path.basename(view.file_name())) [-assert(v.path_name.file_name == v.file_name)-]
		if view.file_name().endswith(".txt") and os.path.basename(view.file_name()) in os.listdir(dropbox_dir()):
			view.run_command("set_file_type", {"syntax": "Packages/pqmarkup/pq.sublime-syntax"})

		if view.find("[\t ]$", 0) != sublime.Region(-1):
			if view.find("\0", 0, sublime.LITERAL) == sublime.Region(-1): # check for binary files
				sublime.error_message("Trailing white space detected!")
		else:
			view.settings().set('there_was_no_trailing_white_space', True)

	def on_pre_save(self, view):
		if view.settings().get('there_was_no_trailing_white_space', False):
			view.run_command("trim_trailing_white_space")


class left_right_command(sublime_plugin.TextCommand): # чтобы гулять клавишами влево/вправо по пробельным отступам было также удобно, как и по табулированным отступам
	def run(self, edit, dir, shift_pressed = False):
		view = self.view
		sels = list(view.sel())
		view.sel().clear()
		for sel in sels:
			# view.sel().subtract(sel)
			if sel.size() != 0 and not shift_pressed:
				p = sel.begin() if dir < 0 else sel.end()
				view.sel().add(sublime.Region(p))
			else:
				line = view.line(sel)
				new_pos = sel.b - line.a + dir
				indent_size = re.search('[^ ]', view.substr(line) + ".").start() # `+ "."` needed for empty lines [-A indent_size = line. {.find_not_of(‘ ’) ?: .len} \\= line.find_not_of@(‘ ’)-]
				if 0 <= new_pos < indent_size:
					tab_size = view.settings().get("tab_size")
					if dir > 0:
						new_pos -= dir
						new_pos -= new_pos % tab_size
						new_pos += tab_size
						if new_pos > indent_size: new_pos = indent_size # когда код выровнен неаккуратно, например: `   j = 1` при размере табуляции = 4
					else:
						new_pos -= new_pos % tab_size
				new_pos += line.a
				view.sel().add(sublime.Region(sel.a if shift_pressed else new_pos, new_pos))
		if len(view.sel()) == 1:
			view.show(view.sel()[0])

class extend_cursor_up_or_down(sublime_plugin.TextCommand): # чтобы расширять курсор клавишами Ctrl+Alt+Shift+Вверх/Вниз для создания дополнительной колонки [комментариев или колонки в текстовой таблице]
	def run(self, edit, down):
		view = self.view
		for sel in reversed(view.sel()):
			line = view.line(sel)
			print('			line = view.line(sel)')
			#print('			'+str(line)+' =         '+sel)
			if line.begin() == 0 and not down: # это первая строка и вверх расширять курсор уже некуда
				continue
			nline = view.line(line.end()+1 if down else line.begin()-1) # view.line() странно себя ведёт, когда позиция выходит за предел, но такое поведение меня устраивает
			print('nline'+repr(nline))
			print('nline.size()'+repr(nline.size()))
			if nline.size() < sel.b - line.begin():
#			   ^^^^^5^^^^^^   ^^8^^   ^^^^^7^^^^^^
				view.insert(edit, nline.end(), ' '*(sel.b - line.begin() - nline.size()))
			view.sel().add(sublime.Region(nline.begin() + sel.b - line.begin()))
			# [-TODO: Добавить поддержку символов табуляции.-]

#[-Сделать такой пункт в F4: Debug prints add, который автоматически будет добавлять/убирать отладочные print-ы.-]
#[-Вместо курсора замены: блокировка размера выделения на 1 символ. Выглядит так: С(-678)‘_’-]

class tab_command(sublime_plugin.TextCommand): # [-не написал что не так с обычным табом, поэтому пока команда будет отключена-]
	def run(self, edit):
		view = self.view
		for sel in reversed(view.sel()):
			view.insert(edit, sel.b, "\t" if view.settings().get("translate_tabs_to_spaces") else ' '*view.settings().get("tab_size"))

class new_find_all_under_command(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		if len(view.sel()) > 1:
			if not all(view.substr(s) == view.substr(view.sel()[0]) for s in view.sel()): # за исключением случая, когда все выделения содержат одинаковый текст — эта проверка для того, чтобы повторное нажатие Alt+F3 не приводило к ошибке
				return sublime.error_message("There should be only one selection, otherwise text to search may be taken from the first selection [of many selections] which [the first selection] is not visible!")
		selected_text = view.substr(view.sel()[0])
		if selected_text == "":
			return sublime.error_message("Selected text is empty!")
		view.sel().clear()
		view.sel().add_all(view.find_all(selected_text, sublime.LITERAL))

class slash_key_command(sublime_plugin.TextCommand):
	def run(self, edit):
		if self.view.sel()[0].size() == 0:
			self.view.insert(edit, self.view.sel()[0].b, '/')
		else:
			self.view.run_command("toggle_comment", { "block": False })
