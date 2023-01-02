import tkinter as tk
import main

def create_widgets(cell_w, cell_h, master):
    frame_images = tk.Frame(master, bg=f"#000000")
    frame_images.grid_propagate(False)
    frame_images.grid(row=1, column=5, rowspan=5, columnspan=14)
    self.widgets["frame_images"] = frame_images

    panel_preview = tk.Label(frame_images)
    panel_preview.grid(row=1, column=5, rowspan=5, columnspan=7, padx=5, pady=5)
    self.widgets["panel_preview"] = panel_preview
    panel_result = tk.Label(frame_images)  # , borderwidth=2, relief="groove")
    panel_result.grid(row=1, column=12, rowspan=5, columnspan=7, padx=5, pady=5)
    self.widgets["panel_result"] = panel_result
    # panel_console = tk.Label(self.master, background="grey")
    # panel_console.grid(row=6, column=1, rowspan=2, columnspan=11, padx=5, pady=5)
    # self.widgets["panel_console"] = panel_console

    button_pixelate = tk.Button(self.master, state="disabled", text="Pixelate", command=lambda: self.pixelate())
    button_pixelate.grid(row=1, column=1, columnspan=1, padx=5, pady=5)
    self.widgets["button_pixelate"] = button_pixelate
    button_asciiate = tk.Button(self.master, state="disabled", text="toASCII", command=lambda: self.asciiate())
    button_asciiate.grid(row=2, column=1, columnspan=1, padx=5, pady=5)
    self.widgets["button_asciiate"] = button_asciiate

    # label_path_preview = tk.Label(self.master)
    # label_path_preview.grid(row=1, column=5, columnspan=7, padx=5, pady=5)
    # self.widgets["label_path_preview"] = label_path_preview

    button_open_image = tk.Button(self.master, text="Open Image", command=lambda: self.open_file())
    button_open_image.grid(row=6, column=12, rowspan=1, columnspan=1, padx=5, pady=5)
    self.widgets["button_open_image"] = button_open_image
    button_save_image = tk.Button(self.master, text="Save as Image", command=lambda: self.save_file_as_img())
    button_save_image.grid(row=6, column=14, rowspan=1, columnspan=1, padx=5, pady=5)
    self.widgets["button_save_image"] = button_save_image
    button_save_txt = tk.Button(self.master, text="Save as .txt", command=lambda: self.save_file_as_txt())
    button_save_txt.grid(row=6, column=16, rowspan=1, columnspan=1, padx=5, pady=5)
    self.widgets["button_save_txt"] = button_save_txt

    # self.button_save_settings = tk.Button(self.master, text="Save Settings", command=lambda: self.save_settings())
    # self.button_save_settings.grid(row=7, column=19, padx=5, pady=5)

    # set width and height of widgets
    for w_name, widget in self.widgets.items():
        winfo = widget.grid_info()
        c_span = winfo["columnspan"]
        r_span = winfo["rowspan"]
        pad = winfo["padx"]
        new_width = cell_w * c_span - 2 * pad
        new_height = cell_h * r_span - 2 * pad
        print("###")
        print(w_name)
        print(widget.widgetName)
        print(new_width)
        print(new_height)

        row = winfo["row"]
        col = winfo["column"]
        print(widget.config())
        widget.config(width=new_width, height=new_height)
        widget.grid(row=row, column=col, columnspan=c_span, rowspan=r_span)
    return widgets