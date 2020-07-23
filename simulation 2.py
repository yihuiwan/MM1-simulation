"""
Usage: python lab1_template.py <npkts> <lambda>
Example: python lab1_template.py 1000000 1
"""
import sys
import time

ADD1 = 'trace1.txt'
ADD2 = 'trace2.txt'


class Queue:
    def __init__(self):
        self.queuedict = {}

    def insert(self, arrival_time, size, depature_time, Q_exist_pckt_amount, S_exist_pckt_amount):
        self.queuedict[arrival_time] = [size, depature_time, Q_exist_pckt_amount, S_exist_pckt_amount]
        return self.queuedict


# This function inserts a new packet to the queue
# You need to update these variables upon the insertion:
# N, the average number of packets in the system,
# For each n between 0 and 10, the probability P(n) that an arriving packet finds n packets already in the system


class Server:
    def __init__(self, inter_arrival_time, pckt_size, trace_name):
        self.service_rate = 4*pow(10, 3) if trace_name == 'trace1' else 7*pow(10, 3)
        self.inter_arrival_time = inter_arrival_time
        self.packet_size = pckt_size
        self.service_time = 0
        self.depature_time = 0
        self.waiting_time = 0
        self.time_stamp = {}
        self.exist_pckt_queue = 0
        self.serverdict = {}
        self.count = 1
        self.tot_sojourn_time = 0
        self.tot_pckt_in_sys = 0
        self.exist_pckt_in_sys = 0
        self.arrival_time = 0
        self.Pndict = {a: 0 for a in range(11)}

    def s_update(self, arrival_time, size, depature_time, Q_exist_pckt_amount, count, S_exist_pckt_amount):
        self.exist_pckt_in_sys = Q_exist_pckt_amount + S_exist_pckt_amount
        if 0 <= self.exist_pckt_in_sys <= 10:
            self.Pndict[self.exist_pckt_in_sys] += 1
        self.tot_pckt_in_sys += self.exist_pckt_in_sys
        self.serverdict.clear()
        self.serverdict[arrival_time] = [size, depature_time, Q_exist_pckt_amount]
        self.time_stamp[(arrival_time, 0)] = [0, count, Q_exist_pckt_amount]
        self.time_stamp[(depature_time, 1)] = [1, count, size / self.service_rate]
        self.tot_sojourn_time += (depature_time - arrival_time)
        self.count += 1
        return self.serverdict

    def Service(self):
        q = Queue()
        for key1 in range(len(self.inter_arrival_time)):
            self.arrival_time += self.inter_arrival_time[key1]
            self.service_time = 8 * self.packet_size[key1] / self.service_rate

            # check if there are remaining packet in server, if there is, then kick it out
            if self.serverdict != {}:
                for key2 in self.serverdict:
                    break
                if self.arrival_time >= self.serverdict.get(key2)[1]:
                    self.serverdict.pop(key2)

            if self.serverdict == {}:
                if q.queuedict == {}:
                    # if server and queue are both empty, the packet goes out directly
                    self.depature_time = self.arrival_time + self.service_time
                    self.s_update(self.arrival_time, self.packet_size[key1], self.depature_time, 0, self.count, 0)
                else:
                    key2 = max(q.queuedict)
                    if self.arrival_time > q.queuedict.get(key2)[1]:
                        # if the arrival time is later than the depature time of the last pckt in queue, then empty queue and the pckt goes out straight foward
                        while q.queuedict:
                            key3 = min(q.queuedict)
                            self.s_update(key3, q.queuedict.get(key3)[0], q.queuedict.get(key3)[1],
                                          q.queuedict.get(key3)[2], self.count, q.queuedict.get(key3)[3])
                            q.queuedict.pop(key3)
                        self.depature_time = self.arrival_time + self.service_time
                        self.s_update(self.arrival_time, self.packet_size[key1], self.depature_time, 0, self.count, 0)
                    else:
                        # if the arrival time is in the period of the future serving time of the pckt in the queue, then check the time with every pckt in the queue
                        while q.queuedict:
                            key3 = min(q.queuedict)
                            self.s_update(key3, q.queuedict.get(key3)[0], q.queuedict.get(key3)[1],
                                          q.queuedict.get(key3)[2], self.count, q.queuedict.get(key3)[3])
                            if self.arrival_time < q.queuedict.get(key3)[1]:
                                key4 = max(q.queuedict)
                                self.exist_pckt_queue = len(q.queuedict) - 1
                                self.depature_time = q.queuedict.get(key4)[1] + self.service_time
                                q.insert(self.arrival_time, self.packet_size[key1], self.depature_time,
                                         self.exist_pckt_queue, 1)
                                q.queuedict.pop(key3)
                                break
                            q.queuedict.pop(key3)
            else:
                # if the server is not empty when the pckt arrives, the pckt goes into queue
                for key2 in self.serverdict:
                    break
                self.exist_pckt_queue = 0
                self.depature_time = self.serverdict.get(key2)[1] + self.service_time
                if q.queuedict:
                    key3 = max(q.queuedict)
                    self.exist_pckt_queue = len(q.queuedict)
                    self.depature_time = q.queuedict.get(key3)[1] + self.service_time
                q.insert(self.arrival_time, self.packet_size[key1], self.depature_time, self.exist_pckt_queue, 1)

        while q.queuedict:
            # finalize the remaining pckts in queue
            key3 = min(q.queuedict)
            self.s_update(key3, q.queuedict.get(key3)[0], q.queuedict.get(key3)[1], q.queuedict.get(key3)[2],
                          self.count, q.queuedict.get(key3)[3])
            q.queuedict.pop(key3)
        # self.data_display()

    def data_display(self):
        for a in sorted(self.time_stamp):
            if int(self.time_stamp[a][0]) == 0:
                print('[{:<18}]: packet {} arrives and finds {} packets in the queue'.format(a[0], self.time_stamp[a][1],
                                                                                             self.time_stamp[a][2]))
            else:
                print('[{:<18}]: packet {} departs having spent {} us in the system'.format(a[0], self.time_stamp[a][1],
                                                                                            self.time_stamp[a][2]))

    # This function takes the next packet in the queue and handles it
    # Service time should be calculated based on the size of the packet
    # You also need to calculate the packet's departure time
    # In addition to service time,
    # what else do you need to calculate the correct departure time of the current packet?

    def summary(self, npkts):
        T = self.tot_sojourn_time / npkts
        N = self.tot_pckt_in_sys / npkts

        print("Summary:")
        print("-------------------------------------------")
        print("average number of packets in the system N : {}".format(N))
        print("average time spent by a packet in the system T : {} us".format(T))
        print("probability P(n) that an arriving packet finds n packets already in the system: ")
        for n in range(11):
            print('p[{}]:{}'.format(n, self.Pndict[n]/npkts))
        self.plot(npkts, self.Pndict)

    def plot(self, npkts, p):
        import matplotlib.pyplot as plt

        P = [p[i] / npkts for i in range(11)]
        X = [i for i in range(11)]
        plt.figure()
        plt.bar(X, P)
        plt.xlabel("X-axis")
        plt.ylabel("Y-axis")
        plt.show()


# Here you need to plot P(n) for n from 0 to 10
# X axis would be 0 to 10
# Y axis would be P(n)


def ReadFile(add):
    inter_arrival_time = []
    pckt_size = []
    lst = []
    f = open(add)
    while True:
        line = f.readline()
        if not line:
            break
        lst.append(line)
    f.close()
    for i in lst:
        m = i.splitlines()
        j = m[0].split('\t')
        inter_arrival_time.append(float(j[0]))
        pckt_size.append(int(j[1]))
    npkts = len(inter_arrival_time)
    return npkts, inter_arrival_time, pckt_size


def main():
    npkts, inter_arrival_time, pckt_size = ReadFile(ADD1) if sys.argv[1] == 'trace1' else ReadFile(ADD2)
    s = Server(inter_arrival_time, pckt_size, sys.argv[1])
    s.Service()
    s.summary(npkts)


if __name__ == "__main__":
    main()
