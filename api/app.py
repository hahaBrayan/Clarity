from flask import Flask, request, jsonify
import SingleCare
import csv
import io
app = Flask(__name__)


'''
OLD SEARCH
@app.route("/search/<search_term>")
def search(search_term):
    db_conn, db_cursor = util.get_db()
    db_cursor.execute("SELECT * FROM medications WHERE name= %(name)s", {'name': search_term})
    results = db_cursor.fetchall()
    db_conn.commit()
    db_cursor.close()
    db_conn.close()
    return jsonify(results)

'''
@app.route("/")
def hello():
    return 'hello'

ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def search_for_med(med_name, form, dosage, zip_code, quantity, generic, buyer_price):
    if not med_name or not form or not dosage:
            return jsonify({"error": "All fields must be supplied."})
    med_name, form, dosage, zip_code, quantity = med_name.lower().strip(), form.lower().strip(), dosage.lower().strip(), zip_code.lower().strip(), quantity.lower().strip()
    if type(generic) != bool:
        generic = generic.strip().lower() == 'true'
    sc = SingleCare.SingleCare()
    ds_data = sc.GetDrugStructureDataV2(med_name).json()
    if 'Value' not in ds_data: return jsonify({"error": "Error accessing SingleCare API!"})
    if 'Value' in ds_data and not 'Value': return jsonify([]) # term not found!
    med_info = ds_data['Value']
    medications = sc.parse_drug_structure_data_v2(med_info, form, dosage, quantity, generic)
    raw_med_data = sc.GetTieredPricings(medications, zip_code) # list of raw med prices
    med_price_data = sc.parse_mult_tiered_price_data(raw_med_data) # parse list of raw med prices, return list of list of price data
    for i in range(0, len(med_price_data)):
        if med_price_data[i] and med_price_data[i].prices:
            if buyer_price:
                if type(med_price_data[i].prices[0]) == dict:
                    price_value = med_price_data[i].prices[0]["Price"]
                    med_price_data[i].prices = [med_price_data[i].prices[0]["Price"]]
                else:
                    price_value = med_price_data[i].prices[0]
                price_diff = (int(buyer_price) - price_value)
                med_price_data[i].save_amount = price_diff if price_diff > 0 else 0
            medications[i].set_price_data(med_price_data[i])
            medications[i].price_data = medications[i].price_data.__dict__ # make json serializable
    return medications

@app.route("/search")
def search():
    med_name = request.args.get('name')
    form = request.args.get('form')
    dosage = request.args.get('dosage')
    zip_code = request.args.get('zip_code')
    quantity = request.args.get('quantity')
    generic = request.args.get('generic', default=False)
    buyer_price = request.args.get('buyer_price')
    medications = search_for_med(med_name, form, dosage, zip_code, quantity, generic, buyer_price)
    return jsonify({"error": None, "medications": [med.__dict__ for med in medications]})


@app.route("/search/bulk", methods=["POST"])
def search_bulk():
    if 'file' not in request.files:
        return jsonify({"error": "File not uploaded."})
    file = request.files['file']
    data = []
    if file and allowed_file(file.filename):
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        for row in csv_input:
            data.append(row)

    med_list = []
    for i in range(1, len(data)):
        med_name, form, dosage, zip_code, quantity, generic, buyer_price = data[i]
        med_list += search_for_med(med_name, form, dosage, zip_code, quantity, generic, buyer_price)
    return jsonify({"error": None, "medications": [med.__dict__ for med in med_list if med.price_data ]})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)