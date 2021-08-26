from Loan.Loan_base import Loan
import sys
from Asset.Asset import CarMixin
import logging
import datetime

#FixedRateLoan
class FixedRateLoan(Loan):
    # overide getRate()
    def getRate(self,period):
        return self._rate

#VariableRateLoan
#modified to add Asset
class VariableRateLoan(Loan):
    def __init__(self,startdate,enddate,rateDict,face,asset):
        #check if not dict then error
        if not isinstance(rateDict,dict):
            raise TypeError('Error: rateDict in VariableRateLoan must be dictionary type')
        # check if startdate and enddate are datetime object
        if not isinstance(startdate, datetime.datetime):
            logging.error('Error in __init__ of VariableRateLoan: startdate has to be an datetime object ')
            raise TypeError('Error: startdate has to be an datetime object')
        if not isinstance(enddate, datetime.datetime):
            logging.error('Error in __init__ of VariableRateLoan: enddate has to be an datetime object ')
            raise TypeError('Error: enddate has to be an datetime object')
        self._rateDict = rateDict
        super(VariableRateLoan, self).__init__(startdate,enddate,None,face,asset)

    #overide getRate()
    def getRate(self,period):
        #sort the keys in increasing order
        key = sorted(self._rateDict.keys())
        #count backward until the period is >= the key value
        count = len(key) - 1
        while period < key[count]:
            count -= 1
        return self._rateDict.get(key[count])

#AutoLoan
class AutoLoan(FixedRateLoan):
    def __init__(self, startdate, enddate, rate, notional, car):
        #check if car is CarMixin object
        if not isinstance(car,CarMixin):
            raise TypeError('Error: car parameter has to be an CarMixin (derived) object')
        # check if startdate and enddate are datetime object
        if not isinstance(startdate, datetime.datetime):
            logging.error('Error in __init__ of AutoLoan: startdate has to be an datetime object ')
            raise TypeError('Error: startdate has to be an datetime object')
        if not isinstance(enddate, datetime.datetime):
            logging.error('Error in __init__ of AutoLoan: enddate has to be an datetime object ')
            raise TypeError('Error: enddate has to be an datetime object')
        super(AutoLoan,self).__init__(startdate, enddate, rate, notional, car)


