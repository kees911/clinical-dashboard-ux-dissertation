import requests
import numpy as np
import pandas as pd

''' API CALLS '''

def call_api(id_number, key='name'):
    #API url
    url = 'API URL goes here'
    #make request of the URL
    r = requests.get(url)
    #turn it into a json
    item_dict = r.json()

    identities = []
    names = []
    typeses = []
    spriteses = []
    for item in item_dict['results']:
        name = item['name']
        identity = item['id']
        types = item['types']

        identities.append(identity)
        names.append(name)
        typeses.append(types)

    item_df = pd.DataFrame({'ids': identities, 'names': names, 'types': typeses})
    return item_df

def get_id(arguments):
    url.format(id=id_number)
    '''
    Get id from command line arguments.
    '''
    return arguments['--id']

def __main__():
    '''
    Entrypoint of command line interface.
    '''
    from docopt import docopt
    arguments = docopt(__doc__, version='0.1.0')
    id_number = get_id(arguments)
    print(call_api(id_number))

df = call_api()


''' FLASK '''

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/prototypes')
def about():
    return render_template('prototypes.html')

if __name__ == '__main__':
    app.run(debug=True)