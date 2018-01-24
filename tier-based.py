from munkres import Munkres
from collections import defaultdict
import itertools
import sys
import argparse
from collections import Counter

###############################################
# This program will try to look into
# per tier average values of bandwidth and
# processing cost in order to decide the best
# tier for placement. It will then do a
# optimization search in the tier in
# order top find the best server.
###############################################

#############################
# INPUT
parser = argparse.ArgumentParser()

parser.add_argument("-size", "--size", help="size of the graph", required=True)
parser.add_argument("-sbw", "--service_bw", type=int, help="service bandwidth", required=True)
parser.add_argument("-sproc", "--service_proc", type=int, help="service processing", required=True)

args = parser.parse_args()

size = args.size
service_bw = args.service_bw
service_proc = args.service_proc

filepath = "Files/" + size

with open(filepath + "/device_conn") as f:
    device_conn = [[int(num) for num in line.split()] for line in f]

with open(filepath + "/device_proc") as f:
    for line in f:
        device_proc = [float(i) for i in line.split()]

with open(filepath + "/edge_levels") as f:
    for line in f:
        edge_levels = [int(i) for i in line.split()]

with open(filepath + "/bandwidth") as f:
    for line in f:
        bandwidth = [int(i) for i in line.split()]

with open(filepath + "/avgbandwidth") as f:
    for line in f:
        avgbandwidth = [float(i) for i in line.split()]

with open(filepath + "/avgproc") as f:
    for line in f:
        avgproc = [float(i) for i in line.split()]

with open(filepath + "/maxbandwidth") as f:
    for line in f:
        maxbandwidth = [float(i) for i in line.split()]

with open(filepath + "/maxproc") as f:
    for line in f:
        maxproc = [float(i) for i in line.split()]


################################

def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    return (locs for key, locs in tally.items()
            if len(locs) > 1)


def print_assignment(index, command):
    proc_cost = 0
    for row, column in index:
        proc = matrix[row][column]
        proc_cost += proc
        if (command == 1):
            print("Job %d -> Device %d" % (row + 1, column + 1))
    if (command == 1):
        print("total processing cost: %.3f" % proc_cost)
    else:
        return proc_cost


def print_network_cost(index, connections, command):
    net_cost = 0
    for i in range(len(connections)):
        job1 = connections[i][0]
        job2 = connections[i][1]
        for j in range(len(index)):
            if (index[j][0] == job1):
                device1 = index[j][1]
                continue
            if (index[j][0] == job2):
                device2 = index[j][1]
        cost = device_conn[device1][device2]
        net_cost += cost
    if (command == 1):
        print("Total networking cost: %d" % net_cost)
    else:
        return net_cost


num_levels = len(avgbandwidth)

no_devices = len(device_proc)

level_count = Counter(edge_levels)

i = 1  # counting levels
j = 1  # counting device index
curr_index = 0
selected_server = 0

while i <= len(level_count):
    if (maxbandwidth[i - 1] >= service_bw and maxproc[i - 1] >= service_proc):
        lowest_netw_cost = 99
        lowest_proc_cost = 99
        while j <= level_count[i] + curr_index:
            if device_proc[j - 1] >= service_proc and bandwidth[j - 1] >= service_bw:
                netw_cost = device_conn[0][j]
                netw_cost = netw_cost + device_conn[j][no_devices + 1]
                if (netw_cost <= lowest_netw_cost):
                    #selected_netw_server = j;
                    proc_cost = device_proc[j-1] / service_proc
                    proc_cost = edge_levels[j-1] * proc_cost
                    if (proc_cost <= lowest_proc_cost):
                        lowest_netw_cost = netw_cost;
                        lowest_proc_cost = proc_cost;
                        selected_netw_server = j;
            j += 1

    curr_index = j - 1
    i += 1

    if (selected_netw_server != 0):
        break

netw_cost = lowest_netw_cost
selected_server = selected_netw_server

proc_cost = device_proc[selected_server-1] / service_proc
proc_cost = edge_levels[selected_server-1] * proc_cost

print(" Selected Edge server: %d, Tier level: %d, Bandwidth: %d, Processing power: %d, Processing cost: %d, Network cost: %d" %
      (selected_server, edge_levels[selected_server - 1], bandwidth[selected_server - 1], device_proc[selected_server - 1],
    proc_cost, netw_cost))
