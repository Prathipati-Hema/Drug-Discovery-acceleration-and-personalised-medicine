from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# ── Disease Database ──────────────────────────────────────────────────────────
CATEGORIES = {
    "Infectious Disease": {
        "cat": "infection", "desc": "Illnesses caused by pathogenic microorganisms.",
        "prefixes": ["Acute", "Chronic", "Viral", "Bacterial", "Parasitic", "Systemic", "Opportunistic", "Nosocomial"],
        "roots": ["Influenza", "Pneumonia", "Bronchitis", "Tonsillitis", "Gastroenteritis", "Hepatitis", "Meningitis", "Tuberculosis", "Malaria", "Dengue", "Cholera", "Typhoid", "Sepsis", "Cellulitis", "Otitis Media", "Sinusitis", "Cystitis", "Pyelonephritis", "Endocarditis", "Osteomyelitis"],
        "meds": [["Azithromycin","500mg","Nausea"],["Amoxicillin","500mg","Rash"],["Ciprofloxacin","500mg","Tendon pain"],["Doxycycline","100mg","Sun sensitivity"],["Metronidazole","400mg","Metal taste"],["Vancomycin","1g","Kidney toxicity"],["Oseltamivir","75mg","Headache"],["Acyclovir","400mg","Kidney stones"],["Clarithromycin","250mg","Stomach pain"],["Nitrofurantoin","100mg","Urine color"]],
        "prec": ["Complete the full course of antibiotics.","Isolate to prevent spread.","Wash hands frequently.","Avoid contaminated water.","Rest and hydrate."]
    },
    "Cardiovascular": {
        "cat": "organs", "desc": "Disorders of heart and blood vessels.",
        "prefixes": ["Coronary","Ischemic","Hypertensive","Arrhythmic","Valvular","Congestive","Pulmonary","Peripheral"],
        "roots": ["Heart Disease","Angina Pectoris","Myocardial Infarction","Atrial Fibrillation","Cardiomyopathy","Endocarditis","Atherosclerosis","Hypotension","Shock","Aneurysm","Thrombosis","Embolism","Pericarditis"],
        "meds": [["Aspirin","75mg","Bleeding"],["Metoprolol","50mg","Fatigue"],["Amlodipine","5mg","Swelling"],["Atorvastatin","20mg","Muscle pain"],["Losartan","50mg","Dizziness"],["Digoxin","0.25mg","Vision"],["Furosemide","40mg","Dehydration"],["Clopidogrel","75mg","Bruising"],["Rivaroxaban","20mg","Bleeding"],["Spironolactone","25mg","Potassium"]],
        "prec": ["Low sodium diet.","Daily weight monitoring.","Stop smoking immediately.","Avoid excessive strenuous exercise.","Monitor blood pressure."]
    },
    "Neurological": {
        "cat": "neuro", "desc": "Conditions affecting brain, spine, and nerves.",
        "prefixes": ["Migraine","Epileptic","Neuropathic","Degenerative","Cerebral","Vascular","Autonomic","Demyelinating"],
        "roots": ["Headache","Seizure","Neuralgia","Parkinsonism","Multiple Sclerosis","Alzheimer's","Stroke","Myasthenia Gravis","ALS","Huntington's","Meningitis","Encephalitis","Bell's Palsy","Neuropathy"],
        "meds": [["Sumatriptan","50mg","Dizziness"],["Levetiracetam","500mg","Mood swings"],["Gabapentin","300mg","Weight gain"],["Pregabalin","75mg","Edema"],["Diazepam","10mg","Drowsiness"],["Ropinirole","1mg","Nausea"],["Donepezil","10mg","Diarrhea"],["Propranolol","40mg","Bradycardia"],["Carbamazepine","200mg","Dizziness"],["Baclofen","10mg","Weakness"]],
        "prec": ["Fall prevention at home.","Do not drive if dizzy.","Take meds at exact times.","Supervise if confused.","Avoid alcohol."]
    },
    "Respiratory": {
        "cat": "respiratory", "desc": "Diseases of lungs and airways.",
        "prefixes": ["Acute","Chronic","Allergic","Obstructive","Asthmatic","Restrictive","Interstitial","Occupational"],
        "roots": ["Asthma","COPD","Bronchitis","Pneumonitis","Sinusitis","Pulmonary Fibrosis","Pleurisy","Cystic Fibrosis","Sarcoidosis","Pulmonary Edema","Pneumothorax","Emphysema"],
        "meds": [["Salbutamol","100mcg","Tremor"],["Fluticasone","125mcg","Thrush"],["Montelukast","10mg","Psychiatric"],["Ipratropium","20mcg","Dry mouth"],["Theophylline","200mg","Insomnia"],["Prednisone","20mg","Weight gain"],["Budesonide","200mcg","Cough"],["Tiotropium","18mcg","Constipation"],["Formoterol","12mcg","Palpitations"],["Roflumilast","500mcg","Diarrhea"]],
        "prec": ["Avoid smoke and dust.","Check peak flow daily.","Use spacer device.","Get annual flu vaccine.","Pursed lip breathing."]
    },
    "Gastrointestinal": {
        "cat": "organs", "desc": "Disorders of digestive tract.",
        "prefixes": ["Gastric","Peptic","Inflammatory","Irritable","Hepatic","Biliary","Pancreatic","Intestinal"],
        "roots": ["Ulcer","Reflux (GERD)","Gastritis","Colitis","Pancreatitis","Cirrhosis","Dyspepsia","Hemorrhoids","Cholecystitis","Hepatitis","Diverticulitis","Gastroenteritis"],
        "meds": [["Omeprazole","20mg","Headache"],["Ranitidine","150mg","Constipation"],["Metoclopramide","10mg","Drowsiness"],["Dicyclomine","20mg","Dry mouth"],["Loperamide","2mg","Constipation"],["Sucralfate","1g","Constipation"],["Pantoprazole","40mg","Joint pain"],["Simethicone","80mg","None"],["Ursodiol","300mg","Diarrhea"],["Mesalamine","400mg","Nausea"]],
        "prec": ["Eat small frequent meals.","Avoid spicy/oily food.","Elevate head while sleeping.","Limit caffeine.","Avoid NSAIDs."]
    },
    "Musculoskeletal": {
        "cat": "skeletal", "desc": "Conditions affecting muscles, bones, and joints.",
        "prefixes": ["Osteo","Rheumatoid","Psoriatic","Gouty","Cervical","Lumbar","Septic","Metabolic"],
        "roots": ["Arthritis","Osteoporosis","Spondylitis","Fibromyalgia","Bursitis","Tendinitis","Sciatica","Scoliosis","Gout","Rhabdomyolysis","Myositis","Fracture"],
        "meds": [["Celecoxib","100mg","Stomach"],["Methotrexate","15mg","Toxicity"],["Alendronate","70mg","Heartburn"],["Prednisone","10mg","Mood"],["Colchicine","0.5mg","Diarrhea"],["Ibuprofen","600mg","Kidney"],["Hydroxychloroquine","200mg","Eyes"],["Gabapentin","300mg","Fatigue"],["Tramadol","50mg","Dizziness"],["Cyclobenzaprine","5mg","Dry mouth"]],
        "prec": ["Low impact exercise.","Fall prevention.","Check calcium levels.","Monitor liver function.","Physical therapy."]
    },
    "Endocrine": {
        "cat": "organs", "desc": "Hormonal imbalances and metabolic disorders.",
        "prefixes": ["Type 1","Type 2","Hypo","Hyper","Autoimmune","Pituitary","Thyroid","Adrenal"],
        "roots": ["Diabetes Mellitus","Thyroidism","Goiter","Adrenal Insufficiency","PCOS","Cushing's Syndrome","Acromegaly","Hypoglycemia","Hyperlipidemia","Obesity","Osteoporosis"],
        "meds": [["Metformin","500mg","Stomach"],["Insulin Glargine","10U","Hypoglycemia"],["Levothyroxine","50mcg","Palpitations"],["Glipizide","5mg","Weight"],["Sitagliptin","100mg","Pancreatitis"],["Lisinopril","10mg","Cough"],["Spironolactone","25mg","Potassium"],["Hydrocortisone","10mg","Insomnia"],["Liothyronine","5mcg","Sweating"],["Empagliflozin","10mg","UTI"]],
        "prec": ["Regular blood sugar checks.","Foot care daily.","Wear medical alert.","Strict diet.","Stay hydrated."]
    },
    "Dermatological": {
        "cat": "dermatology", "desc": "Conditions affecting skin, hair, and nails.",
        "prefixes": ["Acute","Chronic","Allergic","Contact","Atopic","Autoimmune","Bullous","Pustular"],
        "roots": ["Dermatitis","Eczema","Psoriasis","Acne Vulgaris","Urticaria","Rosacea","Fungal Infection","Vitiligo","Cellulitis","Scabies","Lichen Planus","Hives"],
        "meds": [["Hydrocortisone","1%","Thinning"],["Clotrimazole","1%","Burning"],["Terbinafine","250mg","Liver"],["Mupirocin","2%","Dryness"],["Doxycycline","100mg","Sun"],["Isotretinoin","20mg","Lips"],["Cetrizine","10mg","Drowsy"],["Fexofenadine","120mg","Headache"],["Ketoconazole","2%","Irritation"],["Permethrin","5%","Itching"]],
        "prec": ["Moisturize regularly.","Avoid scratching.","Gentle soaps.","Sun protection.","Identify triggers."]
    },
    "Renal / Urological": {
        "cat": "organs", "desc": "Kidney and urinary tract disorders.",
        "prefixes": ["Acute","Chronic","Nephrotic","Glomerular","Interstitial","Obstructive"],
        "roots": ["Kidney Disease","Renal Failure","Nephritis","Kidney Stones","UTI","Prostatitis","Cystitis","Hydronephrosis","Pyelonephritis"],
        "meds": [["Furosemide","40mg","Potassium"],["Amlodipine","5mg","Swelling"],["Sevelamer","800mg","Nausea"],["Calcitriol","0.25mcg","Calcium"],["Iron Sucrose","100mg","Allergy"],["Tamsulosin","0.4mg","Dizziness"],["Nitrofurantoin","100mg","Lungs"],["Phenazopyridine","100mg","Orange urine"],["Allopurinol","100mg","Rash"],["Sodium Bicarbonate","650mg","Gas"]],
        "prec": ["Fluid restriction may apply.","Low potassium diet.","Protein restriction.","Monitor GFR.","Avoid nephrotoxins."]
    },
    "Hematological": {
        "cat": "organs", "desc": "Disorders of blood.",
        "prefixes": ["Iron Deficiency","Megaloblastic","Hemolytic","Sickle Cell","Aplastic","Myeloproliferative"],
        "roots": ["Anemia","Leukemia","Lymphoma","Thrombocytopenia","Hemophilia","Polycythemia","Coagulation Defect"],
        "meds": [["Ferrous Sulfate","325mg","Constipation"],["Folic Acid","1mg","None"],["Cyanocobalamin","1000mcg","Pain"],["Hydroxyurea","500mg","Nausea"],["Warfarin","5mg","Bleeding"],["Epoetin Alfa","4000U","BP"],["Clopidogrel","75mg","Bleeding"],["Prednisone","10mg","Infection risk"]],
        "prec": ["Avoid injury.","Soft toothbrush.","Report bruising.","Iron rich diet.","Regular blood work."]
    },
    "Oncological": {
        "cat": "cancer", "desc": "Malignant growths and tumors.",
        "prefixes": ["Metastatic","Carcinoma","Sarcoma","Lymphoma","Leukemia","Adenocarcinoma","In Situ"],
        "roots": ["Lung Cancer","Breast Cancer","Colon Cancer","Prostate Cancer","Brain Tumor","Melanoma","Pancreatic Cancer","Leukemia","Lymphoma","Ovarian Cancer"],
        "meds": [["Cyclophosphamide","50mg","Hair loss"],["Cisplatin","50mg","Kidney"],["Doxorubicin","60mg","Heart"],["Paclitaxel","100mg","Nerve"],["Methotrexate","15mg","Sores"],["5-Fluorouracil","500mg","Diarrhea"],["Imatinib","400mg","Fluid"],["Tamoxifen","20mg","Clots"],["Vinblastine","10mg","Constipation"],["Bortezomib","2mg","Neuropathy"]],
        "prec": ["Infection prevention.","Hydration is key.","Report fever immediately.","Mouth care.","Avoid crowds."]
    },
    "Psychiatric": {
        "cat": "neuro", "desc": "Mental health disorders.",
        "prefixes": ["Major","Bipolar","Generalized","Obsessive-Compulsive","Post-Traumatic","Schizoaffective"],
        "roots": ["Depression","Anxiety","Schizophrenia","Panic Disorder","PTSD","Insomnia","ADHD","Eating Disorder"],
        "meds": [["Sertraline","50mg","Nausea"],["Fluoxetine","20mg","Insomnia"],["Escitalopram","10mg","Fatigue"],["Alprazolam","0.5mg","Drowsiness"],["Quetiapine","25mg","Weight"],["Lithium","300mg","Thyroid"],["Risperidone","1mg","Movement"],["Venlafaxine","75mg","BP"],["Bupropion","150mg","Seizure"],["Diazepam","5mg","Addiction"]],
        "prec": ["Do not stop suddenly.","Monitor for suicide risk.","Avoid alcohol.","Therapy is essential.","Report mood changes."]
    },
    "Fever Management": {
        "cat": "infection", "desc": "Elevated body temperature often due to infection or inflammation.",
        "prefixes": ["Acute","Chronic","Low-grade","High","Intermittent","Remittent"],
        "roots": ["Fever","Pyrexia","Hyperthermia","Chills","Sweats","Malaise"],
        "meds": [["Paracetamol","500mg","Liver toxicity"],["Ibuprofen","400mg","Stomach upset"],["Aspirin","325mg","Bleeding risk"],["Acetaminophen","650mg","Liver damage"],["Naproxen","220mg","Kidney stress"]],
        "prec": ["Stay hydrated.","Monitor temperature regularly.","Seek help if >103°F.","Do not use aspirin in children.","Rest adequately."]
    },
    "Malaria": {
        "cat": "infection", "desc": "Mosquito-borne infectious disease caused by Plasmodium parasites.",
        "prefixes": ["Uncomplicated","Severe","Cerebral","Vivax","Falciparum","Tertian"],
        "roots": ["Malaria","Ague","Blackwater Fever","Hemolysis","Anemia","Splenomegaly"],
        "meds": [["Artemether","80mg","Dizziness"],["Lumefantrine","480mg","Headache"],["Chloroquine","250mg","Retinopathy"],["Mefloquine","250mg","Vivid dreams"],["Primaquine","15mg","Stomach pain"],["Quinine","300mg","Tinnitus"],["Doxycycline","100mg","Sun sensitivity"],["Atovaquone","250mg","Rash"]],
        "prec": ["Complete the full course.","Use mosquito nets.","Take with food.","Screen for G6PD deficiency.","Avoid pregnancy."]
    },
    "Dengue": {
        "cat": "infection", "desc": "Viral disease transmitted by mosquitoes, causing severe flu-like illness.",
        "prefixes": ["Dengue","Severe Dengue","Dengue Hemorrhagic","Dengue Shock","Classic","Breakbone"],
        "roots": ["Fever","Rash","Myalgia","Arthralgia","Thrombocytopenia","Leukopenia"],
        "meds": [["Paracetamol","500mg","Liver toxicity"],["IV Fluids","Normal Saline","Fluid overload"],["Electrolytes","ORS","None"],["Acetaminophen","650mg","Liver load"],["Platelet Transfusion","1 unit","Allergic reaction"]],
        "prec": ["AVOID Aspirin or Ibuprofen.","Monitor platelet count daily.","Drink plenty of fluids.","Watch for warning signs.","Rest to prevent bleeding."]
    },
    "Typhoid": {
        "cat": "infection", "desc": "Bacterial infection caused by Salmonella Typhi.",
        "prefixes": ["Enteric","Typhoid","Paratyphoid","Intestinal","Septicemic","Carrier"],
        "roots": ["Fever","Rose Spots","Headache","Constipation","Diarrhea","Bradycardia"],
        "meds": [["Ciprofloxacin","500mg","Tendon rupture"],["Ceftriaxone","1g","Injection site pain"],["Azithromycin","500mg","Nausea"],["Amoxicillin","500mg","Allergic reaction"],["Levofloxacin","250mg","Insomnia"],["Ofloxacin","200mg","Dizziness"]],
        "prec": ["Complete the antibiotic course.","Wash hands thoroughly.","Avoid raw foods.","Isolate if active carrier.","Monitor for intestinal perforation."]
    },
    "Migraine & Brain Diseases": {
        "cat": "neuro", "desc": "Disorders involving brain, nerves, and severe headaches.",
        "prefixes": ["Chronic","Acute","Cluster","Tension","Hemiplegic","Vestibular"],
        "roots": ["Migraine","Epilepsy","Stroke","Parkinson's","Neuropathy","Meningitis"],
        "meds": [["Sumatriptan","50mg","Dizziness"],["Rizatriptan","10mg","Drowsiness"],["Propranolol","40mg","Fatigue"],["Topiramate","25mg","Numbness"],["Levetiracetam","500mg","Mood changes"],["Pregabalin","75mg","Weight gain"],["Amitriptyline","25mg","Dry mouth"],["Ergotamine","1mg","Nausea"]],
        "prec": ["Identify and avoid triggers.","Take medication at onset.","Do not drive if drowsy.","Maintain sleep schedule.","Seek help for sudden severe headache."]
    },
    "Lung Diseases": {
        "cat": "respiratory", "desc": "Disorders affecting lungs and airways.",
        "prefixes": ["Chronic","Acute","Obstructive","Restrictive","Asthmatic","Bronchial"],
        "roots": ["Asthma","Bronchitis","Pneumonia","COPD","Tuberculosis","Fibrosis"],
        "meds": [["Salbutamol","100mcg","Tremors"],["Fluticasone","125mcg","Thrush"],["Budesonide","200mcg","Hoarseness"],["Ipratropium","20mcg","Dry mouth"],["Montelukast","10mg","Mood changes"],["Azithromycin","250mg","Diarrhea"],["Theophylline","100mg","Insomnia"],["Prednisone","5mg","Increased appetite"]],
        "prec": ["Avoid smoking.","Use inhalers correctly.","Get flu vaccines.","Practice breathing exercises.","Report increased shortness of breath."]
    }
}

