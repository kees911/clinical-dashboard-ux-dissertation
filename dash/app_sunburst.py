# synpuff.ipynb content
import pandas as pd
pd.set_option("display.max_rows", None, "mode.chained_assignment", None)
from itertools import chain

import numpy as np
import datetime as dt

from dash import Dash, html, dcc, Input, Output, State, callback, callback_context
import plotly.express as px
import plotly
import plotly.offline
import plotly.graph_objs as go

'''Georgie's code'''
# copy the data to your drive and then modify this path as required

folder = '../synpuff/'

# base query for generating the cohort
person = pd.read_csv('../clinical-dashboard-ux-dissertation/synpuff/person.csv')
condition_occurrence = pd.read_csv('../clinical-dashboard-ux-dissertation/synpuff/condition_occurrence.csv')
drug_exposure = pd.read_csv('../clinical-dashboard-ux-dissertation/synpuff/drug_exposure.csv')
concept = pd.read_csv('../clinical-dashboard-ux-dissertation/synpuff/concept.csv')
hierarchy = pd.read_csv('../clinical-dashboard-ux-dissertation/synpuff/hierarchy.csv')
props = pd.read_csv('../clinical-dashboard-ux-dissertation/synpuff/hemonc_component_properties.csv')

neoplasm_codes = [44832128,44834489,44834490,44819488,44826452,44825256]
condition_occurrence=condition_occurrence.loc[condition_occurrence['condition_source_concept_id'].isin(neoplasm_codes)]

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
person_labelled = make_labels(person)

'''Applying extra filters to drug df'''
drug_exposure_labelled['drug_exposure_year'] = pd.to_datetime(drug_exposure_labelled['drug_exposure_start_date'], format='%Y-%m-%d').dt.year
exclusions = ['dexamethasone']
drug_exposure_labelled=drug_exposure_labelled[~drug_exposure_labelled['drug_concept_label'].isin(exclusions)]

'''Data Linkage'''
person_labelled_small= person_labelled.loc[:,['person_id', 'year_of_birth', 'gender_concept_label']]
drug_persons = pd.merge(drug_exposure_labelled, person_labelled_small, on='person_id', how='left')
drug_persons['age_at_treatment'] = drug_persons['drug_exposure_year'] - drug_persons['year_of_birth']
#condition linkage
condition_labelled_small= condition_occurrence_labelled.loc[:,['person_id', 'condition_concept_label']]
condition_labelled_small['occ_number'] = 'cond_' + (condition_labelled_small.groupby('person_id').cumcount()).astype(str) 
cond_pivot = condition_labelled_small.pivot(index='person_id', columns='occ_number', values='condition_concept_label').reset_index()
drug_persons = pd.merge(drug_persons, cond_pivot, on='person_id', how='left')
'''Reshaping dataframe'''
#reduce DF down to relevant variables for the visualization
small = drug_persons[['person_id', 'drug_exposure_start_date', 'drug_concept_label', 'drug_exposure_year', 'gender_concept_label', 'age_at_treatment', 'cond_0', 'cond_1', 'cond_2', 'cond_3']]
#small = pd.merge(small, cond_pivot, on='person_id', how='left')
#small = small.dropna()
small = small.drop_duplicates()
small_sorted = small.sort_values('drug_concept_label')
#small['drug_concept_label'] = small_sorted.groupby(['person_id', 'drug_exposure_start_date'])['drug_concept_label'].transform(lambda x : ' & '.join(x))
#small.head()
small_nodup = small_sorted.drop_duplicates()
#small_nodup['drug_concept_label']=small_nodup['drug_concept_label'].str.replace('& ', '&<br>')

# add new variable for every new drug administration per person
readministrations = pd.Series(np.zeros(len(small_nodup),dtype=int),index=small_nodup.index)

# Loop through all unique ids                                                                                                                                                                                      
all_id = small_nodup['person_id'].unique()
id_administrations = {}
for pid in all_id:
    # These are all the times a patient with a given ID has had surgery                                                                                                                                            
    patient = small_nodup.loc[small_nodup['person_id']==pid]
    administrations_sorted = pd.to_datetime(patient['drug_exposure_start_date'], format='%Y-%m-%d').sort_values()

