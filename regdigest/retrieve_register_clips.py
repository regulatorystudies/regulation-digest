# -*- coding: utf-8 -*-
"""
Created on Mon Jun 13 12:19:24 2022

@author: mark
"""

#%% Init

import requests
import webbrowser

#%% Configure Parameters

# endpoint: /documents.{format}

# define endpoint url
endpoint_url = r'https://www.federalregister.gov/api/v1/documents.csv?'

# define parameters
res_per_page = 1000
sort_order = 'oldest'
fieldsList = ['publication_date', 'agency_names', 'citation', 
              'html_url', 'title', 'type', 
              'action', 'significant', 'correction_of']
start_date = input("Input start date [yyyy-mm-dd]: ")

# dictionary of parameters
dcts_params = {'per_page': res_per_page, 
               'order': sort_order, 
               'fields[]': fieldsList, 
               'conditions[publication_date][gte]': str(start_date)
              }

print('Ready to go!')

#%% Retrieve Data

# get documents
dcts_response = requests.get(endpoint_url, params=dcts_params)
print(dcts_response.status_code,
      dcts_response.headers['Date'],
      'Click url and option to download CSV should pop up...',
      dcts_response.url, sep='\n')  # print request URL

webbrowser.open(dcts_response.url, new = 1)
