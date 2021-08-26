#abstract base class Tranche
import logging
import numpy_financial as npf
import functools as ft
class Tranche(object):
    def __init__(self,notional,annualrate,subordination):
        self._notional = notional
        logging.debug(f'Tranche.__init__: _notional = {self._notional}')
        #rate: input as annualized but stored as monthly basis
        self._rate = Tranche.monthlyRate(annualrate)
        logging.debug(f'Tranche.__init__: _rate (stored at monthly rate) = {self._rate}')
        #flag to record the subordination
        self._subordination = subordination
        logging.debug(f'Tranche.__init__: _subordination = {self._subordination}')

    # getter for notional
    @property
    def notional(self):
        logging.debug(f'Tranche_base.notional getter: {self._notional}')
        return self._notional

    # getter for rate
    @property
    def rate(self):
        logging.debug(f'Tranche_base.rate getter: {self._rate}')
        return self._rate *12 #must return annulized rate

    # getter for subordination
    @property
    def subordination(self):
        logging.debug(f'Tranche_base.subordination getter: {self._subordination}')
        return self._subordination

    #setter for rate
    @rate.setter
    def rate(self,r):
        self._rate = Tranche.monthlyRate(r) #must store as monthly rate

    #static method to convert annualized rate to monthly rate
    @staticmethod
    def monthlyRate(annual):
        res = annual / 12
        logging.debug(f'Tranche_base.monthlyRate(): monthly rate = {res}')
        return res

    #some abstract methods serve as API for tranches classes
    def increaseTimePeriod(self):
        raise NotImplementedError()

    def makePrincipalPayment(self, payment):
        raise NotImplementedError()

    def makeInterestPayment(self, payment):
        raise NotImplementedError()

    #IRR method that returns annualized IRR
    @staticmethod
    def IRR(cashflows):
        rate_monthly = npf.irr(cashflows)
        logging.debug(f'Tranche_base.IRR(): monthly IRR = {rate_monthly}')
        rate_annual = rate_monthly * 12
        logging.debug(f'Tranche_base.IRR(): annualized IRR = {rate_annual}')
        return rate_annual

    #DIRR method that returns annualized DIRR
    def DIRR(self,cashflows):
        dirr = round(Tranche.IRR(cashflows) - (self._rate * 12),6)
        logging.debug(f'Tranche_base.DIRR(): annualized DIRR = {dirr} ')
        return dirr

    #AL method
    def AL(self,principal_list):
        #check if the tranche is not paid down to 0, that sum of principal payments is different from initial notional
        if round(sum(principal_list) - self._notional,6) != 0:
            return None
        res = ft.reduce(lambda total, tup: total + tup[0]*tup[1],enumerate(principal_list),0) / self._notional
        return res

    #static method to return letter rating
    @staticmethod
    def letterRating(dirr):
        # have to round dirr since dirr can have negative value but very close to 0
        bps = dirr * 10000
        rating_dict = {0.06: 'Aaa', 0.67: 'Aa1', 1.3: 'Aa2', 2.7: 'Aa3', 5.2: 'A1', 8.9: 'A2', 13: 'A3', 19: 'Baa1',
                       27: 'Baa2', 46: 'Baa3', 72: 'Ba1', 106: 'Ba2', 143: 'Ba3', 183: 'B1', 231: 'B2', 311: 'B3',
                       2500: 'Caa', 10000: 'Ca'}
        keys = sorted(rating_dict.keys())
        cnt = 0
        # loop until bps is <= keys[cnt] while increasing cnt because the given values is the upper bound
        while bps > keys[cnt]:
            cnt += 1
        return rating_dict[keys[cnt]]




