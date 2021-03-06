### Assigning Jobs to Edge and Fog nodes#####
###Nitinder Mohan####

###############################################
# This code first tries to find the node which
# can house the service with least network cost.
# Once it finds the node, it checks if the node
# can handle the processing capability of service.
# If yes, the best node is returned. If no, it tries
# to find the second node with best network cost.
#################################################

from munkres import Munkres
from collections import defaultdict
import itertools
import sys
import argparse

#############################
#INPUT
parser = argparse.ArgumentParser()

parser.add_argument("-size", "--size", help="size of the graph", required=True)
parser.add_argument("-sbw", "--service_bw", type=int, help="service bandwidth", required=True)
parser.add_argument("-sproc", "--service_proc", type=int, help="service processing", required=True)

args = parser.parse_args()

size = args.size
service_bw = args.service_bw
service_proc = args.service_proc

filepath = "Files/"+ size

with open(filepath+"/device_conn") as f:
    device_conn = [[int(num) for num in line.split()] for line in f]

with open(filepath+"/device_proc") as f:
    for line in f:
        device_proc = [float(i) for i in line.split()]

with open(filepath+"/edge_levels") as f:
    for line in f:
        edge_levels = [int(i) for i in line.split()]

with open(filepath+"/bandwidth") as f:
    for line in f:
        bandwidth = [int(i) for i in line.split()]
################################

def list_duplicates(seq):
    tally = defaultdict(list)
    for i,item in enumerate(seq):
        tally[item].append(i)
    return (locs for key,locs in tally.items()
                            if len(locs)>1)

def print_assignment(index, command):
    proc_cost=0
    for row, column in index:
        proc = matrix[row][column]
        proc_cost += proc
        if (command==1):
            print("Job %d -> Device %d" % (row+1, column+1))
    if (command==1):
        print("total processing cost: %.3f" % proc_cost)
    else:
        return proc_cost

def print_network_cost(index, connections, command):
    net_cost = 0
    for i in range(len(connections)):
        job1 = connections[i][0]
        job2 = connections[i][1]
        for j in range(len(index)):
            if(index[j][0]==job1):
                device1 = index[j][1]
                continue
            if(index[j][0]==job2):
                device2 = index[j][1]
        cost = device_conn[device1][device2]
        net_cost += cost
    if (command==1):
        print("Total networking cost: %d" % net_cost)
    else:
        return net_cost


## Network cost minimization
assign = 1
netw_conn = []

i=1  ## start value as 1 as device_conn has 0 as source/client
#number = []

no_devices = len(device_proc)
lowest_netw_cost = 99;
selected_netw_server = 0;

while i <= no_devices:
    if (bandwidth[i-1]>=service_bw and device_proc[i-1]>=service_proc): #select only the node which can support the service
        netw_cost = device_conn[0][i]
        netw_cost = netw_cost + device_conn[i][no_devices+1]
        if (netw_cost < lowest_netw_cost):
            lowest_netw_cost = netw_cost;
            selected_netw_server = i;

    i += 1

proc_cost = device_proc[selected_netw_server-1]/service_proc
proc_cost = edge_levels[selected_netw_server-1] * proc_cost

print(" Selected Edge server: %d, Tier level: %d, Bandwidth: %d, Processing power: %d, Processing cost: %d, Network cost: %d" %
      (selected_netw_server, edge_levels[selected_netw_server-1], bandwidth[selected_netw_server-1], device_proc[selected_netw_server-1], proc_cost, lowest_netw_cost))



### Network cost minization over


# #make permuted list of indexes
# while i < len(device_conn):
#    number.append(i)
#    i += 1
#
# permuted = list(itertools.permutations(number, len(job_conn)))
#
# perm_index = []
# new_index = []
# for i, lst in enumerate(permuted):
#     for j, elem in enumerate(lst):
#         new_index.append([j,elem])
#     perm_index.append(new_index)
#     new_index = []
#
# ####create processing cost matrix
# matrix = []
# for i in enumerate(job_size):
#     row = []
#     for j in enumerate(device_proc):
#         row.append(round(i[1]/j[1], 3))
#     matrix.append(row)
#
# ####create network connection matrix
# for i in range(len(job_conn)):
#     l=[]
#     for j in range(len(device_conn)):
#         l.append(job_conn[i][j]*device_conn[i][j])
#     netw_conn.append(list(l))
#
# ######get possible combinations yielding to same processing cost#####
# duplicates = []
# for dup in sorted(list_duplicates(device_proc)):
#     duplicates.append(dup)
#
# for p in duplicates:
#     if (len(p)>2):
#         comb = list(itertools.combinations(p,2))
#         duplicates.remove(p)
#         for l in comb:
#             duplicates.append(list(l))
#
# #####get all possible job connections
# connections = []
# for i, lst in enumerate(job_conn):
#     for j, conn in enumerate(lst):
#         if conn == 1:
#             if i<j:
#                 connections.append([i, j])
#             else:
#                 connections.append([j, i])
#
# #remove duplicate both ways connections
# b_set = set(tuple(x) for x in connections)
# connections = [ list(x) for x in b_set ]
#
# index = []
# best_index = []
# best_cost = None
#
# while len(perm_index) != 0:
#     index = perm_index.pop(0)
#     netw_cost = print_network_cost(index, connections, 2)
#     if (best_cost == None):
#         best_cost = netw_cost
#         best_index.append(index)
#     elif (netw_cost < best_cost):
#         best_cost = netw_cost
#         best_index = []
#         best_index.append(index)
#     elif (netw_cost == best_cost):
#         best_index.append(index)
# #
# # print("Best Possible Network Assignments")
# # print("")
#
# index_new =[]
# assignment = 1
# ##Uncomment if you want to find out all the possible assignments having least network cost
#
# # while len(best_index)!=0:
# #     index_new=best_index.pop(0)
# #     print("Assignment "+str(assignment))
# #     print("Processing cost: " + str(print_assignment(index_new, 2)))
# #     print_network_cost(index_new, connections, 1)
# #     print("")
# #     assignment = assignment+1
# index_new=best_index.pop(0)
# print_network_cost(index_new, connections, 1)
