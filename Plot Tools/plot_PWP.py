import matplotlib.pyplot as plt

f = open("pwp1.txt", "r")
g = open("acc_value.txt", "r")


Time = []
pwp1 = []
pwp2 = []
pwp3 = []
pwp4 = []
acc  = []
Time_acc = []

for line in f:
    all_numbers =[]
    numbers_str = line.strip().split()
    Time.append(float(numbers_str[0]))
    pwp1.append((float(numbers_str[1])))
    pwp2.append((float(numbers_str[2])))
    pwp3.append((float(numbers_str[3])))
    pwp4.append((float(numbers_str[4])))

i = 0
for line in g:
    all_numbers = []
    numbers_str = line.strip().split()
    acc.append(float(numbers_str[0]))
    Time_acc.append(i*0.01) 
    i+=1
    
    

   
 
plt.rcParams["figure.figsize"] = [12,8]
plt.subplot(5,1,1)
plt.ylabel("PWP (8m)")
plt.title("excess pore water pressure ratio")  
plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
plt.plot(Time, pwp1 , color='g',)
plt.xticks(visible=False)
plt.xlim([0, 33])

plt.subplot(5,1,2)
plt.ylabel("PWP (kPa) (6m)")
plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
plt.plot(Time, pwp2 , color='g')
plt.xticks(visible=False)
plt.xlim([0, 33])

plt.subplot(5,1,3)
plt.ylabel("PWP (kPa) (4m)")
plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
plt.plot(Time, pwp3 , color='g')
plt.xticks(visible=False)
plt.xlim([0, 33])

plt.subplot(5,1,4)
plt.ylabel("PWP (kPa) (3m)") 
plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
plt.plot(Time, pwp4 , color='g')
plt.xticks(visible=False)
plt.xlim([0, 33])

plt.subplot(5,1,5)
plt.ylabel("ACC (g)") 
plt.xlabel("Time (s)") 
plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
plt.plot(Time_acc, acc , color='Black')
plt.xlim([0, 33])


plt.legend()
plt.show()