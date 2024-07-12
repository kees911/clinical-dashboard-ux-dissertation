'''Georgie's code'''
# synpuff.ipynb content
from pathlib import Path
import pandas as pd
pd.set_option("display.max_rows", None, "mode.chained_assignment", None)
from itertools import chain

'''api manipulation'''
import numpy as np
import matplotlib.pyplot as plt
import json
from json import loads, dumps
import datetime as dt

'''Visualization'''
import plotly
import plotly.express as px
#import flask_table
#import nbformat

# copy the data to your drive and then modify this path as required
# from google.colab import drive
#drive.mount('/content/drive')

folder = 'synpuff/'

# base query for generating the cohort
care_site = pd.read_csv('synpuff/CARE_SITE.csv')
cohort_filter = pd.read_csv('synpuff/COHORT_FILTER.csv')
concept_class= pd.read_csv('synpuff/CONCEPT_CLASS.csv')
concept = pd.read_csv('synpuff/CONCEPT.csv')
condition_occurrence = pd.read_csv('synpuff/CONDITION_OCCURRENCE.csv')
domain = pd.read_csv('synpuff/DOMAIN.csv')
drug_exposure = pd.read_csv('synpuff/DRUG_EXPOSURE.csv')
location = pd.read_csv('synpuff/LOCATION.csv')
measurement = pd.read_csv('synpuff/MEASUREMENT.csv')
observation = pd.read_csv('synpuff/OBSERVATION.csv')
person = pd.read_csv('synpuff/PERSON.csv')
procedure_occurrence = pd.read_csv('synpuff/PROCEDURE_OCCURRENCE.csv')
provider = pd.read_csv('synpuff/PROVIDER.csv')
vocabulary = pd.read_csv('synpuff/VOCABULARY.csv')

# make labels from mapping concept IDs to concept labels
concept_lookup = {c.concept_id: c.concept_name for c in concept.itertuples()}

def make_labels(df):
    for c in df.columns:
        if 'concept_id' in c:
            df[c.replace('_id', '_label')] = df[c].map(concept_lookup)
        if 'concept_id' in c or 'source' in c or len(df[df[c].notna()])==0:
            df = df.drop(c, axis=1)
    return df

care_site_labelled = make_labels(care_site)
cohort_filter_labelled = make_labels(cohort_filter)
condition_occurrence_labelled = make_labels(condition_occurrence)
domain_labelled = make_labels(domain)
drug_exposure_labelled = make_labels(drug_exposure)
location_labelled = make_labels(location)
measurement_labelled = make_labels(measurement)
observation_labelled = make_labels(observation)
person_labelled = make_labels(person)
procedure_occurrence_labelled = make_labels(procedure_occurrence)
provider_labelled = make_labels(provider)
vocabulary_labelled = make_labels(vocabulary)

'''Timeline'''
person_code = 

# pull out individual from relevant datasets
cond_indiv = condition_occurrence_labelled.loc[condition_occurrence_labelled['person_id']==person_code]
drug_indiv = drug_exposure_labelled.loc[drug_exposure_labelled['person_id']==person_code]
meas_indiv = measurement_labelled.loc[measurement_labelled['person_id']==person_code]
#obs_indiv=observation_labelled.loc[observation_labelled['person_id']==person_code]
proc_indiv=procedure_occurrence_labelled.loc[procedure_occurrence_labelled['person_id']==person_code]

# rename and write new columns
#names of the columns and their content correspond to 
#required assignments and data types for the vis.js Javascript library

### condition occurrences
cond_indiv.rename(columns={'condition_start_date':'start', 'condition_end_date':'end'}, inplace=True)
cond_indiv['content'] = cond_indiv['condition_type_concept_label'] + ':<br>' + cond_indiv['condition_concept_label']
cond_indiv['group'] = 'condition occurrence'
cond_indiv['className'] = 'conditions'
cond_indiv.drop_duplicates(subset=['content', 'start'],keep='last',inplace=True)

### drug exposures
drug_indiv.rename(columns={'drug_exposure_start_date':'start', 'drug_exposure_end_date':'end'}, inplace=True)
drug_indiv['content'] = drug_indiv['drug_concept_label'] + ', ' + drug_indiv['route_concept_label'] + ', ' + drug_indiv['quantity'].astype(str)
drug_indiv['group'] = 'drug exposure'
drug_indiv['className'] = 'drugs'
drug_indiv.drop_duplicates(subset=['content', 'start'],keep='last',inplace=True)

### measurements
meas_weight = meas_indiv.loc[meas_indiv['measurement_concept_label'].isin(['Body weight','Weight change'])]
#Merge weight measurements with weight differences from last measurement
meas_weight['value_as_number']=meas_weight['value_as_number'].apply(str)
meas_grouped = meas_weight.groupby(['measurement_date'])['value_as_number'].transform(lambda x: ' kg,<br>Weight change: '.join(x))
meas_weight['value_as_number'] = meas_grouped
meas_weight['content'] = 'Body weight: ' + meas_weight['value_as_number'] + '%'
meas_weight['content'] = meas_weight['content'].replace({'Body weight: 77.4%':'Body weight: 77.4 kg'})
#Rename columns
meas_weight.rename(columns={'measurement_date':'start'}, inplace=True)
meas_weight['group'] = 'measurement'
meas_weight['className'] = 'measurements'
meas_weight.drop_duplicates(subset=['content', 'start'],keep='last',inplace=True)

