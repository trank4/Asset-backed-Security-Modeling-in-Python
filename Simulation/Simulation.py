#Simulation class to encapsulate simulation methods
from Tranche.StructuredSecurities import StructuredSecurities
import math
import multiprocessing
import logging

class Simulation(object):
    @staticmethod
    def simulateWaterfall(structuredSecurities,loanPool, NSIM):
        #run doWaterfall NSIM times and return the list of lists of DIRR and AL
        res = []
        for i in range(NSIM):
            # reset tranches back to initial conditions
            structuredSecurities.tranches_reset()
            # reset default status of loans in loan pool
            loanPool.default_reset()
            #doWaterfall and store DIRR and AL info
            res.append(StructuredSecurities.doWaterfall(structuredSecurities,loanPool)[4:6])
        #find lists of average DIRR for tranches
        avgDIRR_lst = []
        for t in range(len(structuredSecurities.tranches)):
            #list of DIRRs for the tranche
            DIRR_lst = [i[0][t] for i in res]
            #find average
            avgDIRR = sum(DIRR_lst) / NSIM
            #append to avgDIRR_lst
            avgDIRR_lst.append(avgDIRR)
        #find lists of average AL for tranches, with None excluded
        avgAL_lst = []
        for t in range(len(structuredSecurities.tranches)):
            #find list of AL for the tranche in different simulations with None value replaced by 0
            ALlst = [i[1][t] if i[1][t] else 0 for i in res]
            #find average AL for the tranche
            avgAL = sum(ALlst) / NSIM
            #append to avgAL_lst
            avgAL_lst.append(avgAL)
        return (avgDIRR_lst,avgAL_lst)

    # doWork for multiprocessing
    @staticmethod
    def doWork(input, output):
        while True:
            try:
                # get input
                f, args = input.get(timeout=1)
                # run the function and return average DIRR and average AL
                res = f(*args)
                # put the result to output queue
                output.put(res)
            except Exception as ex:
                print(ex)
                break

    # simulateWaterfallParallel
    @staticmethod
    def simulateWaterfallParallel(structuredSecurities, loanPool, NSIM, numProcesses):
        # initialize input_queue and output_queue
        input_queue = multiprocessing.Queue()
        output_queue = multiprocessing.Queue()
        # pass in input, one for each process
        for i in range(numProcesses):
            input_queue.put((Simulation.simulateWaterfall, (structuredSecurities, loanPool, int(NSIM / numProcesses))))
        # initialize processes
        for i in range(numProcesses):
            p = multiprocessing.Process(target=Simulation.doWork, args=(input_queue, output_queue))
            p.start()
            logging.info('Simulation.simulateWaterfallParallel(): 1 sub process started')
        # monitor output
        res = []
        while True:
            res.append(output_queue.get())
            # break if receive enough outputs
            if len(res) == numProcesses:
                for i in range(numProcesses):
                    p.terminate()
                    logging.info('Simulation.simulateWaterfallParallel(): 1 sub process terminated')
                break
        #res = [numProcesses lists of (avgDIRR_lst,avgAL_lst)]
        #goal: to transform res into the form of (avgDIRR_lst,avgAL_lst)
        avgDIRR_lst = [sum([i[0][t]for i in res]) / numProcesses for t in range(len(structuredSecurities.tranches))]
        avgAL_lst = [sum([i[1][t]for i in res]) / numProcesses for t in range(len(structuredSecurities.tranches))]
        return (avgDIRR_lst, avgAL_lst)




    @staticmethod
    def calculateYield(a,d):
        return ((7 / (1 + 0.08 * math.exp(-0.19 * (a/12)))) + (0.019*math.sqrt((a/12)*(d*100)))) / 100

    #runMonte
    @staticmethod
    def runMonte(structuredSecurities, loanPool,tolerance, NSIM, numProcesses):
        #this method assume structuredSecurities has 2 tranches
        coeff = [1.2, 0.8]
        #infinite loop
        while True:
            DIRR_lst, AL_lst = Simulation.simulateWaterfallParallel(structuredSecurities, loanPool, NSIM, numProcesses)
            Yield = [Simulation.calculateYield(AL_lst[i],DIRR_lst[i]) for i in range(2)]
            old_rate = [structuredSecurities.tranches[i].rate for i in range(2)]
            new_rate = [old_rate[i] + coeff[i] * (Yield[i] - old_rate[i]) for i in range(2)]
            notions = [structuredSecurities.tranches[i].notional for i in range(2)]
            diff = (notions[0] * abs((old_rate[0] - new_rate[0])/old_rate[0]) + notions[1] * abs((old_rate[1] - new_rate[1])/old_rate[1])) / structuredSecurities.notional
            if diff > tolerance:
                #update tranches rate to new_rate
                for i in range(2):
                    structuredSecurities.tranches[i].rate = new_rate[i]
            else:
                break
        return (DIRR_lst,AL_lst,new_rate)

