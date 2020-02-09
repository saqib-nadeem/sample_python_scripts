from flask import jsonify, url_for, request, make_response

from flask.ext.restful import reqparse, abort

from web_api.models import db

import requests
import base64
import json

#### Helper Functions ####

def abort_if_record_doesnt_exist(id, entity):
    if entity is None:
        abort(404, message="ID {} doesn't exist".format(id))        

def update_record(table_name, id, args, table_name_prefix):
    record = table_name.query.filter_by(id=id).first()
    abort_if_record_doesnt_exist(id,record)
    
    for field, value in args.iteritems():
        if value is not None:
            setattr(record, field, value)

    db.session.commit()
    #output = get_record_by_ID(table_name, record.id, table_name_prefix)
    return args

def get_all_records(table_name, table_name_prefix):
    records = table_name.query.all()
    output = []

    for record in records:
        row = {}

        for field in table_name.__table__.c:
            field = str(field).replace(table_name_prefix + ".","")
            row[field] = getattr(record, field, None)

        output.append(row)

    return output

def get_record_by_ID(table_name, id, table_name_prefix):
    record = table_name.query.filter_by(id=id).first()
    abort_if_record_doesnt_exist(id,record)
    output = []
    row = {}

    for field in table_name.__table__.c:
        field = str(field).replace(table_name_prefix + ".","")
        row[field] = getattr(record, field, None)

    output.append(row)

    return output

def delete_record(table_name, id):
    record = table_name.query.filter_by(id=id).first()
    abort_if_record_doesnt_exist(id,record)
    db.session.delete(record)
    db.session.commit()

API_KEY = "f29d71ee-9794-4a9f-b2bd-bf30486dec2e" 
vault_id = "cbfa6631-e3f3-4c05-b63a-70f2a99823cf"
base_url = "https://api.truevault.com/"
api_version = "v1"

def create_vault(name):
    url = base_url + api_version + "/vaults" 
    payload = {'name': name}
    response = requests.post(url, data=payload, auth=(API_KEY, ''))
    return response

def get_vault(vault_id):
    url = base_url + api_version + "/vaults/" + vault_id 
    response = requests.get(url, auth=(API_KEY, ''))
    vault = response.json()['vault']['name']
    return vault

def get_all_vaults(page, per_page):
    url = base_url + api_version + "/vaults" 
    payload = {'page': page, 'per_page': per_page} 
    response = requests.get(url, params=payload, auth=(API_KEY, ''))
    vaults = response.json()['vaults']
    return vaults

def update_vault(vault_id, name):
    url = base_url + api_version + "/vaults/" + vault_id
    payload = {'name': name} 
    response = requests.put(url, data=payload, auth=(API_KEY, ''))
    return response

def delete_vault(vault_id):
    url = base_url + api_version + "/vaults/" + vault_id
    response = requests.delete(url, auth=(API_KEY, ''))
    return response

#schema_id = 'ac9a45c0-9e3d-481d-a185-0b4e7904d080'
def create_document(vault_id, schema_id, document):
    url = base_url + api_version + "/vaults/" + vault_id + "/documents" 
    data = base64.b64encode(json.dumps(document))
    payload = {'document': data, 'schema_id': schema_id}
    response = requests.post(url, data=payload, auth=(API_KEY, ''))
    return response
    
#document_id = '2ad2afc0-c3be-43c8-a760-33520d565d16'
def get_document(vault_id, document_id):
    url = base_url + api_version + "/vaults/" + vault_id + "/documents/" + document_id
    response = requests.get(url, auth=(API_KEY, ''))
    document = base64.b64decode(str(response.text))
    return document

def get_all_documents(vault_id, full, page, per_page):
    url = base_url + api_version + "/vaults/" + vault_id + "/documents"
    payload = {'full': full, 'page': page, 'per_page':per_page} 
    response = requests.get(url, params=payload, auth=(API_KEY, ''))
    documents = response.json()
    return documents

def get_all_documents_with_schema(vault_id, schema_id, full, page, per_page):
    url = base_url + api_version + "/vaults/" + vault_id + "/schemas/" + schema_id + "/documents"
    payload = {'full': full, 'page': page, 'per_page':per_page} 
    response = requests.get(url, params=payload, auth=(API_KEY, ''))
    result = response.json()
    data = []
    for document in result['data']['items']:
        data.append(get_document(vault_id, document['id']))
    return data

def update_document(vault_id, document_id, schema_id, document):
    url = base_url + api_version + "/vaults/" + vault_id + "/documents/" + document_id
    data = base64.b64encode(json.dumps(document))
    payload = {'document': data, 'schema_id': schema_id} 
    response = requests.put(url, data=payload, auth=(API_KEY, ''))
    return response

def delete_document(vault_id, document_id):
    url = base_url + api_version + "/vaults/" + vault_id + "/documents/" + document_id
    response = requests.delete(url, auth=(API_KEY, ''))
    return response

def create_schema(vault_id, document):
    url = base_url + api_version + "/vaults/" + vault_id + "/schemas"
    data = base64.b64encode(json.dumps(document))
    payload = {'schema': data}
    response = requests.post(url, data=payload, auth=(API_KEY, ''))
    return response

def get_schema(vault_id, schema_id):
    url = base_url + api_version + "/vaults/" + vault_id + "/schemas/" + schema_id
    response = requests.get(url, auth=(API_KEY, ''))
    schema = response.json()
    return schema

def get_all_schemas(vault_id):
    url = base_url + api_version + "/vaults/" + vault_id + "/schemas"
    response = requests.get(url, auth=(API_KEY, ''))
    schemas = response.json()
    return schemas

def update_schema(vault_id, schema_id, document):
    url = base_url + api_version + "/vaults/" + vault_id + "/schemas/" + schema_id
    data = base64.b64encode(json.dumps(document))
    payload = {'schema': data} 
    response = requests.put(url, data=payload, auth=(API_KEY, ''))
    return response

def delete_schema(vault_id, schema_id):
    url = base_url + api_version + "/vaults/" + vault_id + "/schemas/" + schema_id
    response = requests.delete(url, auth=(API_KEY, ''))
    return response 


 