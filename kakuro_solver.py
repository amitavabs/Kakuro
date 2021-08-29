#kakuro_solver Ver 1.2 amitavabs@yahoo.com
#kakuro_solver_engine works by iteratively checking for valid values 
import tkinter as tk
from kakuro_config import  *

'''
lists used by postprocessor
t[rows][cols]= [variable] phyical kakuro grid representation with variable, static table
t_range index [[maxsum, minsum] , ...] index is number of variables, static table
t_values  [[variable, [varlist values],entry_id] , ...], 0 index stores number of variables solved
Holds checkpoint value of results of postprocessor
t_equations  [[entry_id, sum, [varlist]] , ...]  Equations to solve in kakuro, static table
t_eqn  [[entry_id, sum, [varlist]] , ...]  solved values substituted in  t_equations
Intial soved/allowable value list

lists used by iterative process
t_stack [[[varlist values],len(varlist values), current value iterated] , ...], 0 index special entry, holds stack pointer
Variables mapping changed so that index is variable number. Sorted copy of t_values solved result
t_stack_equations  [[[varlist], sum] , ...] index is equation number, static table
Different  copy of t_equation using  variables remapped on t_stack
t_equation_solve_order [[varlist- processing order from t_stack in t_stack_equations ], ...] index is equation number,static table
t_var_equation map[ [equation number used], ...] index is variable number, static table
'''

#Intial solution done by  elimination followed by iterative process
#K_ROW and K_COL computed in kakuro_main module and need to passed as pgm args
def kaku_solver_engine(K_ROW, K_COL, frame, frame_arr, entries):
    #0 - Incompelete processing 
    #1 - Solution complete
    #2 - Invalid Kakuro data
    global t
    global t_equations
    global t_eqn
    global t_values
    global t_stack
    global VARIABLE_COUNT

    #Holds mapping values of Kakuro entries and equation variables
    #Also used to determine grids having common row and column
    t = [[0 for i in range(K_COL)] for j in range(K_ROW)]

    #linear equation derived from Kakuro entries
    #Format: Entry cell Id, Entry cell value, Grid variables 
    t_equations = []
    
    #Validate Kakuro entries and generate equations 
    if ( kaku_solver_validate_rows(K_ROW, K_COL, entries) ) :
        return 2
    if ( kaku_solver_validate_cols(K_ROW, K_COL, entries) ) :
        return 2
    if ( kaku_solver_validate_sum(K_ROW, K_COL, entries) ) :
        return 2

    mvarcount = 0
    for i in range(K_ROW):
        for j in range(K_COL):
            if mvarcount < t[i][j] : mvarcount = t[i][j]
    VARIABLE_COUNT = mvarcount      

    t_eqn = []
    #t_eqn = t_equations.copy() will be a shallow copy without the list
    for i in t_equations :
        mlist = []
        mlist.extend(i[2])
        t_eqn.append([i[0],i[1],mlist])

    t_values = []
    #Dummy populate 0 index to allow  index n  point to nth variable 
    for i in range(VARIABLE_COUNT + 1) :  t_values.append([i, s_all, 0])
    
    i = kaku_solver_solve_equations() 
    if ( i == 1) or ( i == 2) : return i

    i = kaku_solver_iterate()
    
    s_txt_solution(K_ROW, K_COL)
    if i == 1 : s_graphic_solution(K_ROW, K_COL, frame, frame_arr)
    
    return i



#Verify and extract equations from rows
def kaku_solver_validate_rows(K_ROW, K_COL, entries) :
    global t
    global t_equations

    #End of row entries cannot have a value
    for i in range(K_ROW):
        j = (i + 1) * K_COL * 2 - 2
        k = entries[j].get()
        if k != "0" and k != "" :
            entries[j].configure(bg = 'red')
            print ("Error: End of row entries cannot have a value")
            return True
        
    mvarcount = 1
    for i in range(1,K_ROW):
        mfound = False
        mvar_val = []
        mvar_list =[]
        for j in range (K_COL):
            m = (i * K_COL + j) * 2
            k = entries[m].get()

            if not mfound and k == "" :
                entries[m].configure(bg = 'red')
                print ("Error: Empty row Grid without value")
                return True
            
            #End of entries midway, save equation    
            if mfound and k == '0' :
                mvar_val.append(mvar_list)
                t_equations.append(mvar_val)
                mfound = False
                mvar_val = []
                mvar_list =[]
                continue
                       
            if  (k != "") and (k != '0') :
                #Save equation from previous buffer if more then one equation in a row
                if (mvar_list) :
                    mvar_val.append(mvar_list)
                    t_equations.append(mvar_val)
                    mvar_val = []
                    mvar_list =[]
                mfound = True
                mvar_val.append(m)
                mvar_val.append(int(k))
                mvar_list =[]
                continue

            #Empty Grid, processing continues in row
            if mfound  and  (k == "") :
                t[i][j] = mvarcount
                mvar_list.append(mvarcount)
                mvarcount += 1
                #save current equation if end of grid in row is reached
                if    j+1 ==  K_COL :
                    mvar_val.append(mvar_list)
                    t_equations.append(mvar_val)

    return False


