import logging
from Tranche.StructuredSecurities import StructuredSecurities
from Tranche.Tranches import StandardTranche
from Tranche.Tranche_base import Tranche
from Loan.Loan_pool import LoanPool
from Loan.Loans import FixedRateLoan
from Asset.Asset import Lexus
from Loan.Loans import AutoLoan
import datetime
from Simulation.Simulation import Simulation
import time

#function to create loan given input strings
def createLoan(LoanType,Balance,Rate,Term,asset,AssetVal):
    #arbitrary start date
    start = datetime.datetime.now()
    dt = datetime.timedelta(days = int(Term) * 30) #assuming 1 month = 30 days
    end = start + dt
    #dict to convert loan str to object
    loanNameToClass = {'Auto Loan': AutoLoan}
    # dict to convert Asset str to object
    assetNameToClass = {'Car': Lexus}
    assetCls = assetNameToClass.get(asset)
    if assetCls:
        asset = assetCls(float(AssetVal))
        loanCls = loanNameToClass.get(LoanType)
        if loanCls:
            loan = loanCls(start, end, float(Rate), float(Balance), asset)
            return loan
        else:
            logging.error('Invalid loan type entered.')
            raise TypeError('Invalid loan type entered.')
    else:
        logging.error('Invalid asset type entered.')
        raise TypeError('Invalid asset type entered.')

def read_csv(filename):
    loanPool = LoanPool([])
    with open(filename, 'r') as f:
        logging.info('read_csv(): reading csv file')
        cnt = 0
        # skip header line
        next(f)
        # loop thru each line
        for line in f:
            cnt += 1
            # strip \n and split line into parts
            data = line.strip('\n').rstrip(',').split(',')
            #remove id info
            data = data[1:]
            loan = createLoan(*data)
            if loan:
                loanPool.loans.append(loan)
        logging.info(f'{cnt} loans loaded.')
    logging.info('Finished reading and closed csv file')
    return loanPool

def write_csv(output,assetFileName,liabilityFilename):
    loan_lst = output[0]
    tranches_lst = output[1]
    reserve_lst = output[2]
    #asset csv
    with open(assetFileName,'w') as f:
        logging.info('write_csv(): writing asset csv')
        #write header line
        f.write('Period,Loan Pool Principal Due,LP Interest Due,LP Payment Due,LP Total Balance\n')
        for p, i in enumerate(loan_lst):
            f.write(f'{p},{i[0]},{i[1]},{i[2]},{i[3]}\n')
        logging.info('write_csv(): Finished writing and closed asset csv file')
    #liability csv
    with open(liabilityFilename, 'w') as f:
        logging.info('write_csv(): writing liability csv')
        #writing header
        f.write('Period,')
        #loop thru tranches at period 0
        #[intDue,intPaid,intShort,principalPaid,balance])
        cnt = 0 #counter
        for t in tranches_lst[0]:
            f.write(f'Tranche {cnt} Interest Due,Tranche {cnt} Interest Paid,Tranche {cnt} Interest Shortfall, Tranche {cnt} Principal Paid, Tranche {cnt} Ending Balance,')
            cnt += 1
        f.write('Reserve Account Balance,')
        f.write('\n')
        #writing data
        #loop thru periods
        for p in range(len(tranches_lst)):
            f.write(f'{p},')
            #loop thru each tranche
            for t in tranches_lst[p]:
                f.write(f'{t[0]},{t[1]},{t[2]},{t[3]},{t[4]},')
            #write reserve
            f.write(f'{reserve_lst[p]}\n')
        logging.info('write_csv(): Finished writing and closed liability csv file')




