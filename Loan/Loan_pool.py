from functools import reduce
import logging
from Loan.Loans import AutoLoan
from Loan.Loan_base import Loan
from Loan.Mortgage import FixedMortgage
from Asset.Asset import PrimaryHome,VacationHome,Lexus,Lambourghini
import datetime
import random
# LoanPool
class LoanPool(object):
    def __init__(self, loans):
        self._loans = loans

    def totalPrincipal(self):
        return sum([l.notional for l in self._loans])

    def totalBalance(self, period):
        return sum([l.balance(period) for l in self._loans])

    def principalDue(self, period):
        return sum([l.principalDue(period) for l in self._loans])

    def interestDue(self, period):
        return sum([l.interestDue(period) for l in self._loans])

    def paymentDue(self, period):
        res = sum([l.monthlyPayment(period) for l in self._loans])
        logging.debug(f'LoanPool.paymentDue(): payment of loan pool for period {period} = {res}')
        return res

    def activeLoanCount(self, period):
        tol = 10**(-8)
        #I had to introduce error tolerance because the balance close to 0 can easily mess up the calculation
        logging.debug(f'LoanPool.activeLoanCount(): tolerance is set to {tol}')
        res = sum([1 for l in self._loans if (l.balance(period) - tol) > 0])
        logging.debug(f'LoanPool.activeLoanCount(): # of active loans for period {period} = {res}')
        return res

    # modified WAM and WAR functions to use lambda and reduce()
    def WAM(self):
        wam = reduce(lambda total, loan: total + loan.notional * loan.term, self._loans, 0)
        s = reduce(lambda total, loan: total + loan.notional, self._loans, 0)
        return wam / s

    def WAR(self):
        war = reduce(lambda total, loan: total + loan.notional * loan.getRate(0), self._loans, 0)
        s = reduce(lambda total, loan: total + loan.notional, self._loans, 0)
        return war / s

    #make LoanPool iterable
    def __iter__(self):
        for l in self._loans:
            yield l

    # class method to write loans to csv
    @classmethod
    def writeLoansToCSV(cls, loanPool, fileName):
        # list to contain lines
        lines = []
        for loan in loanPool:
            lines.append(','.join([loan.__class__.__name__, loan.asset.__class__.__name__, str(loan.asset.Value(0)),str(loan.notional), str(loan.rate), str(loan.term)]))
        outputString = '\n'.join(lines)
        with open(fileName, 'w') as fp:
            fp.write('loan type,asset name, asset value, amount, rate, term\n')
            fp.write(outputString)
        logging.info('loan csv is written and closed')

    # class method to create Loan
    @classmethod
    def createLoan(cls, loanType, assetName, assetValue, principal, rate, startdate, enddate):
        # check if startdate and enddate are datetime object
        if not isinstance(startdate, datetime.datetime):
            logging.error('Error in __init__ of Loan: startdate has to be an datetime object ')
            raise TypeError('Error: startdate has to be an datetime object')

        if not isinstance(enddate, datetime.datetime):
            logging.error('Error in __init__ of Loan: enddate has to be an datetime object ')
            raise TypeError('Error: enddate has to be an datetime object')

        loanNameToClass = {'AutoLoan': AutoLoan, 'FixedMortgage': FixedMortgage}
        assetNameToClass = {'Lambourghini': Lambourghini, 'Lexus': Lexus, 'VacationHome': VacationHome,'PrimaryHome': PrimaryHome}
        assetCls = assetNameToClass.get(assetName)
        if assetCls:
            asset = assetCls(float(assetValue))
            loanCls = loanNameToClass.get(loanType)
            if loanCls:
                loan = loanCls(startdate,enddate, float(rate), float(principal), asset)
                return loan
            else:
                logging.error('Invalid loan type entered.')
                raise TypeError('Invalid loan type entered.')
        else:
            logging.error('Invalid asset type entered.')
            raise TypeError('Invalid asset type entered.')

    #_loans getter
    @property
    def loans(self):
        logging.debug(f'LoanPool.loans getter: returning _loans')
        return self._loans

    #checkDefaults update default loans for the given period and returns the recovery value
    def checkDefaults(self,period):
        recoveryValue = 0
        prob = Loan.DefaultProb(period)
        odds = int(1 / prob)
        randlst = [random.randint(0,odds - 1) for i in self._loans]
        #loop thru each loan and pass in random number to checkDefault
        for i in range(len(self._loans)):
            #check if the loan is already defaulted
            default_before = 1 if self._loans[i].default == 1 else 0
            #update newly default loans
            self._loans[i].checkDefault(randlst[i])
            #check if the loan just default
            default_after = 1 if self._loans[i].default == 1 else 0
            #if the loan just default in this period, add its recovery value to recovery value of the loan pool
            if default_before == 0 and default_after == 1:
                recoveryValue += self._loans[i].recoveryValue(period)
        #return total recovery value of the loanpool
        return recoveryValue

    #reset default status of loans in loan pool
    def default_reset(self):
        for l in self._loans:
            l.default = 0











