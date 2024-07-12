# synpuff.ipynb content
import pandas as pd
pd.set_option("display.max_rows", None, "mode.chained_assignment", None)
from itertools import chain

import numpy as np
import datetime as dt

from dash import Dash, html, dcc, Input, Output, callback
import plotly.express as px
import plotly
import plotly.offline
import plotly.graph_objs as go

'''Georgie's code'''
# copy the data to your drive and then modify this path as required

folder = 'synpuff/'

# base query for generating the cohort
concept = pd.read_csv('synpuff/CONCEPT.csv')
condition_occurrence = pd.read_csv('synpuff/CONDITION_OCCURRENCE.csv')
drug_exposure = pd.read_csv('synpuff/DRUG_EXPOSURE.csv')
observation = pd.read_csv('synpuff/OBSERVATION.csv')
person = pd.read_csv('synpuff/PERSON.csv')
procedure_occurrence = pd.read_csv('synpuff/PROCEDURE_OCCURRENCE.csv')
hierarchy = pd.read_csv('synpuff/hierarchy.csv')
props = pd.read_csv('synpuff/hemonc_component_properties.csv')

'''Ivy's code'''
#rxnorm = props[props['vocabulary_id']=='RxNorm']
#list of valid drug categories from Ivy from RxNorm/HemOnc
sact=['Alkylating agent', 'Anti-CD38 antibody', 'Anti-CTLA-4 antibody', 'Anti-TACSTD2 antibody-drug conjugate', 'Anthracycline', 'Antiandrogen', 'Antifolate',
'Antimetabolite', 'Antitumor antibiotic', 'Anti-CD52 antibody', 'Anti-CD20 antibody', 'Anti-EGFR antibody', 'Anti-HER2 antibody', 'Anti-CD38 antibody', 'Anti-PD-1 antibody',
'Anti-PD-L1 antibody', 'Anti-RANKL antibody', 'Anti-SLAMF7 antibody','Anti-VEGF antibody', 'Aromatase inhibitor', 'Aromatase inhibitorsthird generation',
'Biosimilar', 'BRAF inhibitor', 'DNA methyltransferase inhibitor', 'Deoxycytidine analog', 'EGFR inhibitor', 'ERBB 2 inhibitor', 'Estrogen receptor inhibitor',
'Folic acid analog', 'Fluoropyrimidine', 'GnRH agonist', 'HDAC inhibitor', 'Human DNA synthesisinhibitor', 'Microtubule inhibitor', 'MTOR inhibitor',
'Nitrogen mustard', 'Nitrosourea', 'Neutral', 'PARP inhibitor', 'PARP1 inhibitor', 'PARP2 inhibitor', 'Phenothiazine', 'Platinum agent', 'Proteasome inhibitor',
'Purine analog', 'Pyrimidine analog', 'RANK ligand inhibitor', 'Selective estrogen receptor modulator', 'Somatostatin analog', 'T-cell activator',
'Targeted therapeutic', 'Taxane', 'Topoisomerase I inhibitor', 'Topoisomerase II inhibitor', 'Triazene', 'Vinca alkaloid', 'Xanthine oxidase inhibitor',
'WHO Essential Cancer Medicine']
#rxnorm = rxnorm[rxnorm['component_class_name'].isin(sact)]
props=props[props['component_class_name'].isin(sact)]
antican = props['concept_id_2']
drug_exposure=drug_exposure[drug_exposure['drug_concept_id'].isin(antican)]
#rxnorm['component_class_name'].value_counts()

# make labels from mapping concept IDs to concept labels
concept_lookup = {c.concept_id: c.concept_name for c in concept.itertuples()}

def make_labels(df):
    for c in df.columns:
        if 'concept_id' in c:
            df[c.replace('_id', '_label')] = df[c].map(concept_lookup)
        if 'concept_id' in c or 'source' in c or len(df[df[c].notna()])==0:
            df = df.drop(c, axis=1)
    return df

condition_occurrence_labelled = make_labels(condition_occurrence)
drug_exposure_labelled = make_labels(drug_exposure)
observation_labelled = make_labels(observation)
person_labelled = make_labels(person)
procedure_occurrence_labelled = make_labels(procedure_occurrence)

exclusions = ['dexamethasone']
drug_exposure_labelled=drug_exposure_labelled[~drug_exposure_labelled['drug_concept_label'].isin(exclusions)]


