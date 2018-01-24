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
import argparse
import sys

#############################
#INPUT

parser = argparse.ArgumentParser()

parser.add_argument("--size", help="size of the graph", required=True)
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


## Processing cost minization

no_devices = len(device_proc)
lowest_proc_cost = 99;
selected_proc_server = 0;
i=0

while i < no_devices:
    if (device_proc[i]>=service_proc and bandwidth[i] >= service_bw):
        proc_cost = device_proc[i]/service_proc
        proc_cost = edge_levels[i] * proc_cost
        if (proc_cost < lowest_proc_cost):
                lowest_proc_cost = proc_cost;
                selected_proc_server = i+1;
    i += 1

netw_cost = device_conn[0][selected_proc_server]
netw_cost = netw_cost + device_conn[selected_proc_server][no_devices+1]

print(" Selected Edge server: %d, Tier level: %d, Bandwidth: %d, Processing power: %d, Processing cost: %d, Network cost: %d" %
      (selected_proc_server, edge_levels[selected_proc_server-1], bandwidth[selected_proc_server-1], device_proc[selected_proc_server-1], lowest_proc_cost, netw_cost))
