# Source - https://stackoverflow.com/a
# Posted by furas, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-22, License - CC BY-SA 4.0

import networkx as nx
import tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import random

def change_graph():

    #nodes = [1, 2, 3, 4, 5, 6]
    #edges = [(1, 2), (3, 4), (1,4), (2, 3), (4, 5), (5, 6)]

    n = random.randint(4, 10)
    nodes = list(range(n))
    edges = [random.sample(nodes, 2) for _ in range(2*n)]

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    ax.clear()     # remove previous graph 
    nx.draw(G, with_labels=True, font_weight='bold', ax=ax)
    canvas.draw()  # it needs it in this place
    
# --- create graph

G = nx.Graph()
G.add_nodes_from([1, 2, 3, 4])
G.add_edges_from([(1, 2), (3, 4), (1,4), (2, 3)])

# ---

root = tkinter.Tk()
root.wm_title("Embedding in Tk")

# --- create figure and axis
# --- draw graph using `ax=ax`

fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot()
nx.draw(G, with_labels=True, font_weight='bold', ax=ax)
#canvas.draw()

# --- create widgets

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill='both', expand=True)
#canvas.draw()

# --- other elements in window

button_change = tkinter.Button(root, text="Change Graph", command=change_graph)
button_change.pack(fill='x')

button_quit = tkinter.Button(root, text="Quit", command=root.destroy)
button_quit.pack(fill='x')

tkinter.mainloop()
