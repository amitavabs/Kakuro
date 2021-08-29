#kakuro_main Ver 1.2 amitavabs@yahoo.com
#kakuro_main is the front GUI for Kakuro input data
#1st screen accepts  rows and columns count of Kakuro and 2nd screen actual data

import tkinter as tk

from kakuro_config import *
from kakuro_solver import *

global K_ROW
global K_COL
global labels
global entries
global buttons

K_ROW = 0
K_COL = 0
frame = []
frame_arr = []
buttons =[]

#Validate initial row column screen entry
def reg_data_chk1(input):
    #exclude leading zeros
    if (len(input) == 2 and input[0] == "0") : return False
    
    if (input.isdigit() and int(input) <= 20 )  \
          or input is "": return True
    return False


#Validate Kakuro screen entry
def reg_data_chk2(input):
    global K_ROW
    global K_COL
    global labels
    global entries
    global images
    #exclude leading zeros
    if (len(input) == 2 and input[0] == "0") : return False
    
    #exclude non numeric  and max sum 45=(1+2...+9)  
    if (input.isdigit() and int(input) <= 45 )  \
          or input is "":
        if (INPUT_MODE == INPUT_SCREEN) :
            i = (entries.index(root.focus_get()))
            update_entries(i, input, K_ROW, K_COL, labels, entries, images)
        return True
       
    return False


def solver_start():
    global K_ROW
    global K_COL
    global labels
    global entries
    global images
    global buttons
    
    #Correct entry of only half filled in grid area, by  blackening it(value 0)
    #Exclude top row and left column  as only half of grid is editable
    for i in range(1,K_COL):
        for j in range (1,K_ROW):
            m =  (i * K_ROW +j) * 2
            n = m + 1
            p = entries[m].get()
            q = entries[n].get()
            
            if (p == "" and q != "") :
                entries[m].insert(0,"0")
                update_entries(m,"0",K_ROW,K_COL,labels,entries,images)               
            elif (p != "" and q == "") :
                entries[n].insert(0,"0")
                update_entries(n,"0",K_ROW,K_COL,labels,entries,images)               
    
    i = kaku_solver_engine(K_ROW, K_COL, frame, frame_arr, entries)
    
    if i == 1 :  buttons[0].config(state = 'disabled')
    print("End of Solve")
    
    return


# Kakuro entry screen
##############################
#Top row and left col of entry are left blank("") instead of "0" to fully blacken entry
#update_entries() is not used for top row and left col, as disp_kakuro() handles it
def disp_kakuro() :
    global K_ROW
    global K_COL
    global frame_arr
    global labels
    global entries
    global buttons
    global images
    global INPUT_MODE
    global INPUT_SCREEN

    #Continue batch data validation of number of rows and cols  from screen
    if (INPUT_MODE == INPUT_SCREEN) :
        #Validate entries to get integer between 3 and 20 inclusive
        i = e11.get()
        if not i.isdigit() or  int(i)  < 3 :
            e11.focus_set()
            return
        j = e12.get()
        if not j.isdigit() or int(j)  < 3 :
            e12.focus_set()
            return
        
        K_ROW = int(i)
        K_COL = int(j)
        frame_row_cols.destroy()

    #sum-in-grid validation lookup 
    set_t_range()

    #list of top row and left column
    #Top row entries list
    row_axis = []
    for i in range(0,K_COL*2,2): row_axis.append(i)
    #Left column entries list
    col_axis = []
    for i in range(K_ROW): col_axis.append(i * K_COL * 2 + 1)

    #Validation container for entries 
    md = [tk.StringVar()] * K_ROW * K_COL * 2
    #Seperate address place
    for i in range(K_ROW * K_COL * 2) : md[i] = str(i)
    
    frame_but = tk.Frame(root)
    frame_but.config(bg = '#F2B33D', bd = 10, )
    frame_but.grid( row=1,column=0, padx=2, pady=2)

    frame_arr = []
    mcount = 0
    for i in range(K_ROW):
        for j in range(K_COL):
            frame_element =  tk.Frame(frame)       
            frame_element.grid( row=i,column=j,padx=1, pady=1)
            frame_arr.append(frame_element)

    images = []
    for i in  FILL_FILES  :          
        img  = tk.PhotoImage(file=i)
        images.append(img)
    labels = []
    entries = []
    buttons = []
    mcount = 0
    mi = 0
    mj = 0

    for i in range(K_ROW):
        for j in range(K_COL):
            k = i * K_COL + j
            for m in [ [0,0,1,0] ,[1,1,0,1] ] :
                l1= tk.Label(frame_arr[k], image=images[0],
                             highlightthickness=0,bd = 0,)
                l1.grid( column = m[0], row = m[1])
                labels.append(l1)
         
                e1 = tk.Entry(frame_arr[k], width=2,textvariable=md[mcount], \
                             highlightthickness=0,bd = 0,cursor="dotbox")
                e1.grid(  column = m[2], row = m[3] )
                e1.config(validate ="key", validatecommand =(data_chk2, '%P'))
                e1.delete(0,"end")
                e1.insert(0,"")
                entries.append(e1)
                mcount += 1

    for i in row_axis:
        labels[i].config(image=images[1])
        labels[i+1].config(image=images[1])

    for i in col_axis:
        labels[i-1].config(image=images[2])
        labels[i].config(image=images[2])
    
    for i in range(2) : labels[i].config(image=images[3])

    for i in row_axis: entries[i].configure(state='disabled', disabledbackground = "black")
    for i in col_axis: entries[i].configure(state='disabled', disabledbackground = "black")

    msg_label = tk.Label(frame_but, highlightthickness=0,bd = 0,
                         anchor = "center", padx=50, pady=10,bg = '#F2B33D',
                         text = "Use 0 to barr an entry" )
    msg_label.grid( column = 0, row = 0, columnspan=2)


    button1 = tk.Button(frame_but, text='Solve',command= solver_start, padx=10, pady=10)
    button1.grid(row=1, column=0, pady=0, padx=50,ipadx=5)
    button1.config(font=('helvetica', 14))
    buttons.append(button1)

    button2 = tk.Button(frame_but, text='Quit', command=root.destroy,padx=10, pady=10)
    button2.grid(row=1, column=1, pady=0, padx=50,ipadx=10)
    button2.config(font=('helvetica', 14))
    buttons.append(button2)

    populate_kaku(labels,entries,images)
    #Provision for user editing of data if populate mode was differnt, example through data file.
    INPUT_MODE = INPUT_SCREEN
    
    return


root = tk.Tk()
#root.geometry("+500+150")
root.config(bg = '#F2B33D')
root.option_add("*font", "lucida 12")
root.title("KAKURO")

#register background update handlers that are polled while the application is idle.
data_chk1 = root.register(reg_data_chk1)
data_chk2 = root.register(reg_data_chk2)

frame = tk.Frame(root)
frame.config(bg = '#F2B33D', bd = 10, relief = tk.RIDGE)
frame.grid( row=0,column=0)

frame_row_cols =  tk.Frame(frame)
frame_row_cols.config(bg = '#F2B33D',)
frame_row_cols.grid( row=0,column=0)
frame_row_cols.option_add("*font", "lucida 12")

#Request number of row and columns if user provides data through screen
#Max 20 rows can fit in a FHD screen. Program logic has no limitation
if (INPUT_MODE == INPUT_SCREEN) :
    label11 = tk.Label(frame_row_cols,anchor = "w", padx=15, pady=30,bg = '#F2B33D',
                       text = "Enter number of rows : range 3 to 20    " )
    label11.grid( column = 0, row = 0,)

    label12 = tk.Label(frame_row_cols,anchor = "w", padx=15, pady=30,bg = '#F2B33D',
                       text = "Enter number of columns : range 3 to 20 " )
    label12.grid( column = 0, row = 1,)

    me11 = tk.StringVar()
    me12 = tk.StringVar()
    e11 = tk.Entry(frame_row_cols, width=2,textvariable=me11,) 
    e11.grid( column = 1, row = 0 )
    e11.config(validate ="key", validatecommand =(data_chk1, '%P'))
    e12 = tk.Entry(frame_row_cols, width=2,textvariable=me12,) 
    e12.grid( column = 1, row = 1 )
    e12.config(validate ="key", validatecommand =(data_chk1, '%P'))

    button11 = tk.Button(frame_row_cols, text='Proceed',command=disp_kakuro, padx=10, pady=10)
    button11.grid(row=2, column=0, pady=10, padx=50,ipadx=5)
    button11.config(font=('helvetica', 14))

    button12 = tk.Button(frame_row_cols, text='Quit', command=root.destroy,padx=10, pady=10)
    button12.grid(row=2, column=1, pady=10, padx=50,ipadx=10)
    button12.config(font=('helvetica', 14))

#Get number of rows and columns from file if input mode as file selected instead of screen
elif (INPUT_MODE == INPUT_FILE) :
    mrec_use = INPUT_FILE_REC
    f = open(INPUT_FILE_NAME, "r")
    for mdata in f: 
        mfield = mdata.split(",")
        mrec = int(mfield[0][:])
        if mrec_use == mrec :
             K_COL = int(mfield[1][:])
             K_ROW = int(mfield[2][:])
             break
    f.close
    disp_kakuro()
    
# Set up values for hardcoded program example    
else :
    K_ROW = 8
    K_COL = 8
    disp_kakuro()   
    
#revert back to default screen entry if earlier input was file or  program mode
INPUT_MODE == INPUT_SCREEN
#set focus on an updatable item so that focus_get is valid
for i in range(K_ROW * K_COL) :
    if entries[i].get() == "" :
        entries[i].focus_set()
        break
        
    
root.mainloop()
