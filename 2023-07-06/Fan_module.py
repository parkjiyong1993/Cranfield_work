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
    global beta_Nc
    global beta_values


    filename = filedialog.askopenfilename(filetypes=[("Map files", "*.map")])  
    if filename:
        with open(filename, 'r') as f:
            data = f.read()

        beta_Nc = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)}', data, re.DOTALL)
        beta_Nc_Wc = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+Wc =  {(.*?)}', data, re.DOTALL)
        beta_Nc_PR = re.findall(r'beta = (\d+)\s+{\s+Nc =  {(.*?)\}\s+PR =  {(.*?)}', data, re.DOTALL)

        #print(beta_Nc_Wc)
        #print(beta_Nc_PR)
        beta_values = [int(beta) for beta, _, _ in beta_Nc_Wc]

        status_var.set(1) 
        status_label.config(text="File loaded successfully.")
    else:
        status_var.set(0)  
        status_label.config(text="No file loaded.")

def Nc_selection_window():
    global beta_Nc_Wc
    global selected_Nc  # declare 
    selected_Nc = [tk.StringVar()] # init
    selected_Nc_value = sorted(set(float(val) for _, Nc in beta_Nc for val in Nc.split(', ')))
    #selected_Nc_value = sorted(set(Nc for _, Nc, _ in beta_Nc_Wc))  # Extract unique Nc values
    
    selection_Nc_window = tk.Toplevel()
    selection_Nc_window.geometry("350x350")
    
    listbox_frame = tk.Frame(selection_Nc_window, relief=tk.SUNKEN, highlightbackground="green", highlightthickness=1, borderwidth=1, width=200, height=100)  
    listbox_frame.grid(row=1, column=1, rowspan=6, padx=(20, 20))  
    
    frame_label = tk.Label(listbox_frame, text="selection Nc")  
    frame_label.pack() 

    scrollbar = tk.Scrollbar(listbox_frame) 
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  

    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set)  
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)  
    scrollbar.config(command=listbox.yview)

    listbox.insert(tk.END, 'All') 
    for Nc in selected_Nc_value:
        listbox.insert(tk.END, Nc)

    def select_and_close():
        selected_items = [str(listbox.get(i)) for i in listbox.curselection()]
        if not selected_items:
            messagebox.showwarning("Warning", "No Nc is selected!") 
            return
        if 'All' in selected_items:
            selected_Nc[0].set(', '.join(str(val) for val in selected_Nc_value))
        else:
            selected_Nc[0].set(', '.join(selected_items))
        
        #if not listbox.curselection():
        #    messagebox.showwarning("Warning", "No Nc is selected!") 
        #    return

        
        selected_Nc[0].set(', '.join(selected_items))
        #selected_Nc[0].set(listbox.get(listbox.curselection()))
        selection_Nc_window.destroy()

    # Nc select window, select button
    select_button = tk.Button(selection_Nc_window, text="Select", command=select_and_close)
    select_button.grid(row=7, column=1)

def plot_Nc(ax1):
    global selected_Nc
    global current_figure_index
    global canvas

    Wc_values = [[float(val) for val in Wc.split(', ')] for _, _, Wc in beta_Nc_Wc]
    PR_values = [[float(val) for val in PR.split(', ')] for _, _, PR in beta_Nc_PR]
    Nc_values = [[float(val) for val in Nc.split(', ')] for _, Nc in beta_Nc]
    
    selected_Nc_items = selected_Nc[0].get().split(", ")
    if 'All' in selected_Nc_items:
        selected_Nc_floats = sorted(set(float(val) for _, Nc in beta_Nc for val in Nc.split(', ')))
    else:
        selected_Nc_floats = [float(val) for val in selected_Nc_items]
    #selected_Nc_floats = [float(val) for val in selected_Nc[0].get().split(", ")]
    for selected_Nc_float in selected_Nc_floats:
        Wc_for_selected_Nc = []
        PR_for_selected_Nc = []
        for Nc, Wc, PR in zip(Nc_values, Wc_values, PR_values):
            if selected_Nc_float in Nc:
                index = Nc.index(selected_Nc_float)
                Wc_for_selected_Nc.append(Wc[index])
                PR_for_selected_Nc.append(PR[index])
        ax1.plot(Wc_for_selected_Nc, PR_for_selected_Nc, label=f'Nc={selected_Nc_float}', linestyle='dashed')

    ax1.legend(loc="best", fontsize="x-small")
                    
plot_window = None

