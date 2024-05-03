#Georgie's code
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

'''Further modifications to the synpuff dataframes'''

#fill NaN as 0
drug_exposure_labelled.fillna("None", inplace=True)
condition_occurrence_labelled.fillna(0, inplace=True)

#filter for specific pages where only this person needs to be viewed
drug_person_filtered = drug_exposure_labelled.query('person_id == 200312')
condition_person_filtered = condition_occurrence_labelled.query('person_id == 200312')

'''import libraries'''
import numpy as np
import matplotlib.pyplot as plt
import json
from json import loads, dumps
import datetime as dt

'''Mutating dataframes for hierarchical display'''
respiratorydf = condition_occurrence_labelled[condition_occurrence_labelled.condition_concept_label=='Respiratory symptom']
respiratorycol = respiratorydf.person_id.tolist()
#print(respiratorycol)

mask = drug_exposure_labelled['person_id'].isin(respiratorycol)
shrinked = drug_exposure_labelled[mask]
#print(shrinked)

#shrink df
small = shrinked[['person_id', 'drug_exposure_start_date', 'drug_concept_label']]
small.fillna('N/A', inplace=True)
small['drug_concept_label'] = small.groupby(['person_id', 'drug_exposure_start_date'])['drug_concept_label'].transform(lambda x : ' & '.join(x))
#print(small)
smalldd = small.drop_duplicates()
#print(smalldd)

# https://stackoverflow.com/questions/60829670/how-to-find-repeated-patients-and-add-a-new-column
readministrations = pd.Series(np.zeros(len(smalldd),dtype=int),index=smalldd.index)

# Loop through all unique ids
all_id = smalldd['person_id'].unique()
id_administrations = {}
for pid in all_id:
    # These are all the times a patient with a given ID has had surgery
    patient = smalldd.loc[smalldd['person_id']==pid]
    administrations_sorted = pd.to_datetime(patient['drug_exposure_start_date'], format='%Y-%m-%d').sort_values()

# This checks if the previous surgery was longer than 180 days ago
    frequency = administrations_sorted.diff()<dt.timedelta(days=6000)

    # Compute the readmission
    n_administrations = [0]
    for v in frequency.values[1:]:
       n_administrations.append((n_administrations[-1]+1)*v)

    # Add these value to the time series
    readministrations.loc[administrations_sorted.index] = n_administrations

smalldd['readministration'] = readministrations

pivoted = smalldd.pivot(index='person_id', columns='readministration', values='drug_concept_label').reset_index()
renamed = pivoted.add_prefix('drug')
#renamed.head()
renamed2 = renamed.rename(columns={"drugperson_id": "person_id", "readministration":"index"})
#renamed2.head()

shrink = renamed2.loc[:, :'drug10']
#shrink.head()
fillednones= shrink.fillna("None")
#fillednones.head()
fillednones["value"] = 1
fillednones.head()

''' FLASK '''
from flask import Flask, render_template, request, jsonify, make_response, Response
from flask_sqlalchemy import SQLAlchemy
import requests

'''Visualization'''
import plotly.express as px
#import flask_table
import nbformat

'''Render Templates'''

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

# Icicle chart featuring plotly express
@app.route('/icicle')
def icicle():
    df = fillednones
    icicle = px.icicle(df, path=[px.Constant("all"), 'drug0', 'drug1', 'drug2', 'drug3', 'drug4', 'drug5'], values='value')
    icicle.update_traces(root_color="lightgrey")
    icicle.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    icicle.show()
    return render_template('icicle.html')

# Radial sunburst page featuring d3.js
@app.route('/sunburst')
def sunburst():
    df = fillednones
    sunburst = px.sunburst(df, path=['drug0', 'drug1', 'drug2', 'drug3'], values='value', color_discrete_map={'None':'black'})
    sunburst.show()
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

# Lighter, filtered version of the conditions API just for the timeline page
@app.route('/api/conditions_timeline', methods=['GET', 'POST'])
def get_condition_timeline():
    conditions = condition_person_filtered.to_dict('index')
    return Response(json.dumps(conditions, allow_nan=False),  mimetype='application/json')

# Timeline page featuring vis.js
@app.route('/timeline')
def timeline():
    drugs = drug_person_filtered
    return render_template('timeline.html', drugs=drugs)

# List of events encountered by this person_id
@app.route('/eventlist')
def eventlists():
    return render_template('eventlist.html')

# Running app
if __name__ == '__main__':
    app.run(debug = False)

###FLASK_APP=app.py flask run