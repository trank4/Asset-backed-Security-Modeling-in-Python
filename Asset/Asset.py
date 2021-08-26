class Asset (object):
    def __init__(self,value):
        self._value = value

    def annualDeprRate(self,period):
        raise NotImplementedError()

    def monthlyDeprRate(self,period):
        return self.annualDeprRate(period) / 12

    def Value(self,period):
        return self._value * (1 - self.monthlyDeprRate(period)) ** period

class CarMixin (Asset):
    def annualDeprRate(self,period):
        raise NotImplementedError()

class Lambourghini(CarMixin):
    def annualDeprRate(self,period):
        return 0.3

class Lexus(CarMixin):
    def annualDeprRate(self,period):
        return 0.2

class HouseBase (Asset):
    def annualDeprRate(self,period):
        raise NotImplementedError()

class PrimaryHome (HouseBase):
    def annualDeprRate(self,period):
        return 0.15

class VacationHome (HouseBase):
    def annualDeprRate(self,period):
        return 0.1

