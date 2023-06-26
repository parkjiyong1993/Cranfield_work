import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import re


beta_Nc_Wc = None
beta_Nc_PR = None
beta_values = None

fan_status_var = None
fan_status_label = None
figures = []
current_figure_index = -1

def load_fan_file(status_var, status_label):
    global beta_Nc_Wc
    global beta_Nc_PR
    global beta_values

    filename = filedialog.askopenfilename(filetypes=[("Map files", "*.map")])  # Only .map files can be imported
    if filename:
        with open(filename, 'r') as f:
            data = f.read()

        beta_Nc_Wc = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+Wc =  {(.*?)}', data, re.DOTALL)
        beta_Nc_PR = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+PR =  {(.*?)}', data, re.DOTALL)
        beta_values = [int(beta) for beta, _, _ in beta_Nc_Wc]

        status_var.set(1)  # Indicate that the file is successfully loaded
        status_label.config(text="File loaded successfully.")
    else:
        status_var.set(0)  # Indicate that no file is loaded
        status_label.config(text="No file loaded.")

def plot_line_graph():
    global current_figure_index
    if beta_Nc_Wc is None or beta_Nc_PR is None:  
        messagebox.showwarning("Warning", "No file is loaded yet!")  
        return

    # Create a new window for the beta selection and plot
    plot_window = tk.Toplevel()
    plot_window.geometry("900x650")

    Wc_values = [[float(val) for val in Wc.split(', ')] for _, _, Wc in beta_Nc_Wc]
    PR_values = [[float(val) for val in PR.split(', ')] for _, _, PR in beta_Nc_PR]

    listbox_frame = tk.Frame(plot_window, relief=tk.SUNKEN, highlightbackground="green", highlightthickness=1, borderwidth=1, width=200, height=100)  # Create a visible frame with a specified size
    listbox_frame.grid(row=2, column=1, rowspan=6, padx=(0, 20))  # Grid it to the left side with some horizontal padding

    frame_label = tk.Label(listbox_frame, text="Selection Beta")  # Create the label inside the frame
    frame_label.pack()  # Pack it at the top of the frame

    scrollbar = tk.Scrollbar(listbox_frame)  # Create a scrollbar inside the frame
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Pack it to the right side, filling in the Y direction

    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)  # Link the scrollbar to the listbox
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)  # Pack the listbox to the left side, filling in both directions
    scrollbar.config(command=listbox.yview)  # Link the listbox to the scrollbar

    listbox.insert(tk.END, 'All')  # Add an 'All' option
    for beta in beta_values:
        listbox.insert(tk.END, f'beta={beta}')  # Insert the beta values into the listbox


    #listbox = tk.Listbox(plot_window, selectmode=tk.MULTIPLE)  # Create a listbox for the beta values
    #listbox.grid(row=1, column=1, rowspan=6)  # Grid it to the left side
    #listbox.insert(tk.END, 'All')  # Add an 'All' option

    figure_index_label = tk.Label(plot_window, text="No figures yet.")
    figure_index_label.grid(row=1, column=2)  # Grid it on top of the canvas

    canvas = FigureCanvasTkAgg(plt.figure(), master=plot_window)  # Create the initial canvas
    canvas.get_tk_widget().grid(row=2, column=2, rowspan=5)  # Grid it to the right of the listbox

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
        selected_betas = [listbox.get(i) for i in listbox.curselection()]  # Get the selected beta values
        if not selected_betas:
            messagebox.showwarning("Warning", "No beta values are selected!")  
            return
        if 'All' in selected_betas:
            selected_betas = beta_values  # If 'All' is selected, plot all betas
        else:
            selected_betas = [int(beta[5:]) for beta in selected_betas]  # Convert to int if 'All' is not selected
        
        fig = plt.figure()  # Create a new figure
        for beta, Wc, PR in zip(beta_values, Wc_values, PR_values):
            if beta in selected_betas:  # Plot only the selected beta values
                plt.plot(PR, Wc, label=f'beta={beta}')
        
        plt.xlabel('PR')
        plt.ylabel('Wc')
        plt.title('PR-Wc graph for different Beta values')
        plt.legend()

        figures.append(fig)  # Add the new figure to the list of figures
        current_figure_index = len(figures) - 1  # Update the current figure index

        # Update the canvas
        canvas.figure = fig
        canvas.draw()
        update_buttons_and_label()

    plot_button = tk.Button(plot_window, text="Plot Selected Graphs", command=plot_selected)
    plot_button.grid(row=7, column=1)  # Grid it below the listbox

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
        messagebox.showinfo("Read Me", "For the beta, if you choose All, please deselect other choices.")  # Display some message

    read_me_button = tk.Button(plot_window, text="Read Me", command=display_readme)
    read_me_button.grid(row=0, column=0)  # Grid it below the plot button

    update_buttons_and_label()