# This checks if the previous surgery was longer than 180 days ago                                                                                                                                              
    frequency = administrations_sorted.diff()<dt.timedelta(days=6000)

    # Compute the readmission                                                                                                                                                                                      
    n_administrations = [0]
    for v in frequency.values[1:]:
       n_administrations.append((n_administrations[-1]+1)*v)

    # Add these value to the time series                                                                                                                                                                           
    readministrations.loc[administrations_sorted.index] = n_administrations

small_nodup['readministration'] = readministrations
#small_nodup['drug_concept_label'] = small_nodup['drug_concept_label'] + (small_nodup['readministration'].apply(lambda x: x*' '))

#pivot the DF from long to wide
pivoted = small_nodup.pivot(index='person_id', columns='readministration', values='drug_concept_label').reset_index()
# add the prefix 'drug' to every instance
prefixed = pivoted.add_prefix('drug')
#remove the word 'drug' from other variables
df = prefixed.rename(columns={"drugperson_id": "person_id", "readministration":"index"})
df.sort_values('drug0')
#add a value of 1 to all data points for sums in the visualization
df["value"] = 1
#fill all empty cells with "N/A"
df = df.fillna(" ")

'''vis'''

    


'''dash'''
app = Dash(__name__)

drugoptions = ['epoetin alfa',
               'cyclophosphamide',
               'methylprednisolone',
               'filgrastim',
               'paclitaxel',
               'doxorubicin',
               'leuprolide',
               'azacitidine',
               'triptorelin',
               'hydrocortisone',
               'octreotide',
               'methotrexate']

options = ['Malignant neoplasm of nipple and areola of female breast',
            'Malignant neoplasm of axillary tail of female breast',
            'Malignant neoplasm of other specified sites of female breast',
            'Carcinoma in situ of breast']

app.layout = html.Div(children=[
    html.H1(children='Sunburst', style={'textAlign':'center'}),

    #Left menu 1
    html.Div([
        html.B(children='First Drug', style={'textAlign':'left'}),
        # first treatment
        dcc.Checklist(
            drugoptions,
            ['doxorubicin','cyclophosphamide'],
        id='first_treatment'
        ),
        html.Br(),
        dcc.Checklist(
            [{"label":"Select all drugs", "value":"Alldrugs"}],
            options,
            id='all_drugs_or_none'
            )
    ], style={'display':'inline-block', 'width':'10%'}),

    #Left menu 2
    html.Div([
        html.B(children='Sex', style={'textAlign':'left'}),
        dcc.Checklist(
            ['MALE', 'FEMALE'],
            ['MALE', 'FEMALE'],
        id='person_gender'
        ),
        html.B(children='Age at treatment', style={'textAlign':'left'}),
        dcc.RangeSlider(min=26, max=101, value=[26, 101],
        id='age_at_treatment',
        tooltip={
            "always_visible": False
        }
        ),
        html.B(children='Treatment Year', style={'textAlign':'left'}),
        dcc.Checklist(
            [2007, 2008, 2009, 2010],
            [2007, 2008, 2009, 2010],
        id='treatment_year'
        )
    ], style={'display':'inline-block', 'width':'10%'}),

    #Right main
    html.Div(
        [
            #Graph container
            html.Div(
                dcc.Graph(
                    id='hn_sankey',
                    style={'marginLeft':'25%','marginRight':'25%'}
                    )
            ),

            #Slider container
            html.Div(
                dcc.Slider(
                    min=0,max=4, step=1,
                    value=2,
                    id='sankey_slider',
                    tooltip={
                        "always_visible": True
                    }
                    )
            ),
            html.B(children='Condition', style={'textAlign':'left'}),
            dcc.Checklist(
            [{"label":"Select all conditions", "value":"All"}],
            value=[],
            id='all_or_none'
            ),
            dcc.Checklist(
            options,
            value=["Malignant neoplasm of nipple and areola of female breast"],
            inline=True,
            id='condition'
        )
        ], style={'display':'inline-block', 'width':'80%', 'height':'900px'}
    )
])