# ── Build DB at startup ───────────────────────────────────────────────────────
DB = {}

def generate_db():
    for cat_key, cat_data in CATEGORIES.items():
        for i in range(18):
            if random.random() > 0.3:
                name = f"{random.choice(cat_data['prefixes'])} {random.choice(cat_data['roots'])}"
            else:
                name = random.choice(cat_data['roots'])
            if name in DB:
                name = f"{name} (Type {i+1})"
            shuffled_meds = random.sample(cat_data['meds'], min(5, len(cat_data['meds'])))
            shuffled_prec = random.sample(cat_data['prec'], min(3, len(cat_data['prec'])))
            DB[name] = {
                "cat": cat_data["cat"],
                "desc": cat_data["desc"],
                "meds": shuffled_meds,
                "prec": shuffled_prec
            }

generate_db()
CHIP_SUGGESTIONS = list(DB.keys())[:12]

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", chips=CHIP_SUGGESTIONS)

@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query", "").strip().lower()
    if not query:
        return jsonify({"found": False, "query": query})

    match = next((k for k in DB if query in k.lower()), None)
    if match:
        data = DB[match]
        return jsonify({
            "found": True,
            "name": match,
            "cat": data["cat"],
            "desc": data["desc"],
            "meds": data["meds"],
            "prec": data["prec"]
        })
    return jsonify({"found": False, "query": query})

if __name__ == "__main__":
    app.run(debug=True)