def main():

    #PART 1
    print('BEGINNING PART 1')
    logging.getLogger().setLevel(logging.INFO)
    #set to debug only where you want to debug so the message board is clean
    #test Tranche base init
    t1 = Tranche(10000,0.01,0) #worked
    #test tranche_base getters, all worked
    t1.notional
    t1.rate
    t1.subordination
    #test StandardTranche
    t2 = StandardTranche(10000,0.05,0) #worked
    #test getter
    t2.notional
    t2.period
    t2.interestShortfall
    t2.principalReceived
    t2.interestReceived
    t2.rate
    t2.subordination #all getters worked
    #test increaseTimePeriod
    t2.increaseTimePeriod() #worked
    #test interestDue()
    t2.interestDue() #worked
    #test makeInterestPayment()
    t2.makeInterestPayment(50) #worked
    #test notionalBalance
    t2.notionalBalance() #worked
    #test makePrincipalPayment
    t2.makePrincipalPayment(800) #worked
    #test reset
    t2.reset() #worked
    #test StructuredSecurity class
    p = StructuredSecurities(100000) #worked
    #test tranches getter
    p.tranches #worked
    p.reserveAccount #worked
    p.period #worked
    p.notional #worked
    #test addTranche
    p.addTranche(StandardTranche,0.8,0.1,0)
    #p.addTranche(Tranche,0.2,0.2,1) #this will cause error
    #p.addTranche(StandardTranche,0.3,0.2,1) #this will cause error
    p.addTranche(StandardTranche,0.2,0.15,1)
    #test setMode()
    #p.makePayments(10) #this will cause error since mode has not been set
    #p.setMode(2) #this will cause error
    p.setMode(1) #worked
    #test increaseTimePeriod
    p.increaseTimePeriod() #worked
    #test sequential payment
    p.makePayments(50000) #worked
    #reset and test again for pro-rata mode
    p.tranches_reset() #worked
    p.setMode(0)
    p.increaseTimePeriod()
    #test prorate payment
    p.makePayments(80000) #worked
    #test doWaterFall and getWaterfall
    p2 = StructuredSecurities(100000)
    p2.setMode(1)
    p2.addTranche(StandardTranche,0.8,0.1,0)
    p2.addTranche(StandardTranche, 0.2, 0.15, 1)
    #create a simple loan pool with 100k of 1 fixed rate loan
    start = datetime.datetime(2010,4,1)
    end = datetime.datetime(2010,5,1)
    loan = FixedRateLoan(start,end,0.2,p.notional,Lexus(100000))
    lP = LoanPool([loan])
    StructuredSecurities.doWaterfall(p2,lP) #worked
    #read csv file to LoanPool
    filename = r'C:\Users\binbe\Desktop\lesson\Quantnet Python\level 7 hw\case study\Loans.csv'
    loanPool = read_csv(filename)
    loansum = loanPool.totalBalance(0)
    #create structuredSec and Tranches
    strucSec = StructuredSecurities(loansum)
    strucSec.setMode(1)
    #add tranche 0
    strucSec.addTranche(StandardTranche, 0.7, 0.15,0)
    #add tranche 1
    strucSec.addTranche(StandardTranche,0.3,0.17,1)
    #doWaterfall sequential mode
    output = StructuredSecurities.doWaterfall(strucSec,loanPool)
    #write output to csv
    assetcsv = r'C:\Users\binbe\Desktop\lesson\Quantnet Python\level 7 hw\case study\assetWaterfallSequential.csv'
    liabcsv = r'C:\Users\binbe\Desktop\lesson\Quantnet Python\level 7 hw\case study\liabilityWaterfallSequential.csv'
    write_csv(output,assetcsv,liabcsv)
    #doWaterfall pro-rata mode
    #reset tranches periods and  loanPool's loans default status
    strucSec.tranches_reset()
    loanPool.default_reset()
    strucSec.setMode(0)
    output = StructuredSecurities.doWaterfall(strucSec, loanPool)
    # write output to csv
    assetcsv = r'C:\Users\binbe\Desktop\lesson\Quantnet Python\level 7 hw\case study\assetWaterfallProrata.csv'
    liabcsv = r'C:\Users\binbe\Desktop\lesson\Quantnet Python\level 7 hw\case study\liabilityWaterfallProrata.csv'
    write_csv(output, assetcsv, liabcsv)


    #PART 2
    #print out irr,dirr,al, and rating letter for each tranche
    print('BEGINNING PART 2')
    for t in range(len(strucSec.tranches)):
        irr = output[3][t]
        print(f'IRR for tranche {t} = {irr}')
        dirr = output[4][t]
        print(f'DIRR for tranche {t} = {dirr}')
        al = output[5][t]
        print(f'Average Life of tranche {t} = {al}')
        rating = output[6][t]
        print(f'Letter rating for tranche {t}: {rating}')


    #PART 3
    #note that everytime we run main, DIRR and AL of tranches are different
    #Monte Carlo simulation
    #Simulation.simulateWaterfall(strucSec,loanPool,2000))
    #this took 12349.579906225204 seconds (3-4 hours) to run, I guess my computer is just slow
    #test runMonte
    #reinitialise loanpool and structuredsec according to given description
    # read csv file to LoanPool
    print('BEGINNING PART 3')
    filename = r'C:\Users\binbe\Desktop\lesson\Quantnet Python\level 7 hw\case study\Loans.csv'
    loanPool = read_csv(filename)
    loansum = loanPool.totalBalance(0)
    # create structuredSec and Tranches
    strucSec = StructuredSecurities(loansum)
    strucSec.setMode(1)
    # add tranche 0
    strucSec.addTranche(StandardTranche, 0.8, 0.05, 0)
    # add tranche 1
    strucSec.addTranche(StandardTranche, 0.2, 0.08, 1)
    print(Simulation.runMonte(strucSec,loanPool,0.005,2000,5)) #worked as expected






















if __name__ == '__main__':
    main()