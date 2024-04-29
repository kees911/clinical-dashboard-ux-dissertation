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
#print(list(cohort_files.person_id.unique()))

# select *
# from `bigquery-public-data.cms_synthetic_patient_data_omop.drug_exposure` as p
# where p.person_id in (...)

person = pd.read_csv('synpuff/person.csv')
condition_occurrence = pd.read_csv('synpuff/condition_occurrence.csv')
drug_exposure = pd.read_csv('synpuff/drug_exposure.csv')
concept = pd.read_csv('synpuff/concept.csv')

#print(list(person.location_id.unique()))

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

#fill NaN as 0
drug_exposure_labelled.fillna(0, inplace=True)

#filter for specific pages where only this person needs to be viewed
drug_person_filtered = drug_exposure_labelled.query('person_id == 200312')

'''flask assignment items'''
import numpy as np
import requests
import json
from json import loads, dumps

''' FLASK '''
from flask import Flask, render_template, request, jsonify, make_response, Response
import flask_wtf
from jinja2.utils import markupsafe
markupsafe.Markup()
from markupsafe import Markup 
import flask_table

app = Flask(__name__)

# Homepage
@app.route('/')
def home():
    return render_template('home.html')

# Persons Labelled JSON API
@app.route('/api/persons', methods=['GET', 'POST'])
def get_person():
    persons = person_labelled.to_dict('index')
    return Response(json.dumps(persons, allow_nan=False),  mimetype='application/json')

# Locations Labelled JSON API
@app.route('/api/locations', methods=['GET', 'POST'])
def get_location():
    locations = location_labelled.to_dict('index')
    return Response(json.dumps(locations, allow_nan=False),  mimetype='application/json')

# Condition Occurrence Labelled JSON API
@app.route('/api/conditions', methods=['GET', 'POST'])
def get_condition():
    conditions = condition_occurrence_labelled.to_dict('index')
    return Response(json.dumps(conditions, allow_nan=False),  mimetype='application/json')

# Drug Exposure Labelled JSON API
@app.route('/api/drugs', methods=['GET', 'POST'])
def get_drug():
    drugs = drug_exposure_labelled.to_dict('index')
    return Response(json.dumps(drugs, allow_nan=False),  mimetype='application/json')

# Debug to make sure that the above json dumps worked - 
# uses location which is the lightest of the dataframes
@app.route('/datasafe')
def datasafe():
    ds = location_labelled.to_dict('index')
    df = pd.DataFrame.from_dict(ds, orient='index')
    return render_template('datasafe.html',data = df.to_html())

# First prototype page
@app.route('/prototype1')
def prototype1():
    return render_template('prototype1.html')

# Second prototype page 
@app.route('/prototype2')
def prototype2():
    return render_template('prototype2.html')

# List of events encountered by this person_id
@app.route('/eventlist')
def eventlist():
    return render_template('eventlist.html')

# Radial sunburst page featuring d3.js
@app.route('/sunburst')
def sunburst():
    return render_template('sunburst.html')

# Sankey diagram page featuring Google Charts
@app.route('/sankey')
def sankey():
    return render_template('sankey.html')

# Lighter, filtered version of the drugs API just for the timeline page
@app.route('/api/drugs_timeline', methods=['GET', 'POST'])
def get_drug_timeline():
    drugs = drug_person_filtered.to_dict('index')
    return Response(json.dumps(drugs, allow_nan=False),  mimetype='application/json')

# Timeline page featuring vis.js
@app.route('/timeline')
def timeline():
    drugs = drug_person_filtered
    return render_template('timeline.html', drugs=drugs)


# Running app
if __name__ == '__main__':
    app.run(debug = False)

###FLASK_APP=app.py flask run