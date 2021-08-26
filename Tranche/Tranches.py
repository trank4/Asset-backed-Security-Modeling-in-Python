from Tranche.Tranche_base import Tranche
import logging

class StandardTranche(Tranche):

    def __init__(self,notional,annualrate,subordination):
        #use base tranche init
        logging.debug(f'StandardTranche.__init__: execute the init of parent class')
        super(StandardTranche,self).__init__(notional,annualrate,subordination)

        #flag to record the period
        self._period = 0
        logging.debug(f'StandardTranche.__init__: _period = {self._period}')
        #flag to record principal paid to the tranche in the current period
        self._principalReceived = 0
        logging.debug(f'StandardTranche.__init__: _principalReceived = {self._principalReceived}')
        #flag to record total principal received from the beginning (for notionalBalance())
        self._totalPrincipalReceived = 0
        logging.debug(f'StandardTranche.__init__: _totalPrincipalReceived = {self._totalPrincipalReceived}')
        #flag to record interest paid to the tranche in the current period
        self._interestReceived = 0
        logging.debug(f'StandardTranche.__init__: _interestReceived = {self._interestReceived}')
        #flag to record interest shortfall
        self._interestShortfall = 0
        logging.debug(f'StandardTranche.__init__: _interestShortfall = {self._interestShortfall}')
        #flag = 1 if the principal is paid for the period, = 0 otherwise
        self._principalPaid = 0
        logging.debug(f'StandardTranche.__init__: _principalPaid = {self._principalPaid}')
        # flag = 1 if the interest is paid for the period, = 0 otherwise
        self._interestPaid = 0
        logging.debug(f'StandardTranche.__init__: _interestPaid = {self._interestPaid}')
        # flag to record previous notionalBalance
        self._previousPeriodBalance = None
        logging.debug(f'StandardTranche.__init__: _previousPeriodBalance = {self._previousPeriodBalance}')

    #__repr__ for display object
    def __repr__(self):
        return f'StandardTranche: notional = {self._notional}, rate = {self._rate}, subordination = {self._subordination}'

    #getter for object period
    @property
    def period(self):
        logging.debug(f'StandardTranche.period getter: {self._period}')
        return self._period

    #getter for interest shortfall
    @property
    def interestShortfall(self):
        logging.debug(f'StandardTranche.interestShortfall getter: {self._interestShortfall}')
        return self._interestShortfall

    #getter for principalReceived
    @property
    def principalReceived(self):
        logging.debug(f'StandardTranche.principalReceived getter: {self._principalReceived}')
        return self._principalReceived

    #getter for interestReceived
    @property
    def interestReceived(self):
        logging.debug(f'StandardTranche.interestReceived getter: {self._interestReceived}')
        return self._interestReceived


    #increaseTimePeriod method
    def increaseTimePeriod(self):
        #reset the principalPaid and interestPaid flag to 0
        self._principalPaid = 0
        logging.debug(f'StandardTranche.increaseTimePeriod(): set _principalPaid = {self._principalPaid}')
        self._interestPaid = 0
        logging.debug(f'StandardTranche.increaseTimePeriod(): set _interestPaid = {self._interestPaid}')
        #reset interestReceived and principalReceived to 0 (because the payment has not been made)
        self._interestReceived = 0
        logging.debug(f'StandardTranche.increaseTimePeriod(): set _interestReceived = {self._interestReceived}')
        self._principalReceived = 0
        logging.debug(f'StandardTranche.increaseTimePeriod(): set _principalReceived = {self._principalReceived}')
        #record current balance to previousBalance
        self._previousPeriodBalance = self.notionalBalance()
        logging.debug(f'StandardTranche.increaseTimePeriod(): set _previousPeriodBalance = Tranche.notionalBalance() =  {self._previousPeriodBalance}')
        #increase period by 1
        self._period += 1
        logging.debug(f'StandardTranche.increaseTimePeriod(): increase _period by 1 to {self._period}')

    def makePrincipalPayment(self, payment):
        #throw error if the Principal is already paid for the period
        balance = self.notionalBalance()
        logging.debug(f'StandardTranche.makePrincipalPayment(): balance in the current period = {balance}')
        if self._principalPaid == 1:
            logging.error(f'StandardTranche.makePrincipalPayment(): _principalPaid == {self._principalPaid}')
            raise Exception('Principal is already paid for the period')
        #if the current notional balance is 0, the function should not accept the payment
        if balance == 0:
            logging.error(f'StandardTranche.makePrincipalPayment(): _balance == {self._principalPaid}')
            raise ValueError('Current notional balance is 0')
        # flip principalPaid flag to 1
        self._principalPaid = 1
        logging.debug(f'StandardTranche.makePrincipalPayment(): set _principalPaid to {self._principalPaid}')
        self._principalReceived = payment
        logging.debug(f'StandardTranche.makeInterestPayment(): principal received for the period = {self._principalReceived}')
        self._totalPrincipalReceived += payment
        logging.debug(f'StandardTranche.makePrincipalPayment(): increase _totalPrincipalReceived by {self._principalReceived} to {self._totalPrincipalReceived}')

    def makeInterestPayment(self, payment):
        intDue = self.interestDue()
        logging.debug(f'StandardTranche.makeInterestPayment(): interestDue in the current period = {intDue}')
        # throw error if the interest is already paid for the period
        if self._interestPaid == 1:
            logging.error(f'StandardTranche.makeInterestPayment(): _interestPaid == {self._interestPaid}')
            raise Exception('Interest is already paid for the period')
        if intDue == 0:
            logging.error(f'StandardTranche.makeInterestPayment(): interestDue == {intDue}')
            raise ValueError('No interest Due')
        #flip interestPaid flag to 1
        self._interestPaid = 1
        logging.debug(f'StandardTranche.makeInterestPayment(): set _interestPaid = {self._interestPaid}')
        #add to interest shortfall if there is one, if there is an excess payment, the interest shortfall will be paid
        due_excess = payment - intDue
        logging.debug(f'StandardTranche.makeInterestPayment(): excess payment = {due_excess}')
        self._interestShortfall -= due_excess
        logging.debug(f'StandardTranche.makeInterestPayment(): decrease interestShortfall by {due_excess} to {self._interestShortfall}')
        #record interest received
        self._interestReceived = payment
        logging.debug(f'StandardTranche.makeInterestPayment(): interest received for the period = {self._interestReceived}')

    #This should return the amount of notional still owed to the tranche for the current time period (after any payments made).
    def notionalBalance(self):
        res = self._notional - self._totalPrincipalReceived + self._interestShortfall
        logging.debug(f'StandardTranche.notionalBalance(): balance for current period = {res}')
        return res

    def interestDue(self):
        #if current period is 0, no interest Due
        if self._period == 0:
            logging.error(f'StandardTranche.interestDue(): period = {self._period}')
            raise ValueError('No interest Due at time 0')
        #interestDue = previous period notional * rate
        res = self._previousPeriodBalance * self._rate
        logging.debug(f'StandardTranche.interestDue(): interest Due = {res}')
        return res

    #reset the tranch to its original state
    def reset(self):
        # reset the period
        self._period = 0
        logging.debug(f'StandardTranche.reset(): set _period = {self._period}')
        # reset principal paid to the tranche
        self._principalReceived = 0
        logging.debug(f'StandardTranche.reset(): set _principalReceived = {self._principalReceived}')
        # reset total principal paid
        self._totalPrincipalReceived = 0
        logging.debug(f'StandardTranche.reset(): set _totalPrincipalReceived = {self._totalPrincipalReceived}')
        # reset interest paid to the tranche
        self._interestReceived = 0
        logging.debug(f'StandardTranche.reset(): set _interestReceived = {self._interestReceived}')
        # reset interest shortfall
        self._interestShortfall = 0
        logging.debug(f'StandardTranche.reset(): set _interestShortfall = {self._interestShortfall}')
        # reset the principal is paid flag
        self._principalPaid = 0
        logging.debug(f'StandardTranche.reset(): set _principalPaid = {self._principalPaid}')
        # reset the interest is paid flag
        self._interestPaid = 0
        logging.debug(f'StandardTranche.reset(): set _interestPaid = {self._interestPaid}')
        # reset previous notionalBalance
        self._previousPeriodBalance = None
        logging.debug(f'StandardTranche.reset(): set _previousPeriodBalance = {self._previousPeriodBalance}')