def plot_line_graph():
    global current_figure_index
    global plot_window
    global beta_Nc_Wc
    global beta_Nc_PR
    global canvas
    global show_Nc

    if beta_Nc_Wc is None or beta_Nc_PR is None:  
        messagebox.showwarning("Warning", "No file is loaded yet!")  
        return
    
    if plot_window is None:
        plot_window = tk.Toplevel()
        plot_window.geometry("1150x750")
    else:
        # If it does, clear the plot for new data
        plt.clf()

    Wc_values = [[float(val) for val in Wc.split(', ')] for _, _, Wc in beta_Nc_Wc]
    PR_values = [[float(val) for val in PR.split(', ')] for _, _, PR in beta_Nc_PR]
    Nc_values = [[float(val) for val in Nc.split(', ')] for _, Nc in beta_Nc]
    
    listbox_frame = tk.Frame(plot_window, relief=tk.SUNKEN, highlightbackground="green", highlightthickness=1, borderwidth=1, width=200, height=100)  # Create a visible frame with a specified size
    listbox_frame.grid(row=2, column=1, rowspan=6, padx=(0, 20))  

    frame_label = tk.Label(listbox_frame, text="Selection Beta")  
    frame_label.pack()  

    scrollbar = tk.Scrollbar(listbox_frame) 
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  

    listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE, yscrollcommand=scrollbar.set) 
    listbox.pack(side=tk.LEFT, fill=tk.BOTH)  
    scrollbar.config(command=listbox.yview) 

    listbox.insert(tk.END, 'NULL')
    listbox.insert(tk.END, 'All')  
    for beta in beta_values:
        listbox.insert(tk.END, f'beta={beta}')  

    figure_index_label = tk.Label(plot_window, text="No figures yet.")
    figure_index_label.grid(row=1, column=2) 
    fig = plt.figure(figsize=(8,6)) 
    canvas = FigureCanvasTkAgg(fig, master=plot_window)  

    canvas_widget = canvas.get_tk_widget()
    canvas_widget.grid(row=2, column=2, rowspan=5)  
    canvas_widget.configure(width=800, height=600)  

    def check_Nc_state():
        if show_Nc.get():
            select_button_Nc.config(state="normal")
        else:
            select_button_Nc.config(state="disabled")
    
    
    show_Nc = tk.IntVar()
    chk_show_Nc = tk.Checkbutton(plot_window, text="Show Nc plot", variable=show_Nc, command=check_Nc_state)
    chk_show_Nc.grid(row=3, column=0)


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
        global ax1
        global current_figure_index
        selected_betas = [listbox.get(i) for i in listbox.curselection()]  
        
        #1
        if not selected_betas:
            messagebox.showwarning("Warning", "No beta values are selected!")  
            return
        
        #2
        if 'NULL' in selected_betas:
            fig, ax1= plt.subplots(figsize=(8,6))
            ax1.set_xlabel('Wc')
            ax1.set_ylabel('PR', color='b')
            
            #3
            if show_Nc.get():
                plot_Nc(ax1)
            selected_betas = beta_values  
        #4
        else:
            if 'All' in selected_betas:
                selected_betas = beta_values
            else:
                selected_betas = [int(beta[5:]) for beta in selected_betas]  
        
            fig, ax1 = plt.subplots(figsize=(8,6))  

            for beta, Wc, PR, Nc in zip(beta_values, Wc_values, PR_values, Nc_values):
                if beta in selected_betas:  
                    ax1.plot(Wc, PR, label=f'beta={beta}')
        
            ax1.set_xlabel('Wc')
            ax1.set_ylabel('PR', color='g')
            ax1.legend(loc="best", fontsize="x-small")

            plt.title('Wc-PR graphs for different Beta values')

            if show_Nc.get():
                plot_Nc(ax1)

        figures.append(fig) 
        current_figure_index = len(figures) - 1  

        canvas.figure = fig
        canvas.draw()
        update_buttons_and_label()

    plot_button = tk.Button(plot_window, text="Plot Selected Graphs", command=plot_selected)
    plot_button.grid(row=7, column=1)  # Grid it below the listbox

    select_button_Nc = tk.Button(plot_window, text="Select the Nc value", command=Nc_selection_window)
    select_button_Nc.grid(row=3, column=1)

    # init check Nc
    check_Nc_state()

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
        if current_figure_index < len(figures) - 1:  # If the current figure is not the last one
            current_figure_index += 1  # Go to the next figure
            canvas.figure = figures[current_figure_index]  # Update the canvas
            canvas.draw()
        update_buttons_and_label()

    next_button = tk.Button(plot_window, text="Next Figure >>", command=show_next_figure, state="disabled")
    next_button.grid(row=8, column=2)  # Grid it to the right side

    def display_readme():
        messagebox.showinfo("Read Me", "1. Check the Nc plot checkbox at first if you want to plot Nc. \n2. If you select NULL and ALL for beta, please deselect others.")  # Display some message

    read_me_button = tk.Button(plot_window, text="Read Me", command=display_readme)
    read_me_button.grid(row=0, column=0)  # Grid it below the plot button

    update_buttons_and_label()
