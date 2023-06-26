import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import re

import Fan_module
import Turbine_module


def main():
    global root
    root = tk.Tk()
    root.geometry("800x600")

    # Fan map frame
    fan_frame = tk.LabelFrame(root, text="Fan Map")
    fan_frame.grid(row=0, column=0, padx=10, pady=10)

    fan_load_button = tk.Button(fan_frame, text="Load fan.map file", command=lambda: Fan_module.load_fan_file(fan_status_var, fan_status_label))
    fan_load_button.grid(row=0, column=0, padx=10, pady=10)

    fan_status_var = tk.IntVar(value=0)
    fan_status_label = tk.Label(fan_frame, text="")
    fan_status_label.grid(row=1, column=0, columnspan=3)

    fan_status_button = tk.Checkbutton(fan_frame, variable=fan_status_var, state="disabled")
    fan_status_button.grid(row=0, column=1, padx=10, pady=10)

    fan_plot_button = tk.Button(fan_frame, text="Plot fan graph", command=Fan_module.plot_line_graph)
    fan_plot_button.grid(row=2, column=0, padx=10, pady=10)

    # Turbine map frame 
    turbine_frame = tk.LabelFrame(root, text="Turbine Map")
    turbine_frame.grid(row=0, column=2, padx=10, pady=10)

    fan_load_button = tk.Button(turbine_frame, text="Load turbine.map file", command=lambda: Turbine_module.load_turbine_file(turbine_status_var, turbine_status_label))
    fan_load_button.grid(row=0, column=2, padx=10, pady=10)

    turbine_status_var = tk.IntVar(value=0)
    turbine_status_label = tk.Label(turbine_frame, text="")
    turbine_status_label.grid(row=1, column=2, columnspan=3)

    turbine_status_button = tk.Checkbutton(turbine_frame, variable=turbine_status_var, state="disabled")
    turbine_status_button.grid(row=0, column=3, padx=10, pady=10)

    turbine_plot_button = tk.Button(turbine_frame, text="Plot turbine graph", command=Turbine_module.plot_turbine_line_graph)
    turbine_plot_button.grid(row=2, column=2, padx=10, pady=10)

    root.mainloop()

   
if __name__ == "__main__":
    main()
