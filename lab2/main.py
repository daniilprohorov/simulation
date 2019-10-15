import random
import simpy
from progress.bar import Bar

RANDOM_SEED = 42
COUNT = 10000  # Total number of customers
INTERVAL_GEN = 0.97  # Generate new customers roughly every x seconds

class Modeling():
    def __init__(self, capacity):
        self.elementsCounts = 0
        self.env = simpy.Environment()
        
        self.capacity = capacity 

        self.q               = []
        self.waitSum         = []
        self.deviceTimeSum   = []
        self.count           = []
        self.modelingTimeOne = [] 
        self.qLength         = []
        for el in capacity: 
            self.q.append(simpy.Resource(self.env, capacity=el))
            self.waitSum.append(0.0)
            self.deviceTimeSum.append(0.0)
            self.count.append(0)
            self.qLength.append(0)

        self.modelingTime = 0.0
        self.intensity    = 0.0

    def start(self, count, interval):
        self.env.process(self.gen(count, interval))
        self.env.run()
        self.intensity = self.elementsCounts/self.modelingTime

    def output(self):

        for i in range(3):
            print('%d)   Количество = %d' % (i+1, self.count[i] ))
            print('      Ср.Вр работы прибора = %f ' % (self.deviceTimeSum[i]/self.capacity[i]/self.count[i] ))
            print('      Загрузка = {:.2%}'.format(self.deviceTimeSum[i]/self.capacity[i]/self.modelingTime))
            print('      Нагрузка = {}'.format(  self.count[i] / ((self.deviceTimeSum[i]/self.capacity[i]/self.count[i])*self.intensity*self.elementsCounts)))
            print('      Ср.Вр ожидания = %f ' % (self.waitSum[i]/self.count[i] ))
            print('      Ср.длина очереди = %f ' % (self.qLength[i]/self.count[i] ))
            print()
        print('ModelingTime = %f ' % (self.modelingTime))
        print('Intensity    = %f ' % (self.intensity))
        
    def gen(self, number, interval):
        self.elementsCounts = number
        with Bar('Процесс вычисленния', max=number) as bar:
            modelTimeStart = self.env.now
            for i in range(number):
                d = 0 
                self.env.process(self.smo(0, 'SMO 1', i, 7.0, 0.53))
                t = random.expovariate(1.0 / interval)
                bar.next()
                yield self.env.timeout(t)
            self.modelingTime = self.env.now - modelTimeStart





    def smo(self, n, name, i, m, splitVal = None, RP = False):
        self.count[n] += 1
        arrive = self.env.now
        # RP - realtime print
        if RP:
            print('%9.4f %s %d: Start' % (arrive, name, i))
        if self.q[n].count <= self.capacity[n]:
            self.qLength[n] += self.q[n].count
            with self.q[n].request() as req:
                results = yield req | self.env.timeout(100000)
                wait = self.env.now - arrive
                self.waitSum[n] += wait
                if req in results:

                    if RP:
                        print('%9.4f %s %d: Waited %6.3f' % (self.env.now, name, i, wait))

                    blockTimeStart = self.env.now
                    timeout = random.expovariate(1.0 / m)
                    yield self.env.timeout(timeout)
                    self.deviceTimeSum[n] += self.env.now - blockTimeStart 

                    if RP:
                        print('%9.4f %s %d: Finished' % (self.env.now, name, i))

                    if splitVal != None:
                        splitGen = random.uniform(0, 1)
                        if splitGen > splitVal:
                            self.env.process(self.smo(1, 'SMO %d' % (n+1), i, m=7.0, RP = RP))
                        else:
                            self.env.process(self.smo(2, 'SMO %d' % (n+2), i, m=7.0, RP = RP))



                else:
                    print('lol')


    def __del__(self):
        self.output()

random.seed(RANDOM_SEED)

# Start processes and run
m = Modeling([8, 5, 4])
m.start(COUNT, INTERVAL_GEN)
