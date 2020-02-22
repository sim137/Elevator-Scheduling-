#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np, scipy


# In[5]:


# Floor#, doorOPEN start, end, doorCLOSE start, end
# estimated to 0.5s, not very accurate
# start from 14F, [-0.5] (door closed a little bit before I start recording)
down_data = [
    [29, [26, 28, 28, 30]],
    [28, [42, 44, 46.5, 48.5]],
    [26, [62, 64, 66.5, 68.5]],
    [23, [82, 84, 86, 88]],
    [19, [104.5, 106.5, 109, 111]],
    [14, [127, 129, 131.5, 133.5]],
    [8, [152, 154, 156, 158]],
    [4,  [176, 178, 182.5, 184.5]]
]

up_data = [
    [4,  [176, 178, 182.5, 184.5]],
    [5, [198.5, 200.5, 202, 204]],
    [6, [215.5, 217.5, 220, 222.5]],
    [8, [235.5, 237.5, 239.5, 242]],
    [11, [256, 258, 260, 262]],
    [15,  [278.5, 280.5, 282.5, 284.5]], 
    [20,  [301.5, 303.5,  306, 308]],
    [26, [325.5, 327.5,  330, 332]]
]
# back to 14F, [357.5, 359.5]
# 4F has larger height


# ### parameter estimation

# In[107]:


# one person load, do not consider other loads
# when no person enter/leave
## time from doorOPEN end to doorCLOSE start, allow residents to get in/out
T_boarding = np.average([[x[1][2]-x[1][1] for x in down_data + up_data]])
## time from doorOPEN start to doorCLOSE end, lift rest
T_rest = np.average([[x[1][3]-x[1][0] for x in down_data + up_data]])

## estimated duration for each person to enter/leave, as 2/3 of T_boarding 
# always 1/3 extra for lift to detect and extend boarding time to ensure safeness
# so actual boarding duration will be (N+0.5)*T_pp
T_pp = 2./3. * T_boarding
# doorOPEN start to end; doorCLOSE start to end
T_door = (T_rest - T_boarding)/2.
print('boarding duration', T_boarding, 'rest duration', T_rest, 'per-person duration', np.round(T_pp,3), 'door moving duration', np.round(T_door,3))





# In[9]:


# elevator moving duration
for i in range(1, len(down_data)):
    x1, x2 = down_data[i-1:i+1]
    print('down', x1[0]-x2[0], 'duration', x2[1][0]-x1[1][3])
    
for i in range(1, len(up_data)):
    x1, x2 = up_data[i-1:i+1]
    print('up', x2[0]-x1[0], 'duration', x2[1][0]-x1[1][3])
   
    
    
# extra: up 29-14=15, 26.5s; down 26-14=12, 25.5


# In[46]:


# using piecewise linear function to approximate
# [1, 6], 1.5; (6, 12], 1.25; (12, +\infty), 1
# 4F to 5F counted as 2.5 floors

a0, a1, a2 = 1.4, 1.2, 1.  # linear coefficients
f0, f1 = 6, 12  # boundary
# acceleration/deceleration time
T_acc = 10.4  # around (12 + 11.5)/2 - a0  


# In[47]:


(4.5+2.5+5.5+5.5+4+3.5)/6/3


# In[83]:


def Ntime(nP):
    # nP>0
    #if nP <= 0: nP = 1
    return (nP+0.5)*T_pp


# In[89]:



# elevator travel time between floors: door CLOSE end to door OPEN start
# ignoring variations between up and down
def Ftime(startF, endF):
    nF = abs(startF - endF)
    if nF == 0:
        return 0.
    if startF == 4 or endF == 4:
        nF += 1.5
    
    t = T_acc
    if nF < f0:
        t += a0 * nF
    elif nF < f1:
        t += a0 * f0 + a1 * (nF - f0)
    else:
        t += a0 * f0 + a1 * (f1 - f0) + a2 * (nF - f1)
    
    return t


# In[63]:


Ftime(4, 8)


# In[64]:


# 20 residents each floor, totally 24 floors (5F~28F)
# from the provided demographic data 475 (~480 in our model)

NF = 24
NpF = 20
# 3 lifts, each capacity 12 persons, 900kg
NpL = 12
NL = 3

# ignore rare events like some residents go downstairs to 4F, to 3F library or to 29F laundry room
# estimate 80% of residents will queue up for going upstairs


# In[109]:


# queue model

queue = np.random.permutation(np.arange(NpF*NF)) 
queue = queue % 24 + 5
#queue = queue[:int(NpF*NF*0.8)]



# more probability for floormate pairs


# In[111]:


# one elevator dispatch NL residents and return to 4F
# time from 4F doorOPEN end to 4F doorOPEN end
frange = np.arange(5, 28+1)
def Etime(q, floors=False):
    #len(q) == NL
    cc = np.histogram(q, bins=np.arange(5,28+2))
    Fs = frange[cc[0]>0] # pressed floor buttons
    Ns = cc[0][cc[0]>0] # number of persons each floor
    
    pre = 4
    t = Ntime(len(q)) + T_door
    for (F, N) in zip(Fs, Ns):
        t += Ftime(pre, F) + T_door + Ntime(N) + T_door
        pre = F
        
    # return to 4F
    t += Ftime(pre, 4) + T_door
    
    if floors:
        return t, len(Ns)
    else:
        return t
    
    


# In[95]:


# stops at every (other) floors consecutively
print(Etime(np.arange(5,5+NpL, 1)), Etime(np.arange(5,5+NpL*2, 2)))


# ## Scheduling Algorithms

# In[116]:


# normal queueing
N_thres = int(NpF*NF*0.8)
# time estimate until the elevator, which the N_thres-th person in the queue takes, return to 4F

N_cur = 0

# single elevator
t1 = 0
while N_cur < N_thres:
    t1 += Etime(queue[N_cur:N_cur + NpL])
    N_cur += NpL

print('1 lift:', t1, "%d persons in total"%N_cur)

# NL=3 elevators
N_cur = 0
Ts = [[] for i in range(NL)]
Fs = [[] for i in range(NL)]
totalTs = [0 for i in range(NL)]
while N_cur < N_thres:
    i = np.argmin(totalTs)
    ti,ni = Etime(queue[N_cur:N_cur + NpL], True)
    N_cur += NpL
    totalTs[i] += ti
    Ts[i].append(ti)
    Fs[i].append(ni)

print('%d lifts 1 queue:'%NL, max(totalTs), "%d persons in total"%N_cur)    
print('avg time/batch', [np.average(T) for T in Ts], 'avg #floors/batch', [np.average(F) for F in Fs])


# In[106]:


totalTs


# In[114]:





# In[113]:


Ts, Fs


# In[119]:


# 3 queues according to modulo 3
qmod = queue % NL
qs = [queue[qmod == i] for i in range(NL)]


# NL=3 elevators
N_cur = 0
Ts = [[] for i in range(NL)]
Fs = [[] for i in range(NL)]
totalTs = [0 for i in range(NL)]
N_curs = [0 for i in range(NL)]
mod_cur = -1
while N_cur < N_thres:
    mod_cur = (mod_cur + 1) % NL
    cur = N_curs[mod_cur]
    q = qs[mod_cur]
    if cur >= len(q):
        continue
    
    i = np.argmin(totalTs)
    ti,ni = Etime(q[cur:cur+NpL], True)
    
    totalTs[i] += ti
    N_curs[i] += NpL
    Ts[i].append(ti)
    Fs[i].append(ni)
    
    N_cur += NpL
    

print('%d lifts %d queues mod %d:'%(NL, NL, NL), max(totalTs), "%d persons in total"%N_cur)    
print('avg time/batch', [np.average(T) for T in Ts], 'avg #floors/batch', [np.average(F) for F in Fs])


# In[ ]:


# 3 queues of lower/middle/upper floors


# In[118]:


2137./2843.


# In[ ]:



