"""
Usage: python lab1_template.py <npkts> <lambda>
Example: python lab1_template.py 1000000 1
"""
import numpy
import random
import sys


class Source:
    def __init__(self, lambd, npkts):
        self.packet_amount = npkts
        self.interarrival_time = random.expovariate(lambd)
        self.size = round(numpy.random.exponential(10000))


# This function generates a packet
# Packet size should be a random number based on exponential distribution
# Inter-arrival time of the generated packet should be a random number based on Poisson process
# Note from the lecture's slides: Inter-arrival time (i.e. time between successive arrivals) is an
# exponential r.v. with parameter lambda.
# This basically means that you can generate Poisson process random numbers with exponential distribution
# In addition to inter-arrival time,
# what else do you need to calculate the correct arrival time of the generated packet?


class Packet(Source):
    def __init__(self, lambd, npkts):
        Source.__init__(self, lambd, npkts)
        self.PacketDict = {}
        self.arrival_time = 0

    def Generate(self, lambd, npkts):
        count = 1
        while count <= npkts:
            s = Source(lambd, npkts)
            self.arrival_time = 0 if count == 1 else self.arrival_time + s.interarrival_time
            self.size = s.size
            self.PacketDict[self.arrival_time] = self.size
            count += 1
        return self.PacketDict


class Queue:
    def __init__(self):
        self.queuedict = {}

    def insert(self, arrival_time, size, depature_time, exist_pckt_amount):
        self.queuedict[arrival_time] = [size, depature_time, exist_pckt_amount]
        return self.queuedict


# This function inserts a new packet to the queue
# You need to update these variables upon the insertion:
# N, the average number of packets in the system,
# For each n between 0 and 10, the probability P(n) that an arriving packet finds n packets already in the system


class Server(Packet, Queue):
    def __init__(self, lambd, npkts):
        Packet.__init__(self, lambd, npkts)
        self.service_rate = pow(10, 4)  # The server can prcocess 10Gbps
        self.packet_size = 0
        self.service_time = 0
        self.depature_time = 0
        self.waiting_time = 0
        self.time_stamp = {}
        self.exist_pckt_amount = 0
        self.serverdict = {}
        self.count = 1
        self.tot_sojourn_time = 0
        self.Pndict = {a: 0 for a in range(11)}

    def s_update(self, arrival_time, size, depature_time, exist_pckt_amount, count):
        if 0 <= exist_pckt_amount <= 10:
            self.Pndict[exist_pckt_amount] += 1
        self.serverdict.clear()
        self.serverdict[arrival_time] = [size, depature_time, exist_pckt_amount]
        self.time_stamp[arrival_time] = [0, count, exist_pckt_amount]
        self.time_stamp[depature_time] = [1, count, size / self.service_rate]
        self.tot_sojourn_time += (depature_time - arrival_time)
        self.count += 1
        return self.serverdict

    def Service(self, lambd, npkts):
        q = Queue()
        self.PacketDict = Packet.Generate(self, lambd, npkts)
        for key1 in self.PacketDict:
            self.arrival_time = key1
            self.packet_size = self.PacketDict.get(key1)
            self.service_time = self.packet_size / self.service_rate

            # 判断server里面有没有正在运行的，有就踢出去
            if self.serverdict != {}:
                for key2 in self.serverdict:
                    break
                if self.arrival_time > self.serverdict.get(key2)[1]:
                    self.serverdict.pop(key2)

            if self.serverdict == {}:
                if q.queuedict == {}:
                    # 如果server和queue都是空的，该包直接出去
                    self.depature_time = self.arrival_time + self.service_time
                    self.s_update(self.arrival_time, self.packet_size, self.depature_time, 0, self.count)
                else:
                    key2 = max(q.queuedict)
                    if self.arrival_time > q.queuedict.get(key2)[1]:
                        # 如果到达时间比queue中最后出来的时间还晚，queue全部出去，该包直接出去
                        while q.queuedict:
                            key3 = min(q.queuedict)
                            self.s_update(key3, q.queuedict.get(key3)[0], q.queuedict.get(key3)[1],
                                          q.queuedict.get(key3)[2], self.count)
                            q.queuedict.pop(key3)
                        self.depature_time = self.arrival_time + self.service_time
                        self.s_update(self.arrival_time, self.packet_size, self.depature_time, 0, self.count)
                    else:
                        # 如果到达时间在queue中某个包未来会在运行的时间，一个一个判断queue中的元素踢出去
                        while q.queuedict:
                            key3 = min(q.queuedict)
                            self.s_update(key3, q.queuedict.get(key3)[0], q.queuedict.get(key3)[1],
                                          q.queuedict.get(key3)[2], self.count)
                            if self.arrival_time < q.queuedict.get(key3)[1]:
                                key4 = max(q.queuedict)
                                self.exist_pckt_amount = len(q.queuedict) - 1
                                self.depature_time = q.queuedict.get(key4)[1] + self.service_time
                                q.insert(self.arrival_time, self.packet_size, self.depature_time,
                                         self.exist_pckt_amount)
                                q.queuedict.pop(key3)
                                break
                            q.queuedict.pop(key3)
            else:
                # 如果到达时，server还有在跑，包进queue
                for key2 in self.serverdict:
                    break
                self.exist_pckt_amount = 0
                self.depature_time = self.serverdict.get(key2)[1] + self.service_time
                if q.queuedict:
                    key3 = max(q.queuedict)
                    self.exist_pckt_amount = len(q.queuedict)
                    self.depature_time = q.queuedict.get(key3)[1] + self.service_time
                q.insert(self.arrival_time, self.packet_size, self.depature_time, self.exist_pckt_amount)

        while q.queuedict:
            # 最后把未处理的queue搞完
            key3 = min(q.queuedict)
            self.s_update(key3, q.queuedict.get(key3)[0], q.queuedict.get(key3)[1], q.queuedict.get(key3)[2],
                          self.count)
            q.queuedict.pop(key3)

        self.data_display()

    def data_display(self):
        for a in sorted(self.time_stamp):
            if int(self.time_stamp[a][0]) == 0:
                print('[{:<18}]: packet {} arrives and finds {} packets in the queue'.format(a, self.time_stamp[a][1],
                                                                                             self.time_stamp[a][2]))
            else:
                print('[{:<18}]: packet {} departs having spent {} us in the system'.format(a, self.time_stamp[a][1],
                                                                                            self.time_stamp[a][2]))

    # This function takes the next packet in the queue and handles it
    # Service time should be calculated based on the size of the packet
    # You also need to calculate the packet's departure time
    # In addition to service time,
    # what else do you need to calculate the correct departure time of the current packet?

    def summary(self, lambd, npkts):
        T = self.tot_sojourn_time / npkts
        N = lambd * T

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

def main():
    npkts, lambd = int(sys.argv[1]), float(sys.argv[2])
    # npkts, lambd = 50, 1

    s = Server(lambd, npkts)
    s.Service(lambd, npkts)
    s.summary(lambd, npkts)


if __name__ == "__main__":
    main()