'''Reshaping dataframe'''
#reduce DF down to relevant variables for the visualization
small = drug_exposure_labelled[['person_id', 'drug_exposure_start_datetime', 'drug_concept_label']]
small = small.dropna()
small = small.drop_duplicates()
small_sorted = small.sort_values('drug_concept_label')
small['drug_concept_label'] = small_sorted.groupby(['person_id', 'drug_exposure_start_datetime'])['drug_concept_label'].transform(lambda x : ' & '.join(x))
#small.head()
small_nodup = small_sorted.drop_duplicates()
small_nodup['drug_concept_label']=small_nodup['drug_concept_label'].str.replace('& ', '&<br>')

# add new variable for every new drug administration per person
readministrations = pd.Series(np.zeros(len(small_nodup),dtype=int),index=small_nodup.index)

# Loop through all unique ids                                                                                                                                                                                      
all_id = small_nodup['person_id'].unique()
id_administrations = {}
for pid in all_id:
    # These are all the times a patient with a given ID has had surgery                                                                                                                                            
    patient = small_nodup.loc[small_nodup['person_id']==pid]
    administrations_sorted = pd.to_datetime(patient['drug_exposure_start_datetime'], format='%Y-%m-%d %H:%M:%S').sort_values()

# This checks if the previous surgery was longer than 180 days ago                                                                                                                                              
    frequency = administrations_sorted.diff()<dt.timedelta(days=6000)

    # Compute the readmission                                                                                                                                                                                      
    n_administrations = [0]
    for v in frequency.values[1:]:
       n_administrations.append((n_administrations[-1]+1)*v)

    # Add these value to the time series                                                                                                                                                                           
    readministrations.loc[administrations_sorted.index] = n_administrations

small_nodup['readministration'] = readministrations

#pivot the DF from long to wide
pivoted = small_nodup.pivot(index='person_id', columns='readministration', values='drug_concept_label').reset_index()
# add the prefix 'drug' to every instance
prefixed = pivoted.add_prefix('drug')
#remove the word 'drug' from other variables
renamed = prefixed.rename(columns={"drugperson_id": "person_id", "readministration":"index"})
#fill all empty cells with "N/A"
fillednones = renamed.fillna(" ")
#fillednones = renamed

#add a value of 1 to all data points for sums in the visualization
fillednones["value"] = 1


'''vis'''
app = Dash(__name__)

df = pd.DataFrame(fillednones)




'''dash'''

app.layout = html.Div(children=[
    html.H1(children='Sunburst'),

    dcc.Checklist(
            ['fluorouracil',
            'capecitabine',
            'cisplatin',
            'docetaxel',
            'gemcitabine',
            'carboplatin',
            'pembrolizumab',
            'paclitaxel',
            'allopurinol',
            'promethazine',
            'cetuximab',
            'prochlorperazine',
            'pemetrexed',
            'epirubicin',
            'etoposide',
            'prednisolone',
            'azacitidine',
            'vinorelbine',
            'cemiplimab',
            'dacarbazine',
            'rituximab',
            'leucovorin',
            'oxaliplatin',
            'zoledronic acid'],
            ['cisplatin','carboplatin'],
 id='first_treatment'
        ),

    dcc.Graph(
        id='hn_sunburst'
    ),
    dcc.Slider(
                    min=0,max=118,
                    value=10,
                    step=1,
                    id='sankey_slider'
                    )
])

#controls
@callback(
    Output(component_id='hn_sunburst', component_property='figure'),
    Input(component_id='sankey_slider', component_property='value'),
    Input(component_id='first_treatment', component_property='value')
)
def update_graph(slider_value, selected_treatments):
    column_names = list(df.columns.values)
    drug_num = column_names[2:(slider_value+2)] 
    dff = df[df['drug0'].isin(selected_treatments)]
    return px.sunburst(dff, path=drug_num, values='value', color='drug0', branchvalues='total')
    #fig.update_layout(hovermode=False)
    #set marker colors whose labels are " " to transparent
    marker_colors=list(fig.data[0].marker['colors'])
    marker_labels=list(fig.data[0]['labels'])
    new_marker_colors=["rgba(0,0,0,0)" if label==" " else color for (color, label) in zip(marker_colors, marker_labels)]
    marker_colors=new_marker_colors
    fig.data[0].marker['colors'] = marker_colors



if __name__ == '__main__':
    app.run(debug=True)
