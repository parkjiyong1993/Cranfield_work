import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
import re


beta_Nc_Wc = None
beta_Nc_PR = None
beta_values = None

HPC_status_var = None
HPC_status_label = None
figures = []
current_figure_index = -1

def load_HPC_file(status_var, status_label):
    global beta_Nc_Wc
    global beta_Nc_PR
    global beta_values  

    filename = filedialog.askopenfilename(filetypes=[("Map files", "*.map")])  # Only .map files can be imported
    if filename:
        with open(filename, 'r') as f:
            data = f.read()

        vigv_blocks = re.findall(r'(VIGV = \d+ \{.*?\})', data, re.DOTALL)

        beta_Nc_Wc = []
        beta_Nc_PR = []

        # Iterate over each VIGV block
        for block in vigv_blocks:
            # Extract VIGV value
            vigv = re.search(r'VIGV = (\d+)', block).group(1)
            
            # Extract all beta, Nc, Wc within this block
            block_beta_Nc_Wc = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+Wc =  {(.*?)}', data, re.DOTALL)
            # Extract all beta, Nc, PR within this block
            block_beta_Nc_PR = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+PR =  {(.*?)}', data, re.DOTALL)

            # For each beta, Nc, Wc set, append it along with VIGV value to the result
            for beta, nc, wc in block_beta_Nc_Wc:
                beta_Nc_Wc.append((vigv, beta, nc, wc))

            # For each beta, Nc, PR set, append it along with VIGV value to the result
            for beta, nc, pr in block_beta_Nc_PR:
                beta_Nc_PR.append((vigv, beta, nc, pr))

        beta_values = [int(beta) for _, beta, _, _ in beta_Nc_Wc]

        #print(block_beta_Nc_Wc)

        print(beta_Nc_Wc)
        print(beta_values)

        status_var.set(1)  # Indicate that the file is successfully loaded
        status_label.config(text="File loaded successfully.")
    else:
        status_var.set(0)  # Indicate that no file is loaded
        status_label.config(text="No file loaded.")

def VIGV_selection_window():
    global beta_Nc_Wc
    global selected_VIGV  # declare 
    selected_VIGV = [tk.StringVar()] # init
    VIGV_values = sorted(set(VIGV for VIGV, _, _, _ in beta_Nc_Wc))  # Extract unique VIGV values
    
    selection_window = tk.Toplevel()
    selection_window.geometry("350x350")
    
    listbox_frame = tk.Frame(selection_window, relief=tk.SUNKEN, highlightbackground="green", highlightthickness=1, borderwidth=1, width=200, height=100)  
    listbox_frame.grid(row=1, column=1, rowspan=6, padx=(20, 20))  

    frame_label = tk.Label(listbox_frame, text="Selection VIGV")  
    frame_label.pack() 

    scrollbar = tk.Scrollbar(listbox_frame) 
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  

    listbox = tk.Listbox(listbox_frame, selectmode=tk.SINGLE, yscrollcommand=scrollbar.set)  
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)  
    scrollbar.config(command=listbox.yview)

    for VIGV in VIGV_values:
        listbox.insert(tk.END, VIGV)

    def select_and_close():
        if not listbox.curselection():
            messagebox.showwarning("Warning", "No VIGV is selected!") 
            return

        selected_VIGV[0].set(listbox.get(listbox.curselection()))
        selection_window.destroy()
        #update_plot(selected_VIGV[0].get())
        plot_HPC_line_graph(selected_VIGV[0].get())  # Call plot function with selected VIGV value

    select_button = tk.Button(selection_window, text="Select", command=select_and_close)
    select_button.grid(row=7, column=1)

plot_window = None