#controls
@callback(
    Output(component_id="condition", component_property="value"),
    Output(component_id="all_or_none", component_property="value"),
    Input(component_id="condition", component_property="value"),
    Input(component_id="all_or_none", component_property="value"),
    prevent_initial_call=True,
)
def select_all_none(conds_selected, all_selected):
    ctx=callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id=="condition":
        all_selected = ["All"] if set (conds_selected) == set(options) else []
    else:
        conds_selected = options if all_selected else []
    return conds_selected, all_selected

@callback(
    Output(component_id="first_treatment", component_property="value"),
    Output(component_id="all_drugs_or_none", component_property="value"),
    Input(component_id="first_treatment", component_property="value"),
    Input(component_id="all_drugs_or_none", component_property="value"),
    prevent_initial_call=True,
)
def select_all_drugs(drugs_selected, all_drugs_selected):
    ctx=callback_context
    input_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if input_id=="first_treatment":
        all_drugs_selected = ["Alldrugs"] if set (drugs_selected) == set(drugoptions) else []
    else:
        drugs_selected = drugoptions if all_drugs_selected else []
    return drugs_selected, all_drugs_selected

@callback(
    Output(component_id='hn_sankey', component_property='figure', allow_duplicate=True),
    Input(component_id='person_gender', component_property='value'),
    Input(component_id='age_at_treatment', component_property='value'),
    Input(component_id='treatment_year', component_property='value'),
    Input(component_id='first_treatment', component_property='value'),
    Input(component_id='sankey_slider', component_property='value'),
    Input(component_id='condition', component_property='value'),
    prevent_initial_call='initial_duplicate',
)
def update_graph(selected_genders, selected_ages, selected_years, selected_treatments, slider_value, selected_conditions):
    global small_nodup
    nodup = small_nodup.copy()
    nodup = nodup[nodup[['cond_0','cond_1','cond_2','cond_3']].isin(selected_conditions).any(axis=1)]
    nodup = nodup[nodup['gender_concept_label'].isin(selected_genders)]
    nodup = nodup[nodup['age_at_treatment'] >= selected_ages[0]]
    nodup = nodup[nodup['age_at_treatment'] <= selected_ages[1]]
    nodup = nodup[nodup['drug_exposure_year'].isin(selected_years)]

    #reshape DF
    #pivot the DF from long to wide
    pivoted = nodup.pivot(index='person_id', columns='readministration', values='drug_concept_label').reset_index()
    # add the prefix 'drug' to every instance
    prefixed = pivoted.add_prefix('drug')
    #remove the word 'drug' from other variables
    df = prefixed.rename(columns={"drugperson_id": "person_id", "readministration":"index"})
    df.sort_values('drug0')
    #add a value of 1 to all data points for sums in the visualization
    df["value"] = 1

    #other filters
    column_names_list = df.columns.values.tolist()
    drug_num = column_names_list[1:slider_value+1] 
    df = df[df['drug0'].isin(selected_treatments)]
    df = df.fillna(" ")
    
    colordict = {'epoetin alfa':'#EF553B',
               'cyclophosphamide':'#636EFA',
               'methylprednisolone':'#00CC96',
               'filgrastim':'#AB63FA',
               'paclitaxel':'#FFA15A',
               'doxorubicin':'#19D3F3',
               'leuprolide':'#FF6692',
               'azacitidine':'#B6E880',
               'triptorelin':'#FF97FF',
               'hydrocortisone':'#FECB52',
               'octreotide':'#8C564B',
               'methotrexate':'#7F7F7F',
               '(?)':'#FFFFFF'}

    fig = px.sunburst(df, path=drug_num, values='value', width=600, height=600, color='drug0', color_discrete_map=colordict)
    #fig.update_layout(hovermode=False)
    
    #set marker colors whose labels are " " to transparent
    marker_colors=list(fig.data[0].marker['colors'])
    marker_labels=list(fig.data[0]['labels'])
    new_marker_colors=["rgba(0,0,0,0)" if ((label==" ")or(label=="1")) else color for (color, label) in zip(marker_colors, marker_labels)]
    marker_colors=new_marker_colors
    fig.data[0].marker['colors'] = marker_colors
    
    
    return fig



if __name__ == '__main__':
    app.run(debug=True, port=8000)

