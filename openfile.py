from tkinter import filedialog
import tkinter as tk
import os


def openfile():
    """

    :return: file helye, file neve
    """

    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    file_path = filedialog.askopenfilename(initialdir="/", title="Select A File", )
    return file_path, os.path.basename(file_path)
