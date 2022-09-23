import csv
from os import error
import psycopg2


def get_db():
    conn = psycopg2.connect(
    host="medication.cjwdncteaalz.us-east-2.rds.amazonaws.com",
    database="",
    user="postgres",
    password="OaPUKXQr8mpXm3G2ErOx")
    return conn, conn.cursor()


def validate_input(input):
    if not input.isdigit():
            raise ValueError("Input not valid! Please enter either 1 or 2 and press enter: \n")
            return False
    elif int(input) != 1 and int(input) != 2:
        return False
    
    return True

def get_import_or_extract():
    function_choice = input("Would you like to import or extract data? Enter 1 to import, 2 to extract:\n")
    is_valid = validate_input(function_choice)
    while not is_valid:
        function_choice = input("Invalid input! Please enter 1 or 2 then press enter:\n")
        is_valid = validate_input(function_choice)
    return 'import' if int(function_choice) == 1 else 'export'



def import_data():
    filename = input('Enter filename to import. This should be in the same folder as this file!\n')
    data_to_import = []
    with open(filename, newline='') as csvfile:
        filereader = csv.reader(csvfile, delimiter=',')
        for row in filereader:
            if len(row) < 5: raise error('Missing columns in csv file.')
            name, dosage, route_of_admin, price, frequency = row
            data_to_import.append("('{}', '{}', '{}', {}, '{}')".format(name, dosage, route_of_admin, price, frequency))
    values_for_query = ','.join(data_to_import)
    conn, cursor = get_db()
    cursor.execute('''
    INSERT INTO medications(name, dosage, route_of_admin, price, frequency)
    values ''' + values_for_query)
    conn.commit()
    cursor.close()
    conn.close()
    print('Success! New medications have been written to the database.')

def export_all_data():
    medication_list_file = input('Please type the name of the file with the list of medications you would like export. If you want to export all, leave this'
    + ' blank and press enter:\n')
    conn, cursor = get_db()
    if not medication_list_file:
        cursor.execute('''
        SELECT * FROM medications
        ''')
        rows = cursor.fetchall()
    else:
        with open(medication_list_file, "r+") as med_list_file:
            med_names = med_list_file.readlines()
            med_names = ["'" + r.strip() + "'" for r in med_names]
            med_names = '(' + ','.join(med_names) + ')'
            cursor.execute('''
            SELECT * FROM medications where name in''' + med_names)
            rows = cursor.fetchall()

    cursor.close()
    conn.close()
    with open("extracted_data.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    








if __name__ == "__main__":
    val = get_import_or_extract()
    if val == 'import': import_data()
    else: export_all_data()