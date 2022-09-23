import requests
from Medication import Medication
from PriceData import PriceData
from flask import jsonify

class SingleCare():

    def __init__(self):
        self.BASE_URL = 'https://api.singlecare.com/services/v1_0/Public/PBMService.svc/'

    def GetDrugStructureData(self):
        return
    
    def GetDrugStructureDataV2(self, medication):
        return requests.post(self.BASE_URL + 'GetDrugStructureDataV2', None, {"Value": {"Name": medication}})

    def GetDrugInformation(self, ndc):
        return
    
    def GetTieredPricingFromNDC(self, ndc, qty, zip_code):
        return requests.post(self.BASE_URL + 'GetTieredPricing', None, {"Value": {"NDC": ndc, "Quantity": qty, "ZipCode": zip_code}})

    def GetTieredPricing(self, medication: Medication, zip_code: str):
        return requests.post(self.BASE_URL + 'GetTieredPricing', None, {"Value": {"NDC": medication.ndc, "Quantity": medication.qty, "ZipCode": zip_code, "Distance": 30}})

    def GetTieredPricings(self, medications: list[Medication], zip_code: str):
        medication_raw_data = []
        for medication in medications:
            req = requests.post(self.BASE_URL + 'GetTieredPricing', None, {"Value": {"NDC": medication.ndc, "Distance": 10, "MaxResults": "10", "Quantity": medication.qty, "ZipCode": zip_code}})
            try:
                data = req.json()
                if 'Value' not in data: return jsonify({"error": "Error accessing SingleCare API!"})
                if 'Value' in data and not 'Value': return jsonify([]) # term not found!
                medication_raw_data.append(data["Value"])
            except:
                medication_raw_data.append(None)
        return medication_raw_data


    def GetDrugInformationV2(self, ndc):
        return

    def parse_drug_structure_data_v2(self, med_list, form, dosage, quantity, is_generic) -> list[Medication]:
        parsed_medications = []
        for med_name in med_list:
            cur_name = med_name["Key"]
            cur_values = med_name["Value"]
            for med_form in cur_values:
                cur_med_form = med_form["Key"]
                cur_form_values = med_form["Value"]
                if cur_med_form.lower() == form:
                    for dose in cur_form_values:
                        cur_dosage = dose["Key"]
                        cur_dosage_values = dose["Value"]
                        if cur_dosage.lower() == dosage:
                            for qty in cur_dosage_values:
                                cur_qty = str(qty["Key"])
                                values = qty["Value"] # NDC, Name, etc location
                                if int(cur_qty) == int(quantity) and values["IsGeneric"] == is_generic:
                                    parsed_medications.append(Medication(values["NDC"],
                                    values["Name"],
                                    cur_qty,
                                    cur_dosage,
                                    cur_med_form
                                    ))
        return parsed_medications

    def parse_tiered_price_data(self, medication: dict) -> list[PriceData]:
        price_objects = None
        if not medication: return []
        med_prices = medication["PharmacyPricings"]
        for price_data in med_prices:
            prices = []
            for price in price_data["Prices"]:
                prices.append(price)
            if int(price_data["Pharmacy"]["Distance"]) <= 0: continue
            pd = PriceData(price_data["Pharmacy"], price_data["Pharmacy"]["Distance"],
            price_data["Pharmacy"]["LogoUrl"],
            price_data["Pharmacy"]["Name"],
            prices)
            price_objects = pd
        med_prices = medication["MailOrderPricings"]
        if not med_prices: return price_objects
        for price_data in med_prices:
            if int(price_data["Pharmacy"]["Distance"]) <= 0: continue
            if type(price_data["Prices"]["Price"]) == dict:
                price_value = price_data["Prices"]["Price"][0]["Price"]
            else:
                price_value = price_data["Prices"]["Price"]
            pd = PriceData(price_data["Pharmacy"], price_data["Pharmacy"]["Distance"],
            price_data["Pharmacy"]["LogoUrl"],
            price_data["Pharmacy"]["Name"],
            [price_value])
            price_objects = pd
        
        return price_objects
    
    def parse_mult_tiered_price_data(self, medications: list[dict]) -> list[PriceData]:
        parsed_medications = []
        for med in medications:
            parsed_price_data = self.parse_tiered_price_data(med)
            parsed_medications.append(parsed_price_data)
        return parsed_medications

    def get_medication_price_data(self, medication: Medication, zip_code: str):
        self.GetTieredPricing(medication.ndc, medication.qty, zip_code)