# Change the plot function to accept a selected_VIGV_value parameter
def plot_HPC_line_graph(selected_VIGV_value=None):  
    global current_figure_index
    global beta_Nc_Wc
    global beta_Nc_PR

    global plot_window

    if plot_window is None:
        plot_window = tk.Toplevel()
        plot_window.geometry("1150x750")
    else:
        # If it does, clear the plot for new data
        plt.clf()

    # Create a new window for the beta selection and plot
    #plot_window = tk.Toplevel()
    # New window whole size
    #plot_window.geometry("1150x750")

    if beta_Nc_Wc is None or beta_Nc_PR is None:  
        messagebox.showwarning("Warning", "No file is loaded yet!")  
        return

    #(VIGV, beta, Nc, Wc) or (VIGV, beta, Nc, PR)
    Wc_values = [[float(val) for val in Wc.split(', ')] for VIGV, _, _, Wc in beta_Nc_Wc if VIGV == selected_VIGV_value]
    PR_values = [[float(val) for val in PR.split(', ')] for VIGV, _, _, PR in beta_Nc_PR if VIGV == selected_VIGV_value]

    beta_values_for_selected_VIGV = sorted(set(int(beta) for VIGV, beta, _, _ in beta_Nc_Wc if VIGV == selected_VIGV_value))  # Extract unique beta values for selected VIGV

    listbox_frame = tk.Frame(plot_window, relief=tk.SUNKEN, highlightbackground="green", highlightthickness=1, borderwidth=1, width=200, height=100)  # Create a visible frame with a specified size
    listbox_frame.grid(row=2, column=1, rowspan=6, padx=(0, 20))  

    frame_label = tk.Label(listbox_frame, text="Selection Beta")  
    frame_label.pack() 

    scrollbar = tk.Scrollbar(listbox_frame) 
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  

    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)  
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)  
    scrollbar.config(command=listbox.yview)  

    listbox.insert(tk.END, 'All')  
    for beta in beta_values:
        listbox.insert(tk.END, f'beta={beta}')  

    figure_index_label = tk.Label(plot_window, text="No figures yet.")
    figure_index_label.grid(row=1, column=2)  
    fig = plt.figure(figsize=(8.5,6))
    canvas = FigureCanvasTkAgg(fig, master=plot_window) 

    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=2, column=2, rowspan=5)  
    canvas_widget.configure(width=800, height=600)  

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
            selected_betas = beta_values_for_selected_VIGV
            #selected_betas = beta_values  
        else:
            selected_betas = [int(beta[5:]) for beta in selected_betas] 
        
        fig = plt.figure(figsize=(8.5,6))  

        for beta, Wc, PR in zip(beta_values_for_selected_VIGV, Wc_values, PR_values):
            if beta in selected_betas:  
                plt.plot(Wc, PR, label=f'beta={beta}')
        
        plt.xlabel('Wc')
        plt.ylabel('PR')
        plt.title('Wc-PR graph for different Beta values (VIGV={selected_VIGV_value}) ')
        plt.legend(fontsize='small') 
        #plt.legend()

        print("Selected betas:", selected_betas)
        print("Beta values for selected VIGV:", beta_values_for_selected_VIGV)

        figures.append(fig)  
        current_figure_index = len(figures) - 1  
        
        canvas.figure = fig
        canvas.draw()
        update_buttons_and_label()

    plot_button = tk.Button(plot_window, text="Plot Selected Graphs", command=plot_selected)
    plot_button.grid(row=7, column=1)  # Grid it below the listbox 
    plot_button_VIGV = tk.Button(plot_window, text="Select the VIGV value", command=VIGV_selection_window)
    plot_button_VIGV.grid(row=3, column=1)


    def show_previous_figure():
        global current_figure_index
        if current_figure_index > 0:  
            current_figure_index -= 1  
            canvas.figure = figures[current_figure_index] 
            canvas.draw()
        update_buttons_and_label()

    previous_button = tk.Button(plot_window, text="<< Previous Figure", command=show_previous_figure, state="disabled")
    previous_button.grid(row=7, column=2) 

    def show_next_figure():
        global current_figure_index
        if current_figure_index < len(figures) - 1:  
            current_figure_index += 1  
            canvas.figure = figures[current_figure_index]  
            canvas.draw()
        update_buttons_and_label()

    next_button = tk.Button(plot_window, text="Next Figure >>", command=show_next_figure, state="disabled")
    next_button.grid(row=8, column=2)  # Grid it to the right side

    def display_readme():
        messagebox.showinfo("Read Me", "For the beta, if you choose All, please deselect other choices.")  # Display some message

    read_me_button = tk.Button(plot_window, text="Read Me", command=display_readme)
    read_me_button.grid(row=0, column=0)  # Grid it below the plot button

    update_buttons_and_label()
