from Asset.Asset import Asset
import logging
import datetime
from utils.decorators import Memoize



class Loan(object):
    #modified init to add asset parameter

    def __init__(self,startdate,enddate,annualrate,notional,asset):
        #note that rate is annualized basis
        logging.debug('__init__ of Loan executed')
        # check if startdate and enddate are datetime object
        if not isinstance(startdate, datetime.datetime):
            logging.error('Error in __init__ of Loan: startdate has to be an datetime object ')
            raise TypeError('Error: startdate has to be an datetime object')
        if not isinstance(enddate, datetime.datetime):
            logging.error('Error in __init__ of Loan: enddate has to be an datetime object ')
            raise TypeError('Error: enddate has to be an datetime object')
        # check if asset is Asset object
        if not isinstance(asset, Asset):
            logging.error('Error in __init__ of Loan: asset parameter has to be an Asset object ')
            raise TypeError('Error: asset parameter has to be an Asset object')
        self._startdate = startdate
        self._enddate = enddate
        self._rate = annualrate
        logging.debug(f'Initialized _rate attribute to {self._rate}')
        self._notional = notional
        logging.debug(f'Initialized _notional attribute to {self._notional}')

        self._asset = asset
        logging.debug(f'Initialized _asset attribute to {(self._asset)}')
        #flag to track default, 1 = defaulted, 0 otherwise
        self._default = 0
        logging.debug(f'Initialized _default attribute to {(self._default)}')

    #abstract method
    def getRate(self,period):
        #to be overwritten by derived class
        logging.error('Error in getRate() of Loan: Abstract function is not implemented')
        raise NotImplementedError()
    #term function
    @property
    def term(self):
        # timedelta obj
        term = self._enddate - self._startdate
        # term in months
        days = term.days + term.seconds / (3600 * 24) + term.microseconds / (1000000 * 3600 * 24)
        #assuming 30 days a month
        month = round(days / 30)
        return month
    #getters

    @property
    def rate(self):
        logging.debug(f'rate() returning _rate attribute as {self._rate}')
        return self._rate
    @property
    def notional(self):
        logging.debug(f'notional() returning _notional attribute as {self._notional}')
        return self._notional
    #getter for asset
    @property
    def asset(self):
        logging.debug(f'asset() returning _asset attribute as {self._asset}')
        return self._asset
    #setters
    @rate.setter
    def rate(self,r):
        logging.debug(f'rate() setting _rate attribute to {r}')
        self._rate = r

    @notional.setter
    def notional(self,f):
        logging.debug(f'notional() setting _notional attribute to {f}')
        self._notional = f
    #setter for asset
    @asset.setter
    def asset(self,asset):
        #check if a is an Asset object
        if not isinstance(asset, Asset):
            logging.error('Error in asset() of Loan: asset parameter has to be an Asset object')
            raise TypeError('Error: asset parameter has to be an Asset object')
        logging.info('asset is an Asset object')
        logging.debug(f'asset() setting _asset attribute to {asset}')
        self._asset = asset
        # class-level payment method

    #static methods

    @staticmethod
    def monthlyRate(annual):
        res = annual/12
        logging.debug(f'monthlyRate() returns {res}')
        return res

    @staticmethod
    def annualRate(monthly):
        res = monthly *12
        logging.debug(f'annualRate() returns {res}')
        return res

    @classmethod
    def calcMonthlyPmt(cls, face, annualrate, term):
        monthlyrate = Loan.monthlyRate(annualrate)
        logging.debug(f'Loan_base.calcMonthlyPmt(): calculated annualized rate to monthly rate = {monthlyrate}')
        res = (monthlyrate * face) / (1 - (1 + monthlyrate) ** (-term))
        logging.debug(f'Loan_base.calcMonthlyPmt(): returns = {res}')
        return res

    # cls-level balance method
    @classmethod
    def calcBalance(cls, face, annualrate, term, period):
        #note that the balance is after every payment is made
        monthlyrate = Loan.monthlyRate(annualrate)
        logging.debug(f'Loan_base.calcBalance(): monthly Rate = {monthlyrate}')
        monthlypayment = cls.calcMonthlyPmt(face, annualrate, term)
        logging.debug(f'Loan_base.calcBalance(): monthly payment = {monthlypayment}')
        res = face * (1 + monthlyrate) ** period - monthlypayment * (((1 + monthlyrate) ** period - 1) / (monthlyrate))
        logging.debug(f'calcBalance() returns = {res}')
        return res


    # re-written payment method
    # modified to use getRate()
    def monthlyPayment(self,period = 1):
        #check if period > 0
        if period <= 0:
            logging.error('Loan_base.monthlyPayment(): period cannot be <= 0 ')
            raise ValueError('Error: period cannot be negative or = 0')
        #check if period is > than existing period of loan
        if period > self.term:
            logging.debug(f'Loan_base.monthlyPayment(): period parameter {period} exceeds existence of the loan,{self.term}, returning 0')
            return 0
        #if the loan default, it does not pay monthly payment anymore
        if self._default == 1:
            logging.debug(f'Loan_base.monthlyPayment(): loan defaulted, returning 0')
            return 0
        res = self.calcMonthlyPmt(self._notional,self.getRate(period),self.term)
        logging.debug(f'Loan_base.monthlyPayment(): returns {res}')
        return res

    #total payments assuming that the loan doesn't default in its lifetime
    def totalPayments(self):
        #loop through terms 1 to end
        sum = 0
        for t in range(1, self.term + 1):
            sum += self.monthlyPayment(t)
        logging.debug(f'totalPayments() returns {sum}')
        return sum
    #total interest paid assuming no default
    def totalInterest(self):
        res = self.totalPayments() - self._notional
        logging.debug(f'totalInterest() returns {res}')
        return res

    #methods for balance, interest due. principal due using formula
    # re-written balance method
    # modified to use getRate()
    def balance(self,period):
        if period < 0:
            logging.error('Error in balance() of Loan: period cannot be negative')
            raise ValueError('Error: period cannot be negative')
        if period > self.term:
            logging.debug(f'Loan_base.balance(): period parameter {period} exceeds existence of the loan,{self.term}, returning 0')
            return 0
        if self._default == 1:
            logging.debug(f'Loan_base.balance(): loan defaulted, returning 0')
            return 0
        res = self.calcBalance(self._notional,self.getRate(period),self.term,period)
        logging.debug(f'Loan_base.balance(): balance = {res}')
        return res

    # modified to use getRate()
    def interestDue(self, period):
        if period == 0:
            logging.error('Error in interestDue() of Loan: no due for period 0')
            raise ValueError('Error: no due for period 0')
        if period < 0:
            logging.error('Error in interestDue() of Loan: period cannot be negative')
            raise ValueError('Error: period cannot be negative')
        if period > self.term:
            logging.debug(f'Loan_base.interestDue(): period parameter {period} exceeds existence of the loan,{self.term}, returning 0')
            return 0
        rate = Loan.monthlyRate(self.getRate(period))
        logging.debug(f'interestDue() calculated monthly rate = {rate}')
        res = rate * self.balance(period - 1)
        logging.debug(f'interestDue() returns {res}')
        return res

    def principalDue(self,period):
        if period == 0:
            logging.error('Error in principalDue() of Loan: no due for period 0')
            raise ValueError('Error: no due for period 0')
        if period < 0:
            logging.error('Error in principal Due() of Loan: period cannot be negative')
            raise ValueError('Error: period cannot be negative')
        if period > self.term:
            logging.debug(f'Loan_base.principalDue(): period parameter {period} exceeds existence of the loan,{self.term}, returning 0')
            return 0
        res = self.monthlyPayment(period)-self.interestDue(period)
        logging.debug(f'principalDue() returns {res}')
        return res

    #methods use recursive
    @Memoize
    def balanceRecursive(self, period):
        # base case
        if period == 0:
            logging.warning('balanceRecursive is expected to have long runtime. Thus, balance() is recommended')
            logging.info('period = 0')
            return self._notional
        # recursion
        elif period > 0:
            interestdue = (Loan.monthlyRate(self.getRate(period))) * self.balanceRecursive(period - 1)
            logging.debug(f'balanceRecursive() calculated interestdue = {interestdue}')
            principaldue = self.monthlyPayment(period) - interestdue
            logging.debug(f'balanceRecursive() calculated principaldue = {principaldue}')
            balance = self.balanceRecursive(period - 1) - principaldue
            logging.debug(f'balanceRecursive() returns balance = {balance}')
            return balance
        else:
            logging.error('Error in balanceRecursive() of Loan: period cannot be negative')
            raise ValueError('Error: period cannot be negative')

    @Memoize
    def interestDueRecursive(self, period):
        logging.warning('interestDueRecursive is expected to have long runtime. Thus, interestDue() is recommended')
        if period == 0:
            logging.error('Error in interestDueRecursive() of Loan: no due for period 0')
            raise ValueError('Error: no due for period 0')
        if period < 0:
            logging.error('Error in interestDueRecursive() of Loan: period cannot be negative')
            raise ValueError('Error: period cannot be negative')
        rate = Loan.monthlyRate(self.getRate(period))
        res = rate * self.balanceRecursive(period - 1)
        logging.debug(f'interestDueRecursive() returns {res}')
        return res

    @Memoize
    def principalDueRecursive(self,period):
        logging.warning('principalDueRecursive is expected to have long runtime. Thus, principleDue() is recommended')
        if period == 0:
            logging.error('Error in principalDueRecursive() of Loan: no due for period 0')
            raise ValueError('Error: no due for period 0')
        if period < 0:
            logging.error('Error in principalDueRecursive() of Loan: period cannot be negative')
            raise ValueError('Error: period cannot be negative')
        res = self.monthlyPayment()-self.interestDueRecursive(period)
        logging.debug(f'principalDueRecursive() returns {res}')
        return res

    #recoveryValue method
    def recoveryValue(self,period):
        recovery_multiplier = 0.6
        logging.debug(f'recovery multiplier is set at {recovery_multiplier}')
        res = self.asset.Value(period) * recovery_multiplier
        logging.debug(f'recoveryValue() returns {res}')
        return res

    #equity method
    def equity(self,period):
        loan = self.balance(period)
        logging.debug(f'equity() calculated loan balance at period {period} = {loan}')
        asst = self.asset.Value(period)
        logging.debug(f'equity() calculated asset value at period {period} = {asst}')
        logging.debug(f'equity() returns equity value at period {period} = {asst-loan}')
        return asst - loan

    #static method to return default probability
    @staticmethod
    def DefaultProb(period):
        #create a dictionary that include the upper bounds of period and probability
        prob_dict = {10:0.0005,59:0.001,120:0.002,180:0.004,210:0.002,360:0.001}
        #sort keys
        keys = sorted(prob_dict.keys())
        cnt = 0
        # loop until bps is <= keys[cnt] while increasing cnt because the given values is the upper bound
        while period > keys[cnt]:
            cnt += 1
        return prob_dict[keys[cnt]]

    #checkDefault
    def checkDefault(self,randnum):
        #if randnum == 0, the loan is flag as default
        if randnum == 0:
            #switch default flag to 1
            self._default = 1

    #getter for default status
    @property
    def default(self):
        return self._default

    #setter for default status
    @default.setter
    def default(self, d):
        logging.debug(f'default(): setting _default attribute to {d}')
        self._default = d



