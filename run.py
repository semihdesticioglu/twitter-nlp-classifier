#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import plotly
import pandas as pd
import re

from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

from flask import Flask
from flask import render_template, request, jsonify
from plotly.graph_objs import Bar
import joblib
from sqlalchemy import create_engine


# In[ ]:

app = Flask(__name__ , template_folder='templates')

def tokenize(text):
    text = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())
    
    url_regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    detected_urls = re.findall(url_regex, text)
    for url in detected_urls:
        text = text.replace(url, "urlplaceholder")
    
    tokens = word_tokenize(text)
    stop_words = list(set(stopwords.words('english')))
    clean_tokens = [lemmatizer.lemmatize(word) for word in tokens if word not in stop_words]
     
    return clean_tokens


# In[ ]:


# load data
engine = create_engine('sqlite:///messages.db')
df = pd.read_sql_table('messages', engine)

# load model
model = joblib.load("classifier.pkl")


# In[ ]:


# index webpage displays cool visuals and receives user input text for model
@app.route('/')
@app.route('/index')
def index():
    
    # extract data needed for visuals
    # TODO: Below is an example - modify to extract data for your own visuals
    genre_counts = df.groupby('genre').count()['message']
    genre_names = list(genre_counts.index)
    
    category_names = df.iloc[:,4:].columns
    category_boolean = (df.iloc[:,4:] != 0).sum().values
    
    
    # create visuals

    graphs = [ {
            'data': [Bar( x=category_names, y=category_boolean)],
             'layout': { 'title': 'Distribution of Message Categories',
               'yaxis': { 'title': "Frequency Count"}, 'xaxis': { 'title': "Category",'tickangle': 35}   }
             } ]
    
    # encode plotly graphs in JSON
    ids = ["graph-{}".format(i) for i, _ in enumerate(graphs)]
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)
    
    # render web page with plotly graphs
    return render_template('master.html', ids=ids, graphJSON=graphJSON)


# In[ ]:


@app.route('/go')
def go():
    # save user input in query
    query = request.args.get('query', '')

    # use model to predict classification for query
    classification_labels = model.predict([query])[0]
    classification_results = dict(zip(df.columns[4:], classification_labels))

    # This will render the go.html 
    return render_template(
        'go.html',
        query=query,
        classification_result=classification_results
    )


# In[ ]:


def main():
    app.run(host='0.0.0.0', port=3001, debug=True)


# In[ ]:



if __name__ == '__main__':
    main()

