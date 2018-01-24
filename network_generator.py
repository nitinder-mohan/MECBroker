import os
import random
import subprocess
from itertools import repeat

import matplotlib.pyplot as plt
import networkx as nx

####################################################
# This code will generate a network graph comprising
# of 1 client, X edge servers and 1 cloud node. The
# values for bandwidth, network connections, network
# weights and processing powers are randomly chosen
# between the slice defined by the user. The program
# will then store the values into files in the same
# folder organized according to the graph size.
#####################################################

def decision(probability):
    return random.random() < probability

cwdir = os.getcwd()

####Enter inputs for device placements
###Specify number of device nodes
print("#### Enter the number of devices in edge-fog cloud ####")
print("#### Press enter to take the default value ####")

total_nodes = int(input("Enter total number of edge devices: "))

edge_levels = int(input("Enter the number of edge levels [Default=3]: ") or "3")
levels = []

###Specify lower and upper bounds of processing costs
print("#### Enter the processing power bounds of the devices ####")
proc_edge_low = int(input("Lowest base processing power of edge device [Default=3]: ") or "3")
proc_edge_high = int(input("Highest base processing power of edge device [Default=6]: ") or "6")

###Specify lower and upper bounds of processing costs
print("#### Enter the bandwidth bounds of the devices ####")
bandwidth_edge_low = int(input("Lowest base bandwidth bound of edge device [Default=10]: ") or "10")
bandwidth_edge_high = int(input("Highest base bandwidth bound of edge device [Default=30]: ") or "30")

###Specify lnetwork connecttion weight
print("#### Enter the network connection weight ####")
netw_conn_same_low = int(input("Lowest same level connection weight [Default=1]: ") or "1")
netw_conn_same_high = int(input("Highest same level connection weight [Default=3]: ") or "3")
netw_conn_next_low = int(input("Lowest next level connection weight [Default=4]: ") or "4")
netw_conn_next_high = int(input("Highest next level connection weight [Default=6]: ") or "6")

prob_clientedge = float(input("Enter client probability connectivity to 1st edge layer (0-1) [Default=0.5]: ") or "0.5")
prob_edgeserver = float(input("Enter client probability connectivity to 1st edge layer (0-1) [Default=0.7]: ") or "0.7")

print("#### Enter the network densities between the devices ####")
prob_samelevel = float(input("Enter connections density between same level edge cloud (0-1) [Default=0.4]: ") or "0.4")
prob_nextlevel = float(input("Enter connections density with next level edge cloud (0-1) [Default=0.6]: ") or "0.6")

no_jobs = 0
while(no_jobs!=total_nodes):
    no_jobs=int(input("Enter number of jobs deployed on edge-fog cloud [Default=Total number of devices]: ") or total_nodes)
    if no_jobs!=total_nodes:
        print("Please enter number of jobs as equal to number of total available devices")

####################################

##Create an empty graph
G=nx.Graph()   #Graph for devices

edge_nodes = list(range(1,total_nodes+1))

edge_servers = total_nodes
for i in range(0, edge_levels):

    if i == edge_levels-1:
        levels.extend(repeat(i + 1, edge_servers))
        break

    servers = int(0.5*edge_servers)
    levels.extend(repeat(i + 1, servers))
    edge_servers = edge_servers - servers

##Create a filepath for writing files for scripts
filepath = "Files/"+str(total_nodes)

##Create the directory if it doesnt exist. Can raise an exception on race
if not os.path.exists(filepath):
    os.makedirs(filepath)

G.add_node(0, name='source')

##Add Device nodes to graph
for i in enumerate(edge_nodes):
    if levels[i[0]] == 1:
        processing_cost = 2 * random.randint(proc_edge_low,proc_edge_high)
    elif levels[i[0]] == 2:
        processing_cost = 1.5 * random.randint(proc_edge_low, proc_edge_high)
    else:
        processing_cost = levels[i[0]] * random.randint(proc_edge_low, proc_edge_high)
    G.add_node(i[1],processing=processing_cost,edge_level=levels[i[0]], name=i[1], bandwidth=(levels[i[0]] * random.randint(bandwidth_edge_low,bandwidth_edge_high)))

G.add_node(total_nodes+1, name='datacenter')

##get processing costs
processing = list(nx.get_node_attributes(G,'processing').values())
bandwidth = list(nx.get_node_attributes(G, 'bandwidth').values())

##Calculate average bandwidth per layer
avgNetw_level = []

lev=levels[len(levels)-1]
i=0
while i<=lev:
    i = i+1
    sum = 0
    count = 0
    j=0
    while j<len(levels):
        if levels[j]==i:
            sum += bandwidth[j]
            count += 1
        j += 1
    if count!=0:
        avg = sum / count
        avgNetw_level.append(avg)

