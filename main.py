from flask import Flask, request, render_template
from elasticsearch import Elasticsearch
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib,time
import tkinter as tk
matplotlib.use('Agg')
app = Flask(__name__)

# Define Elasticsearch connection
es = Elasticsearch(
    ['http://localhost:9200'],
    basic_auth=('elastic', 'KZ2yaUbgf-wVS7bbY*g1'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    if request.method == 'GET':
        # Get user input from form
        search_term = request.args.get('search_term')

        # Search Elasticsearch using user input
        response = es.search(
            index='lambdalog',
            size=4000,
            body={
                "query": {
                    "multi_match": {
                        "query": search_term,
                        "fields": ["mimetype"]
                    }
                }
            }
        )

        # Return search results as a list of dictionaries
        results = [hit['_source'] for hit in response['hits']['hits']]

        # Render filter.html template with search results
        return render_template('filter.html', results=results)
    else:
        return 'Invalid request'
    
@app.route('/visual')
def visual():
    search_term = request.args.get('search_term')

    # Search Elasticsearch using user input
    response = es.search(
        index='lambdalog',
        size=4000,
        body={
            "query": {
                "multi_match": {
                    "query": search_term,
                    "fields": ["mimetype"]
                }
            }
        }
    )

    # Convert search results to a DataFrame
    df = pd.DataFrame([hit['_source'] for hit in response['hits']['hits']])

    # Count the number of occurrences of each mimetype for the search term and create a bar chart
    mimetype_counts = df['mimetype'].value_counts()
    plt.clf()
    plt.bar(mimetype_counts.index, mimetype_counts.values)
    plt.title('Mimetype Counts for "{}"'.format(search_term))
    plt.xlabel('Mimetype')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    filename = 'image_{}_{}.png'.format(search_term, int(time.time()))
    plt.savefig('static/{}'.format(filename), format='png')

    # Convert the plot to base64-encoded HTML
    from io import BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    print("Image saved")
    buffer.seek(0)
    import base64
    image_png = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    html_fig = 'data:image/png;base64,' + image_png
    print(search_term, html_fig, mimetype_counts)

    response_all = es.search(
    index='lambdalog',
    size=4000,
    body={
        "query": {
            "match_all": {}
        }
    }
)

    dfall = pd.DataFrame([hit['_source'] for hit in response_all['hits']['hits']])
    # Count the number of occurrences of each mimetype for all documents and create a bar chart
    all_mimetype_counts = dfall['mimetype'].value_counts()
    plt.clf()
    plt.bar(all_mimetype_counts.index, all_mimetype_counts.values)
    plt.title('Mimetype Counts for All Documents')
    plt.xlabel('ALL_Mimetype')
    plt.ylabel('Count')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    all_filename = 'all_image_{}.png'.format(int(time.time()))
    plt.savefig('static/{}'.format(all_filename), format='png')

    # Convert the plot to base64-encoded HTML
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    print("Image saved")
    buffer.seek(0)
    all_image_png = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()
    all_html_fig = 'data:image/png;base64,' + all_image_png

    # Render the HTML template with the necessary variables
    return render_template('visualization.html', search_term=search_term, filename=filename, mimetype_counts=mimetype_counts, all_filename=all_filename, all_mimetype_counts=all_mimetype_counts, all_html_fig=all_html_fig)

if __name__ == '__main__':
   
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.run()