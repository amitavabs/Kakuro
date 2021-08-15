#Kakuro_config Ver 1.1 amitavabs@yahoo.com
#Intial configuration program for Kakuro solving
#Edit this program (see comments below) if Kakuro input data mode needs to be changed

FILL_FILES = ["diag2019.png","up2019.png","dn2019.png","full2019.png"]

INPUT_SCREEN = 0

INPUT_FILE = 1
INPUT_FILE_NAME = "kakuro_data.txt"
#Sample data example :record number, columns, rows, entries data(gridwise)-exclude#! 
#1,4,4,0,0,0,6,0,6,0,5,6,0,,,,,,,6,0,,,,,,,5,0,,,,,0,0,
INPUT_FILE_REC = 1

INPUT_PROGRAM = 2

#Change comment here if you want to change input mode
#if input mode "INPUT_FILE" is used, generate data file "kakuro_data.txt"
INPUT_MODE = INPUT_SCREEN
#INPUT_MODE = INPUT_FILE
#INPUT_MODE = INPUT_PROGRAM

global input_program_data
#Wiki example of Kakuro 
input_program_data = [ 0, 0, 0, 0, 0, 0, 0, 0,  \
                       0,23,30, 0, 0,27,12,16,  \
                      16,"","", 0,24,"","","",  \
                       0,"","", 0,17,"","","",  \
                      17,"","",29,"","","","",  \
                       0,"","",15,"","","","",  \
                      35,"","","","","", 0, 0,  \
                       0,"","","","","",12, 0,  \
                       0, 7,"","", 8,"","", 0,  \
                       0, 0,"","", 7,"","", 7,  \
                       0, 0,16,"","","","","",  \
                       0,11,10,"","","","","",  \
                      21,"","","","", 5,"","",  \
                       0,"","","","", 0,"","",  \
                       6,"","","", 0, 3,"","",  \
                       0,"","","", 0, 0,"",""   ]


#Holds mapping values of Kakuro entries and equation varables
#Also used to determine grids having common row and column
global t
t = []

# Total number of variables to solve
global VARIABLE_COUNT
VARIABLE_COUNT = 0

#linear equation derived from Kakuro entries
#list format: entry number, entry constant(sum) and grid variable list
global t_equations
t_equations = []

#Intermediate processing equations derived from t_equations
global t_eqn
t_eqn = []

#Possible values of variables in grid generated from t_eqn
global t_values
t_values = []

#Stack of possible values being iteratively verified from t_equations
global t_stack
t_stack = []

# Set of all possible values grid may contain
global s_all
s_all = {1,2,3,4,5,6,7,8,9}

#Check for valid sum-in-n grid
# A 2 grid has maxmium 17=(9+8) and minimun 3=(2+1) sum
# A n grid has maximun n(19-n)/2 and minmum n(n+1)/2 sum
#Lookup list of above condition created for validation. 
global t_range
t_range = []
def set_t_range() :
    for i in range(10) :
        mmax = int(i * (19 - i) / 2)
        mmin = int(i * (i + 1) / 2)
        t_range_rec = []
        t_range_rec.append(mmax)
        t_range_rec.append(mmin)
        t_range.append(t_range_rec)
    return


#Kakuro populate modes
#0- User Input 1- Stored flat file  2 - Checkpoint start
def populate_kaku(labels,entries,images):
    global input_program_data
    
    update_mode = INPUT_MODE
    
    if   update_mode ==  INPUT_SCREEN  : return
    elif update_mode ==  INPUT_FILE    : populate_kaku_file(labels,entries,images)
    elif update_mode ==  INPUT_PROGRAM :
        K_ROW = 8
        K_COL = 8
        mcount = 0
        for j in range (K_ROW) :
            for k in range (K_COL) :
                m = j* K_COL*2 + k*2
                entries[m].insert(0,input_program_data[mcount])
                if input_program_data[mcount] == 0 :
                    labels[m].config(image=images[1])
                    labels[m+1].config(image=images[1])
                    entries[m].configure(bg = '#707070')
                else :     
                    entries[m].configure(bg = 'white')
                mcount += 1
                
            for k in range (K_COL) :
                m = j* K_COL*2 + k*2 + 1
                entries[m].insert(0,input_program_data[mcount])
                if input_program_data[mcount] == 0 :
                    if input_program_data[mcount - K_ROW] == 0 :
                        labels[m].config(image=images[3])
                        labels[m-1].config(image=images[3])
                    else :
                        labels[m].config(image=images[2])
                        labels[m-1].config(image=images[2])
                    entries[m].configure(bg = '#707070')
                else :      
                    entries[m].configure(bg = 'white')
                mcount += 1

    return
 
def populate_kaku_row_col():
    global K_ROW
    global K_COL
    mrec_use = INPUT_FILE_REC
    f = open(INPUT_FILE_NAME, "r")
    for mdata in f: 
        mfield = mdata.split(",")
        mrec = int(mfield[0][:])
        if mrec_use == mrec :
            K_ROW = int(mfield[1][:])
            K_COL = int(mfield[2][:])
    f.close
    return


def populate_kaku_file(labels,entries,images):
    global entry_tab_list
    
    mrec_use = INPUT_FILE_REC
    f = open(INPUT_FILE_NAME, "r")
    for mdata in f: 
        mfield = mdata.split(",")
        mrec = int(mfield[0][:])
        if mrec_use == mrec :
            K_COL = int(mfield[1][:])
            K_ROW = int(mfield[2][:])
            melements = K_COL * K_ROW * 2
            for i in range(melements) :
                j = mfield[i+3][:]
                #Force top entry row and left entry column as full bg black 
                #with entry value as "" overiding file values 
                if ( i%2 == 0 ) and ( i < K_COL * 2) :
                    entries[i].insert(0,"")
                elif (i % (K_COL*2) == 1) :
                    entries[i].insert(0,"")
                else :
                    entries[i].insert(0,j)
                    if (j == "0") :
                        update_entries(i,j,K_ROW,K_COL,labels,entries,images)
            break
    f.close
    return


#Display correct backgound of grid based on entry input value
def update_entries(i,input,K_ROW,K_COL,labels,entries,images):
    
    if input == "0" : entries[i].configure(bg = '#707070')
    else : entries[i].configure(bg = 'white')
        
    #Process one below top row
    for j in range(0,K_COL*2,2) :
        if i == j + 1 :
            if input == "0" :
                labels[i].config(image=images[3])
                labels[j].config(image=images[3])
            else :
                labels[i].config(image=images[1])
                labels[j].config(image=images[1])
            return
        
    #Process one beside leftmost column
    for j in range(K_ROW):
        k = j * K_COL * 2   
        if i == k  :
            if input == "0" :
                labels[i].config(image=images[3])
                labels[i+1].config(image=images[3])
            else :
                labels[i].config(image=images[2])
                labels[i+1].config(image=images[2])
            return

    #Process rest of entries
    if not bool(i%2) : j = i + 1
    else : j = i - 1
    
    if (entries[j].get() == "0") :
        if (input == "0" ) : 
            labels[i].config(image=images[3])
            labels[j].config(image=images[3])
        else :
            if not bool(i%2) :
                labels[i].config(image=images[2])
                labels[j].config(image=images[2])
            else :
                labels[i].config(image=images[1])
                labels[j].config(image=images[1])
    else :    
        if (input == "0" ) : 
            if not bool(i%2) :
                labels[i].config(image=images[1])
                labels[j].config(image=images[1])
            else :
                labels[i].config(image=images[2])
                labels[j].config(image=images[2])
        else :
            labels[i].config(image=images[0])
            labels[j].config(image=images[0])

    return
