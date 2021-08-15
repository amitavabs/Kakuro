#kakuro_solver Ver 1.1 amitavabs@yahoo.com
#kakuro_solver_engine works by iteratively checking for valid values 
import tkinter as tk
from kakuro_config import  *


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
    
    kaku_solver_intialise_t_eqn_t_values()
    
    i = kaku_solver_solve_equations() 
    if ( i == 1) or ( i == 2) : return i

    t_stack = []
    for i in t_values : t_stack.append ([ i[0], list(i[1]), list(i[1])[0] ])
    #Edit ndx 0 to  get top of sort order. t_stack[0][0] holds pointer to stack
    t_stack[0] = [ 0 ,[0] ,0 ]
    #Entry cell Id in sort key used to keep variables in a equation nearby
    t_stack.sort(key = lambda i: (len(i[1]), i[2]))
    for mndx, mlist in enumerate(t_stack) :
        if len(mlist[1]) != 1 : break
    t_stack[0][0] = mndx -1
  
    i = kaku_solver_iterate()
    
    s_txt_solution(K_ROW, K_COL)
    if i == 1 : s_graphic_solution(K_ROW, K_COL, frame, frame_arr)

   
    return i


#Intialise with copy of equations and list to hold allowable variable values
def kaku_solver_intialise_t_eqn_t_values() :
    global t_equations
    global t_eqn
    global t_values
    global VARIABLE_COUNT
    global s_all

    t_eqn = []
    #t_eqn = t_equations.copy() will be a shallow copy without the list
    for i in t_equations :
        mlist = []
        mlist.extend(i[2])
        t_eqn.append([i[0],i[1],mlist])

    t_values = []
    #Dummy populate 0 index to allow  index n  point to nth variable 
    for i in range(VARIABLE_COUNT + 1) :  t_values.append([i, s_all, 0])

    return


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


#Last processed valid values in t_values used for iterative processing
# Variable value, combination in stack is added to equation to solve for validity 
def kaku_solver_iterate():
    #0 - Incompelete processing 
    #1 - Solution complete
    #2 - Invalid Kakuro data

    global t_eqn
    global t_stack
    global VARIABLE_COUNT
    
    #Previously computed values ( t_eqn and t_values) initally used
    i = 0
    mstackempty = False
    #mdbg = 0
    while ((i== 0) or (i == 2)) and not mstackempty :
        if i == 0 :
            if t_stack[0][0] == VARIABLE_COUNT :
                mstackempty = True
                i = 2
                continue
            i = kaku_solver_iterate_incomplete()
            continue
        
        if ( i == 2) :
            #Abandon last used value for variable and take new next one
            while not mstackempty :
                mpointer = t_stack[0][0]
                mlist = t_stack[mpointer][1]
                mindex = mlist.index(t_stack[mpointer][2])
                #if last element of list has been checked - pop stack
                if mindex == len(t_stack[mpointer][1])-1 :
                    if mpointer == 1 :
                        mstackempty = True
                    else :
                        t_stack[0][0] = t_stack[0][0] - 1
                    continue
                else :
                    mval = mlist[mindex +1]
                    t_stack[mpointer][2] = mval
                    break

            if  mstackempty : break
            i = kaku_solver_iterate_invalid()
            
    if  mstackempty : i = 2       
 
    return i   


#Verifies variables of t_stack are unique in a kakuro equation 
def kaku_solver_validate_stack_variables() :
    global t_equation
    global t_stack
    global VARIABLE_COUNT

    #Indexable search array from t_stack
    t_temp = [0 for i in range(VARIABLE_COUNT + 1)]
    mpointer = t_stack[0][0] + 1
    for i in range(1, mpointer) :
        mindex = t_stack[i][0]
        mvalue = t_stack[i][2]
        t_temp[mindex] = mvalue
        
    #Check  values of variables in a equation are unique
    for i in t_equations :
        mvarlist = i[2]
        if len(mvarlist) > 1 :
            mvarvalues = []
            for j in mvarlist :
                if (t_temp[j]) != 0 : mvarvalues.append(t_temp[j])
            if len(set(mvarvalues)) <  len(mvarvalues) :
                return 2

    return 0


#Add a value for new variable and check for solution
def kaku_solver_iterate_incomplete() :
    global t_eqn
    global t_values
    global t_stack
 
    #Use allowable variable value from previous iteration ,
    #as we continue with the same assumed previous stack values
    t_stack[0][0] = t_stack[0][0] + 1
    mpointer = t_stack[0][0]
    mvariable = t_stack[mpointer][0]
    mvaluelist = list(t_values[mvariable][1])
    mvalue = mvaluelist[0]
    t_stack[mpointer][2] = mvalue
    
    t_eqn.append([ 0, mvalue, [mvariable] ])
    
    i =  kaku_solver_validate_stack_variables() 
    if (i == 2 ) : return i

    i = kaku_solver_solve_equations() 
 
    return i 


#Change a value for a variable  check for solution
def kaku_solver_iterate_invalid() :
    global t_equations
    global t_eqn
    global t_stack
    global VARIABLE_COUNT
    
    kaku_solver_intialise_t_eqn_t_values()
    
    #Equation of solved/to verify values combined in equations
    mpointer = t_stack[0][0]
    for ndx, mlist in enumerate(t_stack) :
        if ndx > mpointer : break
        if ndx != 0 :
            t_eqn.append([ 0, mlist[2], [mlist[0]] ])
            
    i =  kaku_solver_validate_stack_variables() 
    if (i == 2 ) : return i
    
    i = kaku_solver_solve_equations() 
  
    return i


#Display solution in graphic mode in Kakuro  screen
def s_graphic_solution(K_ROW, K_COL, frame, frame_arr) :
    global t
    global t_values   
   
    mcount = 1
    for i in range(K_ROW) :
        for j in range(K_COL) :
            if t[i][j] != 0 :
                if len(t_values[mcount][1]) == 1 :
                    mval = list(t_values[mcount][1])[0]
                else : mval = "?"
                mval = " " + str(mval) + " "
                k = i * K_ROW + j - mcount -1
                frame_arr[k].destroy
                frame_element =  tk.Frame(frame)       
                frame_element.grid( row=i ,column=j ,padx=1, pady=1)
                l1= tk.Label(frame_element, text=mval, highlightthickness=0,bd = 0,)
                l1.config(font=('lucida', 24))
                l1.grid( column = j, row = i)
                mcount += 1
 
    return


#Display solution in text mode in terminal window
def s_txt_solution(K_ROW, K_COL) :
    global t
    global t_values

    mcount = 1
    for i in range(K_ROW) :
        for j in range(K_COL) :
            if t[i][j] == 0 : print("X", end="|")
            else :
                if len(t_values[mcount][1]) == 1 :
                    mval = list(t_values[mcount][1])[0]
                else : mval = "?"
                print(mval, end="|")
                mcount += 1
            if j == K_COL - 1 : print(" ")
    print("===========================")
    return            
