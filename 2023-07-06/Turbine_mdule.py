import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import re


turbine_Nc_dHqT = None
turbine_Nc_Wc = None
turbine_Nc_values = None

fan_status_var = None
fan_status_label = None
figures = []
current_figure_index = -1


def load_turbine_file(status_var, status_label):
    global turbine_Nc_dHqT
    global turbine_Nc_Wc
    global turbine_Nc_values

    filename = filedialog.askopenfilename(filetypes=[("Map files", "*.map")])  # Only .map files can be imported
    if filename:
        with open(filename, 'r') as f:
            data = f.read()

        turbine_Nc_dHqT= re.findall(r"Nc\s*=\s*(.*?)\s*{\s*dHqT\s*=\s*{(.*?)}", data, re.DOTALL)
        turbine_Nc_Wc = re.findall(r"Nc\s*=\s*(.*?)\s*{\s*dHqT\s*=.*?\s*Wc\s*=\s*{(.*?)}", data, re.DOTALL)
        turbine_Nc_values = [float(Nc) for Nc, _ in turbine_Nc_Wc]
        #turbine_Nc_values = [int(float(Nc)) for Nc, _ in turbine_Nc_dHqT]
        print(turbine_Nc_values)

        status_var.set(1)
        status_label.config(text="FIle loaded successfully.")
    else:
        status_var.set(0)
        status_label.config(text="No file loaded.")


def plot_turbine_line_graph():
    global current_figure_index
    if turbine_Nc_dHqT is None or turbine_Nc_dHqT is None:
        messagebox.showwarning("Warning", "No file is loaded yet!")
        return

    # Create a new window for the Nc selection and plot
    plot_window = tk.Toplevel()
    plot_window.geometry("1150x750")

    turbine_Wc_values = [[float(val) for val in Wc.split(', ')] for _, Wc in turbine_Nc_Wc]
    turbine_dHqT_values = [[float(val) for val in dHqT.split(',')] for _, dHqT in turbine_Nc_dHqT]

    listbox_frame = tk.Frame(plot_window, relief=tk.SUNKEN, highlightbackground="green", highlightthickness=1, borderwidth=1, width=200, height=100)
    listbox_frame.grid(row=2, column=1, rowspan=6, padx=(0, 20))

    frame_label = tk.Label(listbox_frame, text="Select Nc")
    frame_label.pack()

    scrollbar = tk.Scrollbar(listbox_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)
    scrollbar.config(command=listbox.yview)

    listbox.insert(tk.END, 'All')
    for Nc in turbine_Nc_values:
        listbox.insert(tk.END, f'Nc={Nc}')

    figure_index_label = tk.Label(plot_window, text="No figures yet.")
    figure_index_label.grid(row=1, column=2)

    fig = plt.figure(figsize=(8.5,6))  # Create a figure with desired size
    canvas = FigureCanvasTkAgg(fig, master=plot_window)  # Create the initial canvas

    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=2, column=2, rowspan=5)  # Grid it to the right of the listbox
    canvas_widget.configure(width=800, height=600) 

    #canvas = FigureCanvasTkAgg(plt.figure(), master=plot_window)  # Create the initial canvas
    #canvas.get_tk_widget().grid(row=2, column=2, rowspan=5)  # Grid it to the right of the listbox

    def update_buttons_and_label():
        if not figures or current_figure_index == 0:
            previous_button.config(state="disabled")
        else:
            previous_button.config(state="normal")

        if not figures or current_figure_index == len(figures) - 1:
            next_button.config(state="disabled")
        else:
            next_button.config(state="normal")

        if figures:
            figure_index_label.config(text=f"Figure {current_figure_index + 1} of {len(figures)}")
        else:
            figure_index_label.config(text="No figures yet.")

    def plot_selected():
        global current_figure_index
        selected_Nc = [listbox.get(i) for i in listbox.curselection()]
        if not selected_Nc:
            print("Warning: No Nc values are selected!")
            return
        if 'All' in selected_Nc:
            selected_Nc = turbine_Nc_values
        else:
            selected_Nc = [float(Nc[3:]) for Nc in selected_Nc]

        fig = plt.figure(figsize=(8.5,6))
        #fig = plt.figure()
        for Nc, Wc, dHqT in zip(turbine_Nc_values, turbine_Wc_values, turbine_dHqT_values):
            if Nc in selected_Nc:  # Plot only the selected beta values
                plt.plot(dHqT, Wc, label=f'Nc={Nc}')

        plt.xlabel('dHqT')
        plt.ylabel('Wc')
        plt.title('dHqT-Wc graph for different Nc values')
        #plt.legend()
        plt.legend(fontsize='small') 

        figures.append(fig)  
        current_figure_index = len(figures) - 1  

        # Update the canvas
        canvas.figure = fig
        canvas.draw()
        update_buttons_and_label()

    plot_button = tk.Button(plot_window, text="Plot Selected Graphs", command=plot_selected)
    plot_button.grid(row=7, column=1)

    def show_previous_figure():
        global current_figure_index
        if current_figure_index > 0:  # If the current figure is not the first one
            current_figure_index -= 1  # Go to the previous figure
            canvas.figure = figures[current_figure_index]  # Update the canvas
            canvas.draw()
        update_buttons_and_label()

    previous_button = tk.Button(plot_window, text="<< Previous Figure", command=show_previous_figure, state="disabled")
    previous_button.grid(row=7, column=2)  # Grid it to the left side

    def show_next_figure():
        global current_figure_index
        if current_figure_index < len(figures) - 1:  # If the current figure is not the last one
            current_figure_index += 1  # Go to the next figure
            canvas.figure = figures[current_figure_index]  # Update the canvas
            canvas.draw()
        update_buttons_and_label()

    next_button = tk.Button(plot_window, text="Next Figure >>", command=show_next_figure, state="disabled")
    next_button.grid(row=8, column=2)  # Grid it to the right side

    def display_readme():
        messagebox.showinfo("Read Me", "For the Nc, if you choose All, please deselect other choices.")  # Display some message

    read_me_button = tk.Button(plot_window, text="Read Me", command=display_readme)
    read_me_button.grid(row=0, column=0)  # Grid it below the plot button

    update_buttons_and_label()

