# coding=UTF-8
# __author__ = '韵淡烽青'

from tkinter.filedialog import askopenfilename


from tkinter import *
from tkinter import ttk
try:
    from .epub import txt_to_epub
except:
    from epub import txt_to_epub


class EpubTranApp:
    def __init__(self, master):
        self.base_label = ttk.Label(master, text="TXT转EPUB", font="Times 16 bold")
        self.label = ttk.Label(master, text="请选择文件")
        self.base_label.grid(row=0, column=0, columnspan=6)
        self.label.grid(row=2, column=0, columnspan=6)
        self.filename = None

        ttk.Button(master, text='选择txt', command=self.select).grid(
            row=4, column=0)
        ttk.Button(master, text='转epub', command=self.transform).grid(
            row=4, column=1)

    def select(self):
        # self.label.config( text = 'Welcome to Oregon')
        self.filename = askopenfilename(initialdir="/User/zhangdesheng/Downloads/", filetypes=(
            ("Text file", "*.txt"),))
        self.label.config(text="已经选择:{}".format(self.filename))

    def transform(self):
        if not self.filename:
            self.label.config(text="你还没有选择文件...")
        else:
            try:
                epub_name = txt_to_epub(self.filename)
                self.label.config(text="转换成功,保存为:{}".format(epub_name))
            except BaseException as e:
                self.label.config(text="转换失败了,错误为:{}".format(e))


def main():
    root = Tk()
    def get_screen_size(window):  
        return window.winfo_screenwidth(),window.winfo_screenheight()  
  
    def get_window_size(window):  
        return window.winfo_reqwidth(),window.winfo_reqheight()  
      
    def center_window(root, width=300, height=240):  
        screenwidth = root.winfo_screenwidth()  
        screenheight = root.winfo_screenheight()  
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        root.geometry(size)
    center_window(root)
    root.maxsize(600, 400)  
    root.minsize(300, 240) 
    app = EpubTranApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