### procedures
proc_indiv.rename(columns={'procedure_date':'start'}, inplace=True)
proc_indiv['content'] = proc_indiv['procedure_type_concept_label'] + ':<br>' + proc_indiv['procedure_concept_label']
proc_indiv['group'] = 'procedure'
proc_indiv['className'] = 'procedures'
proc_indiv.drop_duplicates(subset=['content', 'start'],keep='last',inplace=True)

# merge dataframes
frames = [cond_indiv, drug_indiv, meas_weight, proc_indiv]
tl_events_merged = pd.concat(frames, ignore_index=True, sort=False)
tl_nodup = tl_events_merged.drop_duplicates(subset=['content', 'start'],keep='last')
#reduce to relevant columns
#tl_event_list = tl_events_merged[['start','end','content','style']]
tl_event_list = tl_nodup[['start','end','content','group', 'className']]
#if no end date, fill with string 'null' as json does not take blanks
tl_event_list['end'] = tl_event_list['end'].fillna('null')
#also change one-day events to null, otherwise they don't show up
tl_event_list['end'] = np.where(tl_event_list['end']==tl_event_list['start'], 'null', tl_event_list['end'])
#it turns out they're actually all one-day items...

'''Appointments Table'''
# Extends the timeline's information
# Renames columns to more user-friendly (hopefully) titles
cond_appts = cond_indiv.rename(columns={'start':'Start', 'end':'End','condition_concept_label':'Description', 'condition_type_concept_label':'Type', 'group':'Category'})
drug_appts = drug_indiv.rename(columns={'start':'Start', 'end':'End', 'drug_concept_label':'Description', 'quantity':'Quantity', 'route_concept_label':'Type', 'group':'Category'})
meas_appts = meas_indiv.rename(columns={'measurement_date':'Start', 'measurement_concept_label':'Description', 'value_as_number':'Quantity', 'measurement_type_concept_label':'Type'})
meas_appts['Category'] = 'measurement'
proc_appts = proc_indiv.rename(columns={'start':'Start', 'end':'End', 'procedure_concept_label':'Description', 'quantity':'Quantity', 'procedure_type_concept_label':'Type', 'group':'Category'})

appt_elements = [cond_appts, drug_appts, meas_appts, proc_appts]
appts_merged = pd.concat(appt_elements, ignore_index=True, sort=False)
#frames was defined as a list in the timeline section
appts_nodup = appts_merged.drop_duplicates(keep='last')
appts_list = appts_nodup[['Start','End','Description','Quantity','Type','Category']]


'''Weight Chart'''
meas_graphs = meas_indiv.loc[meas_indiv['measurement_concept_label'].isin(['Body surface area', 'Body height', 'Body weight', 'Weight change'])]
meas_graphs['measurement_concept_label']=meas_graphs['measurement_concept_label'].replace({
    'Body weight':'Body weight (kg)', 
    'Weight change':'Weight change (%)',
    'Body height': 'Body height (cm)',
    'Body surface area': 'Body surface area (m\u00B2)'})
weight_fig = px.scatter(meas_graphs, x="measurement_date", y="value_as_number", 
facet_col="measurement_concept_label", facet_col_wrap=2,
facet_row_spacing=0.1, facet_col_spacing=0.05)
weight_fig.update_yaxes(matches=None, showticklabels=True)
weight_fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
#weight_fig.show()

''' FLASK '''
from flask import Flask, render_template, request, jsonify, make_response, Response
#from flask_sqlalchemy import SQLAlchemy
#import requests

'''Render Templates'''

app = Flask(__name__)

# Homepage
@app.route('/')
def home():
    return render_template('home.html')

# Timeline JSON API
@app.route('/api/tlapi', methods=['GET', 'POST'])
def get_tlapi():
    tlapi = tl_event_list.reset_index().to_dict(orient='records')
    return Response(json.dumps(tlapi, allow_nan=True),  mimetype='application/json')

# Appointments JSON API
@app.route('/api/apptapi', methods=['GET', 'POST'])
def get_apptapi():
    apptapi = appts_list.reset_index().to_dict(orient='records')
    return Response(json.dumps(apptapi, allow_nan=True),  mimetype='application/json')

# Sankey diagram page featuring Google Charts
@app.route('/sunwidget')
def sunwidget():
    return render_template('sunwidget.html')

# First prototype page
@app.route('/prototype1')
def prototype1():
    return render_template('prototype1.html', p1panda=appts_list.to_html(classes = 'my_class" id = "p1panda'))

# Second prototype page 
@app.route('/prototype2')
def prototype2():
    return render_template('prototype2.html', p1panda=appts_list.to_html(classes = 'my_class" id = "p1panda'))

# Icicle chart featuring plotly express
@app.route('/icicle')
def icicle():
    df = fillednones
    icicle = px.icicle(df, path=[px.Constant("all"), 'drug0', 'drug1', 'drug2', 'drug3', 'drug4', 'drug5'], values='value')
    icicle.update_traces(root_color="lightgrey")
    icicle.update_layout(margin = dict(t=50, l=25, r=25, b=25))
    icicle.show()
    return render_template('icicle.html')

# Radial sunburst page featuring plotly express
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

# Timeline page featuring vis.js
@app.route('/timeline')
def timeline():
    return render_template('timeline.html')

# List of events encountered by this person_id
@app.route('/eventlist')
def eventlists():
    return render_template('eventlist.html', p1panda=appts_list.to_html(classes = 'my_class" id = "p1panda'))

# Running app
if __name__ == '__main__':
    app.run(debug = False)

###FLASK_APP=app.py flask run