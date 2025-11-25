import tkinter as tk
from tkinter import filedialog,font
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import networkx as nx
from graph_models.micrograph import * 
import time 


def get_text_size_in_inches(text_widget):
    # Ensure geometry is updated
    text_widget.update_idletasks()

    # Get widget size in pixels
    width_px = text_widget.winfo_width()
    height_px = text_widget.winfo_height()

    # Get screen DPI (pixels per inch)
    # winfo_fpixels('1i') returns pixels in 1 inch
    dpi_x = text_widget.winfo_fpixels('1i')
    dpi_y = text_widget.winfo_fpixels('1i')

    # Convert to inches
    width_in = width_px / dpi_x
    height_in = height_px / dpi_y

    return width_in, height_in

def dict_to_networkx(d): 
    G = nx.Graph()

    nodes = list(d.keys()) 
    edges = []
    for k,v in d.items(): 
        for v_ in v: 
            edges.append((k,v_))

    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G 

"""
the main Tkinter application class for xFS user 
interface (xFS UI). 
"""
class XFSApplication(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.init_primary_window_details() 
        self.set_primary_window_details()

    def init_primary_window_details(self):
        bold_font = font.Font(family="Arial", size=12, weight="bold")
        self.text_widget = tk.Text(self, wrap="word", width=80, bg="gray",fg="blue",height=15)
        self.open_button = tk.Button(self, text="OpEn GRaf FiLe", command=self.open_file__graph)

        
    def set_primary_window_details(self): 
        self.text_widget.grid() 
        self.open_button.grid() 

        figsize = get_text_size_in_inches(self.text_widget)
        fig = Figure(figsize=figsize,dpi=100)
        self.canvass = FigureCanvasTkAgg(fig, master=self)
        self.canvass_ax = fig.add_subplot()
        self.canvass_ax.set_visible(False)
        self.canvass.get_tk_widget().grid()

    def open_file__graph(self): 
        file_path = filedialog.askopenfilename(
            title="Select a Text File") 
        if file_path:
            D = dict_from_file(file_path)
            self.change_graph(D)
            return

    def change_graph(self,D): 
        G = dict_to_networkx(D)
        self.canvass_ax.clear()
        self.canvass_ax.set_visible(True)
        nx.draw(G, with_labels=True, font_weight='bold', ax=self.canvass_ax)
        self.canvass.draw()

def run_xfs_app(): 
    app = XFSApplication()
    app.master.title('XFS Vhindose')  
    app.mainloop()