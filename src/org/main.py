import os
import sys
import tkinter as tk
from tkinter import messagebox, filedialog

import numpy as np
from PIL import Image, ImageTk, ImageFont, ImageDraw, ImageOps

# TODO: Überlegen, ob diese Globalen Variablen hier richtig sind, oder in die ImageWizard-Class-init gehören

PATH_FONTS = r"./src/res/fnt"
PATH_FONT_DEFAULT = os.path.join(PATH_FONTS, "CONSOLAB.TTF")
PATHS_USERDIR = {"IMG": os.path.join(os.getenv("LOCALAPPDATA"), "ImageWizard", "Images"),
                 "TXT": os.path.join(os.getenv("LOCALAPPDATA"), "ImageWizard", "Text Files"),
                 "SETTINGS": os.path.join(os.getenv("LOCALAPPDATA"), "ImageWizard", "Settings"),
                 }
JSON_FILE = os.path.join(PATHS_USERDIR["SETTINGS"], "settings.json")
SCREEN_W = None
SCREEN_H = None
WIN_W = 1422
WIN_H = 800
GRID_ROWS = 8
GRID_COLS = 20
FRAME_SCALE = .95

class ImageWizard:
    """
    Class Image Wizard
    """

    def __init__(self, master):
        # images
        self.PATH_TO_IMAGE = None
        self.TK_IMAGE_PREVIEW = None
        self.IMG_PREVIEW = None
        self.TK_IMAGE_RESULT = None
        self.IMG_RESULT = None
        self.result_thumb = None
        self.preview_thumb = None

        self.ascii_text = ""

        # settings
        self.PIX_MAX_THUMB_H = None
        self.PIX_MAX_THUMB_W = None
        self.PIX_PX_SIZE = None
        self.ASC_PX_SIZE = None


        # define grid
        self.master = master
        self.master.bind("<Escape>", sys.exit)
        self.master.rowconfigure(tuple(range(GRID_ROWS - 1)), weight=1)
        self.master.columnconfigure(tuple(range(GRID_COLS - 1)), weight=1)

        self.widgets = {}

        # menu
        menu = tk.Menu(master)
        master.config(menu=menu)
        filemenu = tk.Menu(menu)
        menu.add_cascade(label="Datei", menu=filemenu)
        filemenu.add_command(label="Öffnen", command=self.open_file)
        filemenu.add_command(label="Bild speichern", command=self.save_file_as_img)
        filemenu.add_command(label="Txt speichern", command=self.save_file_as_txt)
        filemenu.add_separator()
        filemenu.add_command(label="ImageWizard beenden", command=sys.exit)

        settingsmenu = tk.Menu(menu)
        menu.add_cascade(label="Einstellungen", menu=settingsmenu)
        settingsmenu.add_command(label="Globale Einstellungen", command=self.open_global_settings)

        toolmenu = tk.Menu(menu)
        menu.add_cascade(label="Werkzeuge", menu=toolmenu)
        toolmenu.add_command(label="Batch ausführen", command=self.open_batch_dialog)

        # creating the GUI

        # frames
        frame_preview = tk.LabelFrame(master, text="ORIGINAL")
        frame_preview.place(relx=4 / 20, rely=.5 / 8, relwidth=7.5 / 20, relheight=5.5 / 8)
        self.widgets["frame_preview"] = frame_preview
        frame_result = tk.LabelFrame(master, text="RESULT")
        frame_result.place(relx=11.5 / 20, rely=.5 / 8, relwidth=7.5 / 20, relheight=5.5 / 8)
        self.widgets["frame_result"] = frame_result

        # frame_w, frame_h = frame_preview.winfo_width(), frame_preview.winfo_height()
        # labels
        panel_preview = tk.Label(frame_preview, text="Bitte ein Bild von der Festplatte öffnen", font=("Arial", 18), background="red")
        panel_preview.place(anchor='center', relx=0.5, rely=0.5)
        self.widgets["panel_preview"] = panel_preview
        panel_result = tk.Label(frame_result, background="blue")
        panel_result.place(anchor='center', relx=0.5, rely=0.5)
        self.widgets["panel_result"] = panel_result
        panel_console = tk.Label(master, background="grey", foreground="red", text="CONSOLE")
        panel_console.place(relx=1 / 20, rely=6 / 8, relwidth=11 / 20, relheight=2 / 8)
        self.widgets["panel_console"] = panel_console

        # buttons
        button_pixelate = tk.Button(master, state="disabled", text="Pixelate", command=lambda: self.pixelate())
        button_pixelate.place(relx=1 / 20, rely=2 / 8, relwidth=2 / 20, relheight=.5 / 8)
        self.widgets["button_pixelate"] = button_pixelate
        button_asciiate = tk.Button(master, state="disabled", text="toASCII", command=lambda: self.asciiate())
        button_asciiate.place(relx=1 / 20, rely=3 / 8, relwidth=2 / 20, relheight=.5 / 8)
        self.widgets["button_asciiate"] = button_asciiate

        button_open_image = tk.Button(self.master, text="Open Image", command=lambda: self.open_file())
        button_open_image.place(relx=12.33 / 20, rely=6.5 / 8, relwidth=2 / 20, relheight=1 / 8)
        self.widgets["button_open_image"] = button_open_image
        button_save_image = tk.Button(self.master, text="Save as Image", command=lambda: self.save_file_as_img())
        button_save_image.place(relx=14.66 / 20, rely=6.5 / 8, relwidth=2 / 20, relheight=1 / 8)
        self.widgets["button_save_image"] = button_save_image
        button_save_txt = tk.Button(self.master, text="Save as .txt", command=lambda: self.save_file_as_txt())
        button_save_txt.place(relx=17 / 20, rely=6.5 / 8, relwidth=2 / 20, relheight=1 / 8)
        self.widgets["button_save_txt"] = button_save_txt

        self.create_default_folders()
        self.create_json()
        self.default_settings()

        # master.bind("<Configure>", self.resize_window)
        self.widgets["frame_preview"].bind("<Configure>", self.resize_on_event)

    def resize_on_event(self, event):
        global WIN_W, WIN_H
        if (WIN_W != event.width) or (WIN_H != event.height):
            print("resize")
            WIN_W, WIN_H = event.width, event.height
            self.fit_to_frame()

    def fit_to_frame(self):
        # resize images in frames
        frame_w = int(self.widgets["frame_preview"].winfo_width() * FRAME_SCALE)
        frame_h = int(self.widgets["frame_preview"].winfo_height() * FRAME_SCALE)
        if not self.IMG_PREVIEW:
            return
        new_img = self.IMG_PREVIEW.copy()
        new_img.thumbnail((frame_w, frame_h))
        self.preview_thumb = ImageTk.PhotoImage(new_img)
        self.widgets["panel_preview"].configure(image=self.preview_thumb)
        if not self.IMG_RESULT:
            return
        new_img = self.IMG_RESULT.copy()
        new_img.thumbnail((frame_w, frame_h))
        self.result_thumb = ImageTk.PhotoImage(new_img)
        self.widgets["panel_result"].configure(image=self.result_thumb)

    def open_batch_dialog(self):
        pass

    def open_global_settings(self):
        pass

    def default_settings(self):
        #TODO: diese Variablen rausschmeißen!!!???
        self.PIX_MAX_THUMB_H = 500
        self.PIX_MAX_THUMB_W = 500
        self.PIX_PX_SIZE = 20
        self.ASC_PX_SIZE = 5

    def save_settings(self):
        import json
        settings = {
            "PIX_MAX_THUMB_H": self.PIX_MAX_THUMB_H,
            "PIX_MAX_THUMB_W": self.PIX_MAX_THUMB_W,
            "PIX_PX_SIZE": self.PIX_PX_SIZE,
            "ASC_PX_SIZE": self.ASC_PX_SIZE
        }
        settings_json = json.dumps(settings)
        with open(JSON_FILE, "w") as jf:
            jf.write(settings_json)

    def pixelate(self):
        """
        function for pixelating images (averaging over pixel-chunks)
        :return: None
        """

        # setup grid for creating the pixelated image
        pix = self.IMG_PREVIEW.load()
        width, height = self.IMG_PREVIEW.size
        ncols = int(width / self.PIX_PX_SIZE)
        nrows = int(height / self.PIX_PX_SIZE)
        ncols_remainder = width % self.PIX_PX_SIZE
        nrows_remainder = height % self.PIX_PX_SIZE
        if ncols_remainder > 0:
            ncols += 1
        if nrows_remainder > 0:
            nrows += 1

        # create array for new Pixels
        result_arr = [[0 for _ in range(nrows)] for _ in range(ncols)]
        for j in range(0, nrows):
            for i in range(0, ncols):
                pix_arr = []
                for pix_j in range(j * self.PIX_PX_SIZE, j * self.PIX_PX_SIZE + self.PIX_PX_SIZE):
                    for pix_i in range(i * self.PIX_PX_SIZE, i * self.PIX_PX_SIZE + self.PIX_PX_SIZE):
                        if pix_i < width and pix_j < height:
                            pix_arr.append(pix[pix_i, pix_j])
                result_arr[i][j] = self.get_array_mean(pix_arr)

        # create new Image
        new_img = Image.new(mode="RGB", size=(width, height))
        new_pix = new_img.load()
        for j in range(0, nrows):
            for i in range(0, ncols):
                for pix_j in range(j * self.PIX_PX_SIZE, j * self.PIX_PX_SIZE + self.PIX_PX_SIZE):
                    for pix_i in range(i * self.PIX_PX_SIZE, i * self.PIX_PX_SIZE + self.PIX_PX_SIZE):
                        if pix_i < width and pix_j < height:
                            if isinstance(result_arr[i][j], int):
                                new_pix[pix_i, pix_j] = result_arr[i][j]
                            elif isinstance(result_arr[i][j], tuple):
                                new_rgb = result_arr[i][j][0:3]
                                new_pix[pix_i, pix_j] = new_rgb
        self.IMG_RESULT = new_img
        self.fit_to_frame()
        print("image created!")

    def asciiate(self):
        """
        convert pixel-areas to ASCII-code
        :return: None
        """
        pix = self.IMG_PREVIEW.load()
        width, height = self.IMG_PREVIEW.size
        ncols = int(width / self.ASC_PX_SIZE)
        nrows = int(height / self.ASC_PX_SIZE)
        # create array for new ASCII-characters
        arr = [[0 for _ in range(nrows)] for _ in range(ncols)]
        for j in range(0, nrows):
            for i in range(0, ncols):
                pix_arr = []
                for pix_j in range(j * self.ASC_PX_SIZE, j * self.ASC_PX_SIZE + self.ASC_PX_SIZE):
                    for pix_i in range(i * self.ASC_PX_SIZE, i * self.ASC_PX_SIZE + self.ASC_PX_SIZE):
                        pix_arr.append(pix[pix_i, pix_j])
                arr[i][j] = int(np.mean(pix_arr) + 0.5)

        # fill new_array with ascii-characters
        chars = "N@#W$9876543210?!abc;:+=,._ "
        result_arr = [[0 for _ in range(nrows)] for _ in range(ncols)]
        scale = 255 / len(chars)
        for j in range(0, nrows):
            for i in range(0, ncols):
                ascii_value = int(arr[i][j] / scale - 1)
                result_arr[i][j] = chars[ascii_value]

        # create Image to write the ASCII-chars inside
        self.IMG_RESULT = Image.new("RGB", (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(self.IMG_RESULT)
        # TODO: mehrere fonts auswählbar machen, Größe des Ergebnisses soll gleich grpß sein!
        fontsize = int(height / ncols)
        font = ImageFont.truetype(PATH_FONT_DEFAULT, fontsize)

        # save result in self.ascii_text to be able to save it later
        self.ascii_text = ""
        for row in range(0, nrows):
            line2draw = ""
            for col in range(0, ncols):
                line2draw += result_arr[col][row]
            draw.text((0, row * fontsize), line2draw, (0, 0, 0), font)
            self.ascii_text += line2draw + "\n"

        # show ascii-image in result panel
        self.fit_to_frame()

    def save_file_as_txt(self):
        """

        :return:
        """
        if len(self.ascii_text) == 0:
            messagebox.showinfo("Achtung", "Du hast noch kein ASCII-File erstellt, das man speichern könnte.")
            return
        filename = self.next_file_name(PATHS_USERDIR["TXT"], ".txt")
        save_path_iowrapper = filedialog.asksaveasfile(mode='w', defaultextension=".txt",
                                                       initialdir=PATHS_USERDIR["TXT"],
                                                       initialfile=filename,
                                                       filetypes=[("Text files", ".txt")])
        save_path = save_path_iowrapper.name
        if save_path is None:
            return
        with open(str(save_path), "w") as f:
            f.write(self.ascii_text)

    def save_file_as_img(self):
        if self.IMG_RESULT is None:
            messagebox.showinfo("Achtung", "Du hast noch kein Bild erstellt, das man speichern könnte.")
            return
        filename = self.next_file_name(PATHS_USERDIR["IMG"], ".jpg")
        save_path = filedialog.asksaveasfile(mode='w', defaultextension=".jpg", initialdir=PATHS_USERDIR["IMG"],
                                             initialfile=filename, filetypes=[
                ("JPG files", ("*.jpg", "*.jpeg", "*.jfif", "*.pjpeg", "*.pjp")),
                ("PNG files", "*.png"),
                ("GIF files", "*.gif"),
                ("WebP files", "*.webp"),
                ("All files", "*")])
        if save_path is None:
            return
        self.IMG_RESULT.save(save_path)

    def open_file(self):

        # TODO      Überlegen,ob es sinvoll ist, eine "Tutorial-Markierung" zu erstellen, die verschwindet,
        # TODO          sobald man auf Bild öffnen klickt

        new_filename = filedialog.askopenfilename()
        if len(new_filename) == 0:
            return
        # TODO: restrictions
        try:
            self.IMG_PREVIEW = Image.open(new_filename)
        except Exception as e:
            print(e)
            return

        self.PATH_TO_IMAGE = new_filename
        self.IMG_PREVIEW = Image.open(self.PATH_TO_IMAGE)

        # resize images in frames
        frame_w = int(self.widgets["frame_preview"].winfo_width() * FRAME_SCALE)
        frame_h = int(self.widgets["frame_preview"].winfo_height() * FRAME_SCALE)
        new_img = self.IMG_PREVIEW.copy()
        new_img.thumbnail((frame_w, frame_h))
        self.preview_thumb = ImageTk.PhotoImage(new_img)
        self.widgets["panel_preview"].configure(image=self.preview_thumb)
        self.widgets["button_pixelate"].configure(state="active")
        self.widgets["button_asciiate"].configure(state="active")
        # TODO: mit oder ohne path-label?
        # self.widgets["label_path_preview"].configure(text=self.PATH_TO_IMAGE)


    @staticmethod
    def get_cell_size():
        """
        Calculates the width and height for one cell
        :return: (width, heigth)
        """
        cell_w = int(WIN_W / GRID_COLS)
        cell_h = int(WIN_H / GRID_ROWS)
        return cell_w, cell_h

    @staticmethod
    def get_array_mean(arr):
        """
        Calculates the mean for every col of a 3-columned table
        :param arr:
        :return: result (new RGB-Code, which is the mean of the respective basic color)
        """
        r = [x[0] for x in arr]
        g = [x[1] for x in arr]
        b = [x[2] for x in arr]
        result = (int(np.mean(r) + 0.5), int(np.mean(g) + 0.5), int(np.mean(b) + 0.5))
        return result

    @staticmethod
    def create_default_folders():
        """
        Function to create a directory for saving the results
        :return:
        """
        for path in PATHS_USERDIR.values():
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except Exception as e:
                    print("Could not create Folder: " + path)
                    print(e)

    @staticmethod
    def create_json():
        """
        Function to create a json-file foor storing the settings
        :return:
        """
        # TODO: braucht man das?
        if not os.path.exists(JSON_FILE):
            with open(JSON_FILE, "w") as jf:
                jf.write(" ")

    @staticmethod
    def next_file_name(path, fileformat):
        """
        :return: new_index; reads all filenames in the save folder, extracts leading 3 numbers and returns the next
        possible number. Serves as automated filename
        """
        all_files = [x for x in os.listdir(path) if os.path.splitext(x)[1] == fileformat]
        indices_str = []
        # check if isdigit
        for f in all_files:
            indices_str += [f[:3]] if f[:3].isdigit() else []
        indices = [int(x) for x in indices_str]
        new_index = "001" if len(indices) == 0 else str(max(indices) + 1)
        while len(new_index) < 3:
            new_index = "0" + new_index
        return new_index + fileformat


if __name__ == "__main__":
    print("START IMAGE WIZARD")
    root = tk.Tk()
    root.title("Image Wizard")
    # root.iconbitmap("")
    SCREEN_W = root.winfo_screenwidth()
    SCREEN_H = root.winfo_screenheight()
    root.minsize(800, 600)
    root.geometry(str(WIN_W) + "x" + str(WIN_H))
    ImageWizard(root)
    root.mainloop()