#Copy of above row processing, done columnwise
#For common row and column grids, variable count does not increase
def kaku_solver_validate_cols(K_ROW, K_COL, entries) :
    global t
    global t_equations

    #End of column entries cannot have a value
    for i in range(K_COL):
        j = 2 * K_COL * (K_ROW - 1) + i * 2 + 1
        k = entries[j].get()
        if k != "0" and k != "" :
            msg_label = tk.Label(text = "Error: End of column entries cannot have a value" )
            entries[j].configure(bg = 'red')
            print ("Error: End of column entries cannot have a value")
            return True

    #Extract last variable got from row processing
    mvarcount = 1
    for i in range(K_ROW):
        for j in range(K_COL):
            if mvarcount < t[i][j] : mvarcount = t[i][j]
    mvarcount += 1
    
    for i in range(1,K_COL):
        mfound = False
        mvar_val = []
        mvar_list =[]
        for j in range (K_ROW):
            m = (i + j * K_COL)*2 + 1
            k = entries[m].get()

            if not mfound and k == "" :
                entries[m].configure(bg = 'red')
                print ("Error: Empty column Grid without value")
                return True

            #End of entries midway, save equation    
            if mfound and k == '0' :
                mvar_val.append(mvar_list)
                t_equations.append(mvar_val)
                mfound = False
                mvar_val = []
                mvar_list =[]
                continue
                       
            if  (k != "") and (k != '0') :
               #Save equation from previous buffer if more then one equation in a row
                if (mvar_list) :
                    mvar_val.append(mvar_list)
                    t_equations.append(mvar_val)
                    mvar_val = []
                    mvar_list =[]
                mfound = True
                mvar_val.append(m)
                mvar_val.append(int(k))
                mvar_list =[]
                continue

            #Empty Grid, processing continues in column, with common row and column check 
            if mfound  and  (k == "") :
                n = t[j][i]
                if  n == 0  :            
                    t[j][i] = mvarcount
                    mvar_list.append(mvarcount)
                    mvarcount += 1
                else :
                    mvar_list.append(n)
                    
                #Save current equation if end of grid in column is reached
                if (j + 1) ==  K_ROW :
                    mvar_val.append(mvar_list)
                    t_equations.append(mvar_val)

    return False


# Validate entry sum based on number of empty grids.
# t_range contains allowable sum range for given empty grids
def kaku_solver_validate_sum(K_ROW, K_COL, entries) :
    global t_range
    global t_equations
    
    for i in t_equations :
        j = i[1]
        k = len(i[2])
        #Validation of entries without any grid
        if k == 0 :
            entries[i[0]].configure(bg = 'red')
            print ("Error: Entry present without any grid")
            return True
        
        # Allow entry with with single grid, Solver matches the value
        
        #Validation of entry value within range based on grids covered
        elif ( j > t_range[k][0] ) or ( j < t_range[k][1] ):
            entries[i[0]].configure(bg = 'red')
            print ("Error: Invalid entry, Sum cannot be acheived")
            return True
       
    return False    


def kaku_solver_solve_equations() :
    global t_eqn
    global t_values
    
    mold_solve_count = -1

    while ( mold_solve_count != t_values[0][0] ) :
        mold_solve_count = t_values[0][0]
        i = kaku_solver_allowable_values()
        i =  kaku_solver_validate_variables()
        if ( i == 1) or ( i == 2) : return i
        if (kaku_solver_update_eqn(VARIABLE_COUNT, t_eqn, t_values)):
            return 2
     
    return 0


