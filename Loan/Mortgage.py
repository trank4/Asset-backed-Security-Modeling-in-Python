from Loan.Loans import VariableRateLoan,FixedRateLoan
from Asset.Asset import HouseBase
import datetime
import logging

class MortgageMixin(object):
    #MortgageMixin needs __init__ because it is derived from object
    def __init__(self, startdate, enddate, rate,notional,home):

        #check if home is HouseBase object
        if not isinstance(home,HouseBase):
            raise TypeError('Error: home parameter has to be an HouseBase (derived) object')
        # check if startdate and enddate are datetime object
        if not isinstance(startdate, datetime.datetime):
            logging.error('Error in __init__ of MortgageMixin: startdate has to be an datetime object ')
            raise TypeError('Error: startdate has to be an datetime object')
        if not isinstance(enddate, datetime.datetime):
            logging.error('Error in __init__ of MortgageMixin: enddate has to be an datetime object ')
            raise TypeError('Error: enddate has to be an datetime object')
        super(MortgageMixin,self).__init__(startdate, enddate,rate,notional,home)

    def PMI(self,period):
        balance = super(MortgageMixin,self).balance(period)
        #modified to calculate LTV based on asset value
        val = super(MortgageMixin,self).asset.Value(0)
        #if balance is >= 80% of face value
        if balance >= (0.8*val):
            return 0.000075*val
        else:
            return 0

    def monthlyPayment(self, period=1):
        #check if period is valid
        if period <= 0:
            raise ValueError('Error: period cannot be negative or = 0')
        payment = super(MortgageMixin,self).monthlyPayment(period)
        return payment + self.PMI(period)

    def principalDue(self, period):
        return super(MortgageMixin,self).principalDue(period) - self.PMI(period)

    def principalDueRecursive(self,period):
        return super(MortgageMixin,self).principalDueRecursive(period) - self.PMI(period)

class VariableMortgage(MortgageMixin,VariableRateLoan):
    pass

class FixedMortgage(MortgageMixin,FixedRateLoan):
    pass



