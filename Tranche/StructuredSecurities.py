from Tranche.Tranches import StandardTranche
from Tranche.Tranche_base import Tranche
import logging

class StructuredSecurities (object):

    def __init__(self,notional):
        self._notional = notional
        logging.debug(f'StructuredSecurities.__init__: _notional = {self._notional}')
        self._tranches = []
        logging.debug(f'StructuredSecurities.__init__: _tranches = {self._tranches}')
        #flag to determine if sequential, 1 for sequential, 0 for pro-rata
        self._sequential = None
        logging.debug(f'StructuredSecurities.__init__: _sequential = {self._sequential}')
        #reserve account for excess cash
        self._reserveAccount = 0
        logging.debug(f'StructuredSecurities.__init__: _reserveAccount = {self._reserveAccount}')
        #totalPercent to track total percent add up to 1
        self._totalPercent = 0
        logging.debug(f'StructuredSecurities.__init__: _totalPercent = {self._totalPercent}')
        #period flag to track period of structuredsecuities object
        self._period = 0
        logging.debug(f'StructuredSecurities.__init__: _period = {self._period}')

    #getter for period
    @property
    def period(self):
        logging.debug(f'StructuredSecurities.period getter: {self._period}')
        return self._period

    #getter for tranches
    @property
    def tranches(self):
        logging.debug(f'StructuredSecurities.tranches getter: {self._tranches}')
        return self._tranches

    #getter for reserveAccount
    @property
    def reserveAccount(self):
        logging.debug(f'StructuredSecurities.reserveAccount getter: {self._reserveAccount}')
        return self._reserveAccount

    # getter for notional
    @property
    def notional(self):
        logging.debug(f'StructuredSecurities.notional getter: {self._notional}')
        return self._notional

    #method to add tranches
    def addTranche(self, trancheClass, percentOfNotion, annualrate, subordination):
        #check if percent add up to <= 1
        newPerc = self._totalPercent + percentOfNotion
        if newPerc > 1:
            logging.error(f'StructuredSecurities.addTranche(): total percent of tranches = {newPerc}')
            raise ValueError('Total percent of tranches notions exceeds 1')
        #update _totalPercent if valid
        self._totalPercent = newPerc
        logging.debug(f'StructuredSecurities.addTranche(): total percent of tranches = {self._totalPercent}')
        #list of valid trache type, extend as you have more type of tranche
        lst = [StandardTranche]
        if trancheClass not in lst:
            logging.error(f'StructuredSecurities.addTranche(): {trancheClass} is not in {lst}')
            raise TypeError('invalid tranche input')
        trancheNotional = percentOfNotion * self._notional
        logging.debug(f'StructuredSecurities.addTranche(): tranche notion = {trancheNotional}')
        logging.debug(f'StructuredSecurities.addTranche(): adding tranche to _tranches')
        self._tranches.append(trancheClass(trancheNotional,annualrate,subordination))
        logging.debug(f'StructuredSecurities.addTranche(): _tranches contains {self._tranches}')

    #method to set sequential or pro-rata modes, 1 for sequential, 0 otherwise
    def setMode(self,seqBool):
        #check if input is valid
        if seqBool not in [0,1]:
            logging.error(f'StructuredSecurities.setMode(): invalid seqBool = {seqBool}')
            raise ValueError('Mode input is invalid')
        self._sequential = seqBool
        logging.debug(f'StructuredSecurities.setMode(): set _sequential to {self._sequential}')

    #method to increase time period for each tranche
    def increaseTimePeriod(self):
        logging.debug(f'StructuredSecurities.increaseTimePeriod(): increase time period for each tranche in _tranches')
        for t in self._tranches:
            t.increaseTimePeriod()
            logging.debug(f'StructuredSecurities.increaseTimePeriod():period of {t} is currently {t.period}')
        self._period +=1

    #method to make payment to each tranche
    def makePayments(self,cash_amount):
        #check if mode is set
        if self._sequential is None:
            logging.error(f'StructuredSecurities.makePayments(): Payment mode has not been set, _sequential = {self._sequential}')
            raise ValueError('_sequential type is invalid')
        availableFund = cash_amount + self._reserveAccount
        logging.debug(f'StructuredSecurities.makePayments(): availableFund = {availableFund}')
        #sort tranches in order of subordination from low to high
        logging.debug(f'StructuredSecurities.makePayments(): sort _tranches by subordination from low to high')
        self._tranches.sort(key = lambda x: x.subordination)
        logging.debug(f'StructuredSecurities.makePayments(): _tranches after sorting = {self._tranches}')
        #cycle thru each tranche to pay interest
        for t in self._tranches:
            logging.debug(f'StructuredSecurities.makePayments(): looping thru {t}')
            #interest owed, previous shortfall included, the tranche track its own interest shortfall
            owed = t.interestDue() + t.interestShortfall
            logging.debug(f'StructuredSecurities.makePayments(): interest due + shortfall = {owed}')
            #check if the tranche is already paid off
            if owed == 0:
                # if the tranche is already paid off, we don't need to pay, skip iteration
                logging.debug(f'StructuredSecurities.makePayments(): tranche {t} is paid off, skip iteration')
                logging.debug(f'StructuredSecurities.makePayments(): remaining availableFund = {availableFund}')
                continue
            logging.debug(f'StructuredSecurities.makePayments(): remaining availableFund = {availableFund}')
            #if we have enough fund, we'll pay all owed, if not, we'll pay as much as we can
            payment = min(availableFund,owed)
            logging.debug(f'StructuredSecurities.makePayments(): payment to the tranche = {payment}')
            t.makeInterestPayment(payment)
            logging.debug(f'StructuredSecurities.makePayments(): interest payment made')
            availableFund -= payment

        #cycle thru each tranche to pay principal
        #case 1: sequential payment (make maximum principal payment at each tranche)
        if self._sequential == 1:
            logging.debug(f'StructuredSecurities.makePayments(): sequential mode')
            for t in self._tranches:
                logging.debug(f'StructuredSecurities.makePayments(): looping thru {t}')
                #note that balance will reflect the remaining principal for every period
                #thus, no need to track principal shortfall, since balance = (notional - received) (which is already principal shortfall) + interest shortfall
                balance = t.notionalBalance()
                logging.debug(f'StructuredSecurities.makePayments(): notional balance = {balance}')
                #check if the trache is paid off
                if balance == 0:
                    # if the tranche is already paid off, we don't need to pay, skip iteration
                    logging.debug(f'StructuredSecurities.makePayments(): tranche {t} is paid off, skip iteration')
                    logging.debug(f'StructuredSecurities.makePayments(): remaining availableFund = {availableFund}')
                    continue
                logging.debug(f'StructuredSecurities.makePayments(): remaining availableFund = {availableFund}')
                payment = min(balance,availableFund)
                logging.debug(f'StructuredSecurities.makePayments(): payment to the tranche = {payment}')
                t.makePrincipalPayment(payment)
                logging.debug(f'StructuredSecurities.makePayments(): principal payment made')
                availableFund -= payment
        # case 2: pro-rata
        elif self._sequential == 0:
            logging.debug(f'StructuredSecurities.makePayments(): pro-rata mode')
            #what left after paying interests
            principal_payment = availableFund
            logging.debug(f'StructuredSecurities.makePayments(): principal received = {principal_payment}')
            for t in self._tranches:
                logging.debug(f'StructuredSecurities.makePayments(): looping thru {t}')
                percent = t.notional / self._notional
                logging.debug(f'StructuredSecurities.makePayments(): notional percent = {percent}')
                prorataprincipal = percent * principal_payment
                logging.debug(f'StructuredSecurities.makePayments(): pro-rata principal = {prorataprincipal}')
                balance = t.notionalBalance()
                logging.debug(f'StructuredSecurities.makePayments(): notional balance = {balance}')
                # check if the trache is paid off
                if balance == 0:
                    # if the tranche is already paid off, we don't need to pay, skip iteration
                    logging.debug(f'StructuredSecurities.makePayments(): tranche {t} is paid off, skip iteration')
                    logging.debug(f'StructuredSecurities.makePayments(): remaining availableFund = {availableFund}')
                    continue
                logging.debug(f'StructuredSecurities.makePayments(): remaining availableFund = {availableFund}')
                payment = min(prorataprincipal,balance,availableFund)
                logging.debug(f'StructuredSecurities.makePayments(): payment = {payment}')
                t.makePrincipalPayment(payment)
                logging.debug(f'StructuredSecurities.makePayments(): principal payment made')
                availableFund -= payment
        #add available fund leftover to reserve
        self._reserveAccount += availableFund
        logging.debug(f'StructuredSecurities.makePayments(): reserve Account increases by {availableFund} to {self._reserveAccount}')

    #reset function to reset all tranches in structure back to period 0
    def tranches_reset(self):
        #reset reserveAccount and period
        self._reserveAccount = 0
        logging.debug(f'StructuredSecurities.tranches_reset(): _reserveAccount = {self._reserveAccount}')
        self._period = 0
        logging.debug(f'StructuredSecurities.tranches_reset(): _period = {self._period}')
        for t in self._tranches:
            logging.debug(f'StructuredSecurities.tranches_reset(): looping thru {t}')
            t.reset()

    #I used staticmethod for getWaterfall and doWaterfall because logically they follow a StructuredSecurities class
    #although they don't belong to the class or object levels
    # standalone method to return list of lists that contain info of each tranche for the given period
    @staticmethod
    def getWaterfall(structuredSecurity, loanPool,period):
        #note that structuredSecurity is already updated to the given period
        #the output of getWaterFall should be [assetlist,lists of liability tranches,Reserve Account]
        #with assetlist = [principal,interest, total, balance] for the given period
        #and liability = lists of [tranches info] for each period
        #so output[0] is always info of the loan pool at the given period
        #output[-1] is always reserve account at the given period
        lst = []
        logging.debug(f'structuredSecurities.getWaterFall(): created empty list lst = {lst} ')
        #loan info
        linterest = loanPool.interestDue(period)
        logging.debug(f'structuredSecurities.getWaterFall(): loan pool interest due at period {period} = {linterest} ')
        lpayment = loanPool.paymentDue(period)
        logging.debug(f'structuredSecurities.getWaterFall(): loan pool payment due at period {period} = {lpayment} ')
        lprincipal = lpayment -linterest
        logging.debug(f'structuredSecurities.getWaterFall(): loan pool principal due at period {period} = {lprincipal} ')
        lbalance = loanPool.totalBalance(period)
        logging.debug(f'structuredSecurities.getWaterFall(): loan pool balance at period {period} = {lbalance} ')
        lst.append([lprincipal,linterest,lpayment,lbalance])
        logging.debug(f'structuredSecurities.getWaterFall(): appended loan info to lst = {lst} ')
        #loop thru each tranche in structuredSecurities at the given period
        for t in structuredSecurity.tranches:
            logging.debug(f'structuredSecurities.getWaterFall(): looping thru {t}')
            #interest Due
            intDue = t.interestDue()
            logging.debug(f'structuredSecurities.getWaterFall(): tranche interest due at period {period} = {intDue}')
            #interest shortfall
            intShort = t.interestShortfall
            logging.debug(f'structuredSecurities.getWaterFall(): tranche interest shortfall at period {period} = {intShort}')
            #interest Paid for the period
            intPaid = t.interestReceived
            logging.debug(f'structuredSecurities.getWaterFall(): tranche interest paid at period {period} = {intPaid}')
            #principal paid for the period
            principalPaid = t.principalReceived
            logging.debug(f'structuredSecurities.getWaterFall(): tranche principal paid at period {period} = {principalPaid}')
            #balance of the tranche at the period
            balance = t.notionalBalance()
            logging.debug(f'structuredSecurities.getWaterFall(): tranche balance at period {period} = {balance}')
            #append these into lst
            lst.append([intDue,intPaid,intShort,principalPaid,balance])
        reserve = structuredSecurity.reserveAccount
        logging.debug(f'structuredSecurities.getWaterFall(): reserve account balance at period {period} = {reserve}')
        lst.append(reserve)
        logging.debug(f'structuredSecurities.getWaterFall(): returning lst = {lst}')
        return lst


    # static method doWaterfall
    @staticmethod
    def doWaterfall(structuredSecurity, loanPool):
        #structuredSecurity and loanPool is initially at period 0
        #use while true loop to find time period until loan pool has no more active loans
        period = 0
        logging.debug(f'structuredSecurities.doWaterFall(): initialize period = {period}')
        loan_lst = [[0,0,0,loanPool.totalBalance(0)]]
        logging.debug(f'structuredSecurities.doWaterFall(): loan_lst at period 0= {loan_lst}')
        tranches_lst = []
        zero_period_tranches = []
        for t in structuredSecurity.tranches:
            zero_period_tranches.append([0,0, 0, 0, t.notionalBalance()])
        tranches_lst.append(zero_period_tranches)
        logging.debug(f'structuredSecurities.doWaterFall(): tranches_lst at period 0 = {tranches_lst}')
        reserve_lst = [0]
        logging.debug(f'structuredSecurities.doWaterFall(): reserve_lst at period 0= {reserve_lst}')
        while True:
            # increase period
            period += 1
            logging.debug(f'structuredSecurities.doWaterFall(): period = {period}')
            #for each period, check defaults
            recoveryValue = loanPool.checkDefaults(period)
            # increase period on StructuredSecurities
            structuredSecurity.increaseTimePeriod()
            logging.debug(f'structuredSecurities.doWaterFall(): structured security period = {structuredSecurity.period}')
            #Ask the LoanPool for its total payment for the current time period, add the recovery value
            totalpayment = loanPool.paymentDue(period) + recoveryValue
            logging.debug(f'structuredSecurities.doWaterFall(): total payment from loan pool = {totalpayment}')
            #Pay the StructuredSecurities with the amount provided by the LoanPool.
            structuredSecurity.makePayments(totalpayment)
            logging.debug(f'structuredSecurities.doWaterFall(): structured security period = {structuredSecurity.period}')
            #call getWaterfall()
            logging.debug(f'structuredSecurities.doWaterFall(): calling getWaterFall()')
            infolst = StructuredSecurities.getWaterfall(structuredSecurity,loanPool,period)
            #note that infolst is a list of lists with infolst[0] is the loan infos and the follwing lists
            #are info for each tranche
            #append loan info to loan_lst
            loan_lst.append(infolst[0])
            logging.debug(f'structuredSecurities.doWaterFall(): appended to loan_lst = {infolst[0]}')
            #append tranches info to tranches_lst
            tranches_lst.append(infolst[1:-1])
            logging.debug(f'structuredSecurities.doWaterFall(): appended to tranches_lst = {infolst[1:-1]}')
            # append reserve info to reserve_lst
            reserve_lst.append(infolst[-1])
            logging.debug(f'structuredSecurities.doWaterFall(): appended to reserve_lst = {infolst[-1]}')
            # check if loan pool has active loan for the current period
            # note that balance of loan is calculated after all payment is made
            if loanPool.activeLoanCount(period) == 0:
                logging.debug('doWaterfall(): loan Pool has no more active loan')
                logging.debug('doWaterfall(): break while true loop')
                break
        logging.debug(f'structuredSecurities.doWaterFall(): returning loan_lst = {loan_lst}')
        logging.debug(f'structuredSecurities.doWaterFall(): returning tranches_lst = {tranches_lst}')
        logging.debug(f'structuredSecurities.doWaterFall(): returning reserve_lst = {reserve_lst}')
        #add metrics for each tranche
        #irr_lst contains IRR for each tranche
        irr_lst = []
        dirr_lst = []
        al_lst =[]
        rating_lst = []
        for t in range(len(structuredSecurity.tranches)):
            #IRR
            #get cashflow list from tranche_lst
            #get tranche notion for the initial cashflow
            tranche_notion = tranches_lst[0][t][4]
            cashflow = [-tranche_notion]
            #create a list of following payments and extend the cashflow
            payments = [tranches_lst[i][t][1]+tranches_lst[i][t][3] for i in range(1,len(tranches_lst))]
            cashflow.extend(payments)
            #append irr_lst
            irr_lst.append(Tranche.IRR(cashflow))
            #DIRR
            # dirr of tranche
            dirr = structuredSecurity.tranches[t].DIRR(cashflow)
            # append dirr_lst
            dirr_lst.append(dirr)
            #AL
            #list of principal payments
            principaldues = [tranches_lst[i][t][3] for i in range(len(tranches_lst))]
            #al of tranche
            al = structuredSecurity.tranches[t].AL(principaldues)
            #append al_lst
            al_lst.append(al)
            #rate the tranche
            rating = Tranche.letterRating(dirr)
            #append to rating_lst
            rating_lst.append(rating)
        logging.debug(f'structuredSecurities.doWaterFall(): returning irr_lst = {irr_lst}')
        logging.debug(f'structuredSecurities.doWaterFall(): returning dirr_lst = {dirr_lst}')
        logging.debug(f'structuredSecurities.doWaterFall(): returning al_lst = {al_lst}')
        logging.debug(f'structuredSecurities.doWaterFall(): returning rating_lst = {rating_lst}')
        #return a tuple that contains info of loans thru periods, info of each tranche thru periods, and ending reserve Account
        return (loan_lst,tranches_lst,reserve_lst,irr_lst,dirr_lst,al_lst,rating_lst)





