def kaku_solver_allowable_values() :
# list containing allowable values of variable is created.
# Format :  Allowable variable Id, value set, entry cell id 
# Single grid with entry is allowed and processed first
    global t_range
    global t_values
    global t_equations
    global t_stack
  
    for i in t_eqn :
        mentry_id = i[0]
        msum = i[1]
        mvarlist = i[2]
        if not mvarlist : continue
        mlen = len(mvarlist)
        mset = set()
       
        if mlen == 1 :
            mset =  set(list([msum]))   
        else :
            # Maximum value of a grid in n cell grid is
            # entry sum minus minimum sum of n-1 grids.
            maxval = msum - t_range[mlen-1][1]
            if maxval > 9 : maxval = 9
            # Minimum value of a grid in n cell grid is
            # entry sum minus maximum sum of n-1 grids.
            minval = msum - t_range[mlen-1][0]
            if minval < 1 : minval = 1
            mset = set(list(range(minval, maxval + 1,)))
    
        for j in mvarlist :
            if (i[0] == 79) :
                if t_stack :
                #if t_stack[0][0] = 0
                    pass
            #Use entry id of more restrictive value
            if len(mset) < len(t_values[j][1]) :
                t_values[j][2] = mentry_id
            mintset = set()
            mintset = mset.intersection(t_values[j][1])
            t_values[j][1] = mintset
 
    return False


def kaku_solver_validate_variables() :
    global t_values
    global t_equations
    global VARIABLE_COUNT
    
    msolved_count = 0
    for i in range(1, VARIABLE_COUNT + 1) :
        mvalid_values = t_values[i][1]
        if not mvalid_values : return 2
        if len(mvalid_values) == 1 : msolved_count += 1
         
    # t_values has dummy index 0 value. t_values[0][0] stores variables solved
    t_values[0][0] =  msolved_count
    
    #Check for  unique values of variables in a equation
    for i in t_equations :
        mvarlist = i[2]
        if len(mvarlist) > 1 :
            mvarvalues = []
            for j in mvarlist :
                if len(t_values[j][1]) == 1 :
                    mvarvalues.append(t_values[j][0])
            if len(set(mvarvalues)) <  len(mvarvalues) : return 2
    
    # Return solved in the end after all error verification
    if msolved_count == VARIABLE_COUNT : return 1
        
    return 0 


#Updates equation with variable values that are found/given in t_values
def  kaku_solver_update_eqn(VARIABLE_COUNT, t_eqn, t_values) :

    for i in range (1, VARIABLE_COUNT +1) :
        if len(t_values[i][1]) == 1 :
            mvarval1 = list(t_values[i][1])
            mvarval2 = mvarval1[0]
            for ndx, j in enumerate(t_eqn) :
                if not j[2] : continue
                if  i in j[2] :
                    t_eqn[ndx][1] = t_eqn[ndx][1] - mvarval2
                    t_eqn[ndx][2].remove(i)
                    #Equations fully solved will contain no variable or value
                    #Other equations of one or more variab;es will have sum > 0
                    if not t_eqn[ndx][2] :
                        if t_eqn[ndx][1] < 0 :  return True
                    else :
                        if t_eqn[ndx][1] < 1 :  return True
    return False


#Valid values in t_stack used for iterative processing
# Solved equation(t_stack_eqn ) maintains variablewise equation solved iteratively
def kaku_solver_iterate():
    #0 - Incompelete processing 
    #1 - Solution complete
    #2 - Invalid Kakuro data
    
    global t_values
    global t_equations
    global t_stack
    global t_stack_equations
    global t_var_equation_map
    global VARIABLE_COUNT

    #Edit ndx 0 to  get top of sort order. 
    t_values[0] = [ 0 ,{0} ,0 ]
    #Entry cell Id in sort key used to keep variables in a equation nearby
    t_values.sort(key = lambda i: (len(i[1]), i[2]))

    t_stack = []
    mlist = []
    for mndx, i in enumerate(t_values) :
        mlist = list(i[1])
        mlist.sort()
        t_stack.append ([ mlist,len(mlist), 0])
        t_values[mndx][1] = mlist
    
    for mndx, mlist in enumerate(t_stack) :
        if len(mlist[0]) != 1 : break
        else : t_stack[mndx][2] = t_stack[mndx][0][0]
    #Preprocessor stage completes solution
    if mndx == VARIABLE_COUNT : return 1
    t_stack[0][0] = mndx -1
    
    t_stack_equations = []
    for i in t_equations :
        mlist = []
        for j in i[2] :
            for mndx, k in enumerate(t_values) :
                if j == k[0] : break
            mlist.append(mndx)
        #arrange as per t_stack
        mlist.sort()
        t_stack_equations.append([ mlist, i[1],len(mlist) ])
                                   
    t_var_equation_map = []
    for mndx1, i in enumerate(t_stack) :
        if mndx1 == 0 :
            t_var_equation_map.append([0]) #dummy value
            continue
        mlist = []
        for mndx2, j in enumerate(t_stack_equations) :
           if mndx1 in j[0] :
                mlist.append(mndx2)
        t_var_equation_map.append(mlist)
    
    i = 0
    while ( i != 1 ) :
        
        if (i == 0) :
            if t_stack[0][0] == VARIABLE_COUNT :
                i = kaku_solver_solved()
                if i == 1 : return 1
                else : continue
            t_stack[0][0] += 1
            mpointer = t_stack[0][0]
            t_stack[mpointer][2] = t_stack[mpointer][0][0]
            i = kaku_solver_validate_stack_variables()
            continue
        
        if (i == 2) :
            mfound = False
            while not mfound :
                mpointer = t_stack[0][0]
                mval = t_stack[mpointer][2]
                mndx = t_stack[mpointer][0].index(mval)
                #Check if all possible values of variable used up
                if mndx == t_stack[mpointer][1] - 1 :
                    if mpointer == 1 :
                        print("Warning : Top of variable list reached")
                        return 2
                    t_stack[0][0] = mpointer -1
                    continue
                else :
                    mfound = True
                    t_stack[mpointer][2] = t_stack[mpointer][0][mndx + 1]
            #Restore Checkpoint      
            for j in range(mpointer + 1, VARIABLE_COUNT + 1) :
                t_stack[j][0] = t_values[j][1]
                t_stack[j][1] = len(t_stack[j][0])
                
            i = kaku_solver_validate_stack_variables()
            continue

    return i   


#Verifies a variable value of t_stack is valid in always two kakuro equations
#Assign more restrictive range of allowable values
def kaku_solver_validate_stack_variables() :
    global t_range
    global t_stack
    global t_stack_equations
    global t_var_equation_map
    global VARIABLE_COUNT
    
    mpointer = t_stack[0][0]
    if mpointer == 6 :
        pass
 
    for meqn in t_var_equation_map[mpointer]  : 
        #Checks variables values are unique
        #and computes ranges for unassigned variables
        msum = 0
        mlist = []
        mrangecompute = False
        for mndx, i in enumerate(t_stack_equations[meqn][0]) :
            if i <= mpointer :
                j = t_stack[i][2]
                if j in mlist : return 2
                else : mlist.append(j)
                msum = msum + j
                continue

            if not mrangecompute :
                mrangecompute = True
                msum = t_stack_equations[meqn][1] - msum
                if msum < 0 : return 2
                mvar_no = t_stack_equations[meqn][2] - mndx
                # single unassigned variable that is not unique
                if mvar_no == 1 :
                    if msum in mlist : return 2
                    if  msum < 1 or msum > 9 : return 2
                elif mvar_no == 2 :
                    if  msum < 2 or msum > 17 : return 2
                maxval = msum - t_range[mvar_no - 1][1]
                if maxval > 9 : maxval = 9
                minval = msum - t_range[mvar_no - 1][0]
                if minval < 1 : minval = 1
                mstacklist = list(range(minval, maxval + 1,))
                mstacklistlen = len(mstacklist)
                
            if mstacklistlen < t_stack[i][1] :
                 t_stack[i] = [mstacklist, mstacklistlen, 0 ]

    return 0


def kaku_solver_solved() :
    global t_stack
    global t_stack_equations
    for i in t_stack_equations :
        msum = 0
        for j in i[0] :
            msum = msum + t_stack[j][2]
        if msum != i[1] :
            return 2
    print("Kakuro solved")
    return 1
                

#Display solution in text mode in terminal window
def s_txt_solution(K_ROW, K_COL) :
    global t
    global t_values

    mcount = 1
    for i in range(K_ROW) :
        for j in range(K_COL) :
            if t[i][j] == 0 : print("X", end="|")
            else :
                for mndx, p in enumerate(t_values) :
                    if p[0] == mcount : break
                mval = t_stack[mndx][2]
                if mcount >  t_stack[0][0] : mval  = "?"         
                print(mval, end="|")
                mcount += 1
            if j == K_COL - 1 : print(" ")
    print("===========================")
    return            
            

#Display solution in graphic mode in Kakuro  screen
def s_graphic_solution(K_ROW, K_COL, frame, frame_arr) :
    global t
    global t_values   
   
    mcount = 1
    for i in range(K_ROW) :
        for j in range(K_COL) :
            if t[i][j] != 0 :
                for mndx, p in enumerate(t_values) :
                    if p[0] == mcount : break
                mval = t_stack[mndx][2]
                    
                if  mval == 0 : mvalstr = " ? "
                mvalstr = " " + str(mval) + " "
                k = i * K_ROW + j - mcount -1
                frame_arr[k].destroy
                frame_element =  tk.Frame(frame)       
                frame_element.grid( row=i ,column=j ,padx=1, pady=1)
                l1= tk.Label(frame_element, text=mvalstr, highlightthickness=0,bd = 0,)
                l1.config(font=('lucida', 24))
                l1.grid( column = j, row = i)
                mcount += 1
 
    return
