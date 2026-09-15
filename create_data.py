import json
import random
import os
from reportlab.pdfgen import canvas 


# lists of random data
first_names = ["Ahmed","Sara","Ali","Fatima","Karim","Lina","Youssef","Samir" ,"Omar" ,"Nour" ,"Hassan" ,"Ibrahim" ,"Mohamed" ,"Yasin" ,"Layla" ,"Zainab"]
last_names = ["Ali","Mansour","Benali","Haddad","Saadi","Khaled" ,"El-Din" ,"Hussein" ,"Nasser" ,"Yahia","Khalil" ,"Jouini"]

blood_types = ["A+","A-","B+","B-","O+","O-","AB+"]
marital_status = ["Single","Married"]

diseases = ["Diabetes","Hypertension","Anemia","Asthma","Healthy"]

medications = {
    "Diabetes":"Metformin",
    "Hypertension":"Amlodipine",
    "Anemia":"Iron supplements",
    "Asthma":"Salbutamol",
    "Healthy":"None"
}

os.makedirs("pdf_reports", exist_ok=True)

patients = []

for i in range(200):

    name = random.choice(first_names)
    last = random.choice(last_names)

    age = random.randint(18,80)
    blood = random.choice(blood_types)
    status = random.choice(marital_status)

    disease = random.choice(diseases)
    medicine = medications[disease]

    # decide if patient has PDF
    has_pdf = random.choice([True, False])

    pdf_file = None

    if has_pdf:

        pdf_file = f"patient_{i}.pdf"
        path = f"pdf_reports/{pdf_file}"

        c = canvas.Canvas(path)

        text = f"""
Patient Medical Report

Name: {name} {last}
Age: {age}
Blood Type: {blood}
Marital Status: {status}

Diagnosis: {disease}
Medication: {medicine}

Blood Sugar: {random.randint(80,200)} mg/dL
Hemoglobin: {round(random.uniform(10,16),2)} g/dL
Cholesterol: {random.randint(150,260)} mg/dL
"""

        y = 750
        for line in text.split("\n"):
            c.drawString(50,y,line)
            y -= 20

        c.save()

    patient = {
        "id": i,
        "first_name": name,
        "last_name": last,
        "age": age,
        "blood_type": blood,
        "marital_status": status,
        "disease": disease,
        "medication": medicine,
        "pdf_report": pdf_file
    }

    patients.append(patient)

# save JSON
with open("patients.json","w") as f:
    json.dump(patients,f,indent=4)

print("200 patients generated!")