import json
from PriceData import PriceData

class Medication():
    def __init__(self, ndc, name, qty, dosage, form):
        self.ndc = ndc
        self.name = name
        self.qty = qty
        self.dosage = dosage
        self.form = form
        self.price_data = None

    def set_price_data(self, pd: PriceData):
        self.price_data = pd

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)