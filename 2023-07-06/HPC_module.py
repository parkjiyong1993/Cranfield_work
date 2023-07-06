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
    global beta_Nc
    global beta_values  

    filename = filedialog.askopenfilename(filetypes=[("Map files", "*.map")])  # Only .map files can be imported
    if filename:
        with open(filename, 'r') as f:
            data = f.read()

        vigv_blocks = re.findall(r'(VIGV\s+=\s+\d+\s+\{[^{}]*?(?:\{[^{}]*?(?:\{[^{}]*?\}[^{}]*?)*?\}[^{}]*?)*?\})', data, re.DOTALL)

        beta_Nc_Wc = []
        beta_Nc_PR = []
        beta_Nc = []

        # Iterate over each VIGV block
        for block in vigv_blocks:
            # Extract VIGV value
            vigv = re.search(r'VIGV\s+=\s+(\d+)', block).group(1)
            #print(block)
            
            beta_blocks = re.findall(r'(beta\s+=\s+\d+\s+\{[^{}]*?(?:\{[^{}]*?\}[^{}]*?)*?\})', block, re.DOTALL)
            
            for beta_block in beta_blocks:
                beta = re.search(r'beta\s+=\s+(\d+)', beta_block).group(1)
                nc = re.search(r'Nc\s+=\s+\{([^\}]*)\}', beta_block).group(1)
                wc = re.search(r'Wc\s+=\s+\{([^\}]*)\}', beta_block).group(1) if re.search(r'Wc\s+=\s+\{([^\}]*)\}', beta_block) else None
                pr = re.search(r'PR\s+=\s+\{([^\}]*)\}', beta_block).group(1) if re.search(r'PR\s+=\s+\{([^\}]*)\}', beta_block) else None
                
                if wc is not None:
                    beta_Nc_Wc.append((vigv, beta, nc, wc))
                
                if pr is not None:
                    beta_Nc_PR.append((vigv, beta, nc, pr))

                beta_Nc.append((vigv, beta, nc))

        beta_values = [int(beta) for _, beta, _, _ in beta_Nc_Wc]
        print("beta_Nc_Wc", beta_Nc_Wc)

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
    
    print("selected VIGV = ", selected_VIGV)

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
        plot_HPC_line_graph(selected_VIGV[0].get())  
        Selected_VIGV_value_label = tk.Label(plot_window, text="")
        Selected_VIGV_value_label.config(text='VIGV value : ' + str(selected_VIGV[0].get()))
        Selected_VIGV_value_label.grid(row=2, column=0)
        
    select_button = tk.Button(selection_window, text="Select", command=select_and_close)
    select_button.grid(row=7, column=1)

###
def Nc_selection_window():
    global beta_Nc
    global selected_Nc  # declare 
    selected_Nc = [tk.StringVar()] # init
    selected_Nc_value = sorted(set(float(val) for _, _, Nc in beta_Nc for val in Nc.split(', ')))
    
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
        
        #selected_Nc[0].set(listbox.get(listbox.curselection()))
        selection_Nc_window.destroy()

    # Nc select window, select button
    select_button = tk.Button(selection_Nc_window, text="Select", command=select_and_close)
    select_button.grid(row=7, column=1)

def plot_Nc(ax1, selected_VIGV_value):
    global selected_Nc
    global current_figure_index
    global canvas
    global beta_Nc_Wc
    global beta_Nc_PR

    filtered_beta_Nc_Wc = [item for item in beta_Nc_Wc if (item[0]) == selected_VIGV_value]
    filtered_beta_Nc_PR = [item for item in beta_Nc_PR if (item[0]) == selected_VIGV_value]
    
    Wc_values = [[float(val) for val in Wc.split(', ') if val] for _, _, _, Wc in filtered_beta_Nc_Wc]
    PR_values = [[float(val) for val in PR.split(', ') if val] for _, _, _, PR in filtered_beta_Nc_PR]
    Nc_values = [[float(val) for val in Nc.split(', ') if val.strip()] for _, _, Nc, _ in filtered_beta_Nc_Wc]


    print("selected_VIGV_value : ", selected_VIGV_value)
    print("selected_Nc : ", selected_Nc)

    #print("Nc_values = ", Nc_values)

    selected_Nc_items = selected_Nc[0].get().split(", ")
    #print("selected_Nc_items = ", selected_Nc_items)
    print("Type of selected_Nc[0]:", type(selected_Nc[0]))
    print("selected_Nc[0].get():", selected_Nc[0].get())

    if 'All' in selected_Nc_items:
        selected_Nc_floats = sorted(set(float(val) for sublist in Nc_values for val in sublist))
    else:
        selected_Nc_floats = [float(val) for val in selected_Nc_items if val.strip()]

    #print("selected_Nc_floats = ", selected_Nc_floats)

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
###

plot_window = None

# Change the plot function to accept a selected_VIGV_value parameter
def plot_HPC_line_graph(selected_VIGV_value=None):  
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

    #(VIGV, beta, Nc, Wc) or (VIGV, beta, Nc, PR)
    Wc_values = [[float(val) for val in Wc.split(', ')] for VIGV, _, _, Wc in beta_Nc_Wc if VIGV == selected_VIGV_value]
    PR_values = [[float(val) for val in PR.split(', ')] for VIGV, _, _, PR in beta_Nc_PR if VIGV == selected_VIGV_value]
    Nc_values = [[float(val) for val in Nc.split(', ')] for VIGV, _, Nc, _ in beta_Nc_Wc if VIGV == selected_VIGV_value]

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

    listbox.insert(tk.END, 'NULL')
    listbox.insert(tk.END, 'All')  
    for beta in beta_values_for_selected_VIGV:
        listbox.insert(tk.END, f'beta={beta}')  

    figure_index_label = tk.Label(plot_window, text="No figures yet.")
    figure_index_label.grid(row=1, column=2)  
    fig = plt.figure(figsize=(8.5,6))
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
        selected_betas = [listbox.get(i) for i in listbox.curselection()]  # Get the selected beta values
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
                plot_Nc(ax1, selected_VIGV_value)
            selected_betas = beta_values_for_selected_VIGV
        #4
        else:
            if 'All' in selected_betas:
                selected_betas = beta_values_for_selected_VIGV
            else:
                selected_betas = [int(beta[5:]) for beta in selected_betas] 
        
            fig, ax1 = plt.subplots(figsize=(8,6))  

            for beta, Wc, PR, Nc in zip(beta_values_for_selected_VIGV, Wc_values, PR_values, Nc_values):
                if beta in selected_betas:  
                    plt.plot(Wc, PR, label=f'beta={beta}')

            ax1.set_xlabel('Wc')
            ax1.set_ylabel('PR', color='g')
            ax1.legend(loc="best", fontsize="x-small")

            plt.title('Wc-PR graph for different Beta values depending on VIGV')

            if show_Nc.get():
                plot_Nc(ax1, selected_VIGV_value)
        #plt.legend()

        figures.append(fig)  
        current_figure_index = len(figures) - 1  
        
        canvas.figure = fig
        canvas.draw()
        update_buttons_and_label()

    plot_button = tk.Button(plot_window, text="Plot Selected Graphs", command=plot_selected)
    plot_button.grid(row=7, column=1)  # Grid it below the listbox 

    select_button_VIGV = tk.Button(plot_window, text="Select the VIGV value", command=VIGV_selection_window)
    select_button_VIGV.grid(row=2, column=1)

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

    Guidance_label = tk.Label(plot_window, text="Please provide the VIGV, \n then select the beta")
    Guidance_label.grid(row=1, column=1)  

    update_buttons_and_label()
