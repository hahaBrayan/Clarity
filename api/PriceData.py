class PriceData():
    def __init__(self, pharmacy, distance, logo, name, prices, save_amount=None):
        self.pharmacy = pharmacy
        self.distance = distance
        self.logo = logo
        self.name = name
        self.prices = prices
        self.save_amount = save_amount