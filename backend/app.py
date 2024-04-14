# synpuff.ipynb content
from pathlib import Path
import pandas as pd
from itertools import chain

# copy the data to your drive and then modify this path as required
# from google.colab import drive
#drive.mount('/content/drive')

folder = 'synpuff/'

# base query for generating the cohort

# (anyone who has a diagnosis of breast cancer OR had at least one dose of doxorubicin OR at least one dose of cyclophosphomide)

# N.B. - these data are synthetically generated and therefore not really representative, but should give you a handle on how to
# interact with the concepts and data structures. That's why there are no breast cancer patients who had breast cancer AND
# the drugs of interest, which would be very common in the real world, but it's definitely adequate to get started.

# SELECT distinct(de.person_id)
# FROM
# `bigquery-public-data.cms_synthetic_patient_data_omop.drug_exposure` as de join
# `bigquery-public-data.cms_synthetic_patient_data_omop.concept` as c on c.concept_id = de.drug_concept_id join
# `bigquery-public-data.cms_synthetic_patient_data_omop.drug_exposure` as de2 on de.person_id = de2.person_id join
# `bigquery-public-data.cms_synthetic_patient_data_omop.concept` as c2 on c2.concept_id = de2.drug_concept_id join
# `bigquery-public-data.cms_synthetic_patient_data_omop.condition_occurrence` as co on co.person_id = de.person_id join
# `bigquery-public-data.cms_synthetic_patient_data_omop.concept` as c3 on c3.concept_id = co.condition_concept_id
# where upper(c.concept_name) like '%DOXORUBICIN%'
# or upper(c2.concept_name) like '%CYCLOPHOSPHAMIDE%'
# or upper(c3.concept_name) LIKE '%NEOPLASM%BREAST%'
# LIMIT 1000

# ended up downloading them separately because it was too slow combined...

cohort_files = pd.concat([pd.read_csv(f'{folder}cyclo.csv'),
                          pd.read_csv(f'{folder}doxo.csv'),
                          pd.read_csv(f'{folder}breast.csv')])

# copy this as filter to next queries
print(list(cohort_files.person_id.unique()))

# select *
# from `bigquery-public-data.cms_synthetic_patient_data_omop.drug_exposure` as p
# where p.person_id in (...)

person = pd.read_csv('synpuff/person.csv')
condition_occurrence = pd.read_csv('synpuff/condition_occurrence.csv')
drug_exposure = pd.read_csv('synpuff/drug_exposure.csv')
concept = pd.read_csv('synpuff/concept.csv')

print(list(person.location_id.unique()))

location = pd.read_csv('synpuff/location.csv')

concept_lookup = {c.concept_id: c.concept_name for c in concept.itertuples()}

def make_labels(df):
    for c in df.columns:
        if 'concept_id' in c:
            df[c.replace('_id', '_label')] = df[c].map(concept_lookup)
        if 'concept_id' in c or 'source' in c or len(df[df[c].notna()])==0:
            df = df.drop(c, axis=1)
    return df

person_labelled = make_labels(person)
condition_occurrence_labelled = make_labels(condition_occurrence)
drug_exposure_labelled = make_labels(drug_exposure)
location_labelled = make_labels(location)

drug_exposure_labelled[drug_exposure_labelled.drug_concept_label.str.contains('cyclo', case=False, na=False)]

person_labelled.head()
location_labelled.head()
condition_occurrence_labelled.head()
drug_exposure_labelled.head()

drug_exposure_labelled[drug_exposure_labelled.drug_concept_label.str.contains('cyclophosphamide', na=False, case=False)]

drug_exposure[drug_exposure.drug_concept_id==1338512]

'''flask assignment items'''

import requests
import numpy as np
import json
from json import loads, dumps

''' FLASK '''
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/api/persons')
def get_person():
    persons = person_labelled.to_dict('index')
    return jsonify({'persons':persons})

@app.route('/datasafe')
def datasafe():
    r = requests.get('https://raw.githubusercontent.com/kees911/clinical-dashboard-ux-dissertation/main/backend/templates/api/persons.html')
    dfjson = r.json()
    return render_template('datasafe.html', data = dfjson)

@app.route('/prototype1')
def prototype1():
    return render_template('prototype1.html')

@app.route('/prototype2')
def prototype2():
    return render_template('prototype2.html')

@app.route('/eventlist')
def eventlist():
    return render_template('eventlist.html')

@app.route('/sunburst')
def sunburst():
    return render_template('sunburst.html')

@app.route('/timeline')
def timeline():
    return render_template('timeline.html')


# Running app
if __name__ == '__main__':
    app.run()

###FLASK_APP=app.py flask run