##Calculate average bandwidth per layer
avgProc_level = []

i = 0
while i <= lev:
    i = i + 1
    sum = 0
    count = 0
    j = 0
    while j < len(levels):
        if levels[j] == i:
            sum += processing[j]
            count += 1
        j += 1
    if count != 0:
        avg = sum / count
        avgProc_level.append(avg)

##Calculate max bandwidth per layer
maxNetw_level = []

i=0
while i<=lev:
    i = i+1
    max = 0
    j=0
    while j<len(levels):
        if levels[j]==i and bandwidth[j]>max:
            max = bandwidth[j]
        j += 1
    if max!=0:
        maxNetw_level.append(max)

##Calculate max proc per layer
maxProc_level = []

i=0
while i<=lev:
    i = i+1
    max = 0
    j=0
    while j<len(levels):
        if levels[j]==i and processing[j]>max:
            max = processing[j]
        j += 1
    if max!=0:
        maxProc_level.append(max)
#####################################

###Add connections between devices

#connections from source to edge level 1
j=1
while j<len(edge_nodes):
    if levels[j-1]==1:
        if decision(prob_clientedge):
            G.add_edge(0, edge_nodes[j-1], weight=random.randint(1,3))
        j=j+1
    else:
        break

##Connections between the edge devices
for i in range(len(edge_nodes)):
    j=i+1
    while j<len(edge_nodes):
        if levels[i]==levels[j]:
            if decision(prob_samelevel)==True:
                G.add_edge(i+1, j+1, weight=random.randint(netw_conn_same_low, netw_conn_same_high))

        elif levels[j] - levels[i] == 1:
            if decision(prob_nextlevel) == True:
                G.add_edge(i+1, j+1, weight=random.randint(netw_conn_next_low, netw_conn_next_high))

        else:
            break

        j=j+1

##Add connection from last edge level to cloud
j=1
while j<len(edge_nodes)+1:
    if levels[j-1]==edge_levels:
        if decision(prob_edgeserver):
            G.add_edge(total_nodes+1, edge_nodes[j-1], weight=random.randint(5, 10))
    j=j+1

###############################################
            #OUTPUTS
###############################################
######Write to files for input to scripts

# write processing cost to file
f = open(filepath + "/device_proc", "w")
for j in enumerate(processing):
    f.write(str(j[1]) + " ")
f.close()

# write edge levels to file
f = open(filepath + "/edge_levels", "w")
for j in enumerate(levels):
    f.write(str(j[1]) + " ")
f.close()

# write bandwidth to file
f = open(filepath + "/bandwidth", "w")
for j in enumerate(bandwidth):
    f.write(str(j[1]) + " ")
f.close()

# write average bandwidth to file
f = open(filepath + "/avgbandwidth", "w")
for j in enumerate(avgNetw_level):
    f.write(str(j[1]) + " ")
f.close()

# write average processing to file
f = open(filepath + "/avgproc", "w")
for j in enumerate(avgProc_level):
    f.write(str(j[1]) + " ")
f.close()

# write max network to file
f = open(filepath + "/maxbandwidth", "w")
for j in enumerate(maxNetw_level):
    f.write(str(j[1]) + " ")
f.close()

# write max proc to file
f = open(filepath + "/maxproc", "w")
for j in enumerate(maxProc_level):
    f.write(str(j[1]) + " ")
f.close()

##write network costs to file
f = open(filepath+"/device_conn","w")
for i in range(total_nodes+2):
    for j in range(total_nodes+2):
        if i==j:
            f.write("99 ")
        else:
            try:
                f.write(str(nx.dijkstra_path_length(G,i,j,weight="weight")) + " ")
            except:
                f.write("0 ")
    if i!=total_nodes+1:
        f.write("\n")
f.close()

#########Draw the device graph
pos = nx.spring_layout(G)

plt.figure(1, figsize=(20,20))
node_name_labels = nx.get_edge_attributes(G, "name")
nx.draw_networkx_nodes(G,pos,nodelist=edge_nodes,node_color='b', node_size=300 ,alpha=0.7)
#nx.draw_networkx_nodes(G,pos,nodelist=fog_nodes,node_color='r', node_size=500, node_shape='s',alpha=0.7)
nx.draw_networkx_labels(G, pos, edge_labels=node_name_labels)

edge_weight_labels = nx.get_edge_attributes(G, "weight")

nx.draw_networkx_edges(G, pos)
nx.draw_networkx_edge_labels(G,pos,edge_labels=edge_weight_labels)

plt.savefig(filepath+"/device_layout.png")


plt.show(block=False)


plt.show()
