import sublime_plugin


class NewFileWithUTF8BOM(sublime_plugin.EventListener):
    def on_new(self, view):
        view.set_encoding('UTF-8 with BOM')