import matplotlib.pyplot as plt

f = open("acc1.txt", "r")
g = open("acc_value.txt", "r")


Time = []
acc1 = []
one  = []
acc  = []
Time_acc = []

for line in f:
    all_numbers =[]
    numbers_str = line.strip().split()
    Time.append(float(numbers_str[0]))
    acc1.append(float(numbers_str[1]))
    one.append(1)

i = 0
for line in g:
    all_numbers = []
    numbers_str = line.strip().split()
    acc.append(float(numbers_str[0]))
    Time_acc.append(i*0.01) 
    i+=1
    
plt.rcParams["figure.figsize"] = [12,8]
plt.subplot(2,1,1)
plt.ylabel("ACC (1m)")
plt.title("Horizental Acceleration")  
plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
plt.plot(Time, acc1 , color='r')
plt.xticks(visible=False)
plt.xlim([0, 33])

plt.subplot(2,1,2)
plt.ylabel("ACC(g)") 
plt.xlabel("Time (Second)") 
plt.grid(color = 'black', linestyle = '--', linewidth = 0.5)
plt.plot(Time_acc, acc , color='Black')
plt.xlim([0, 33])


plt.legend()
plt.show()