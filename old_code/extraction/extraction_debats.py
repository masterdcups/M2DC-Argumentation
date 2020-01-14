import requests
import json


def main():
    wikidebats_api_url = 'https://wikidebats.org/w/api.php'

    requests_parameters = {
            'debats_construits': {   
                'action': 'query',
                'list': 'categorymembers',
                'cmtitle': 'Category:Débats construits'
            },
    }

    parameters = requests_parameters['debats_construits']
    parameters['format'] = 'json'

    response = requests.get(wikidebats_api_url, params=parameters)
    print("url:", response.url)

    response_json = response.json()
    print(json.dumps(response_json, indent=2, ensure_ascii=False), '\n')

    category_pages = [
        (member['pageid'],member['title'])
        for member in response_json['query']['categorymembers']
    ]

    print(*category_pages, sep='\n')

    # Request the wikitext of the first page found.
    #response = requests.get(wikidebats_api_url, params={
    #    'action':'query', 'prop':'revisions', 'titles':category_pages[0][1],
    #    'rvprop':'content', 'format':'json'
    #})

    # Request the html of the first page found.
    response = requests.get(wikidebats_api_url, params={
        'action':'parse', 'pageid': category_pages[0][0],
        'format':'json'
    })

    with open('debat.html', 'w') as f:
        f.write(response.json()['parse']['text']['*'])
    
    return

    # After this is some code to agregate the batches returned by a query.
    # (you might need to use something different than "accontinue")

    # Get the list of results of the query ("list": [{...}]).
    # This dictionary will accumulate the results of each batch.
    responses = response_json['query']

    # Second level header of the response ("query":{"result_list":[]})
    # For the categories request, this is "allcategories".
    result_lists = list(responses.keys())
    print("Result lists:", result_lists)

    # Reponse contains a continue field as long as there is data to be fetched.
    while 'continue' in response_json:
        # Add the continue parameter (title of next page).
        parameters['accontinue'] = response_json['continue']['accontinue']

        # Get the next batch. 
        response = requests.get(wikidebats_api_url, params=parameters)
        response_json = response.json()
        print(json.dumps(response_json, indent=2, ensure_ascii=False), '\n')

        # Append each query results to its correponding accumulator.
        for result_list in result_lists:
            responses[result_list].append(response_json['query'][result_list])


    with open('responses.json', 'w') as f:
        f.write(json.dumps(responses, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
