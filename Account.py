class Account():
    def __init__(self, balance):
        self.balance = balance
        self.holdings = []


    def buy(self, stock, quantity):
        if stock not in self.holdings:
            self.holdings.append(stock)
        if stock.price * quantity > self.balance:
            stock.add_holding(round(self.balance / stock.price, 3))
            self.balance -= round(stock.price * (self.balance / stock.price), 3)
            print("Bought ", round(self.balance / stock.price, 3), " shares of ", stock.name, " for ", self.balance, " dollars.")
        else:
            self.balance -= stock.price * quantity
            stock.add_holding(quantity)
            print("Bought ", quantity, " shares of ", stock.name, " for ", stock.price * quantity, " dollars.")

    def sell(self, stock, quantity):
        if quantity > stock.holding:
            self.balance += stock.price * stock.holding
            stock.remove_holding(stock.holding)
            print("Sold ", stock.holding, " shares of ", stock.name, " for ", stock.price * stock.holding, " dollars.")
        else:
            self.balance += stock.price * quantity
            stock.remove_holding(quantity)
            print("Sold ", quantity, " shares of ", stock.name, " for ", stock.price * quantity, " dollars.")


    def net_worth(self):
        return self.balance + sum([(stock.price * stock.holding) for stock in self.holdings])

class Stock():
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.holding = 0

    def update_price(self, new_price):
        self.price = new_price

    def add_holding(self, quantity):
        self.holding += quantity

    def remove_holding(self, quantity):
        self.holding -= quantity