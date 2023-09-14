import json
import urllib.parse

import requests


class DremioHelper:

    def __init__(self, url, username, password) -> None:
        self.url = url
        self.username = username
        self.password = password

    # def get_access_token(self):
    #     try:
    #         return self.get_access_token_data()
    #     except:
    #         return 'this is bibek'
    def get_access_token(self):
        access_token_endpoint = "/apiv2/login"
        access_token_payload = json.dumps({
            "userName": self.username,
            "password": self.password
        })

        access_token_headers = {'Content-Type': 'application/json'}
        access_token_response = requests.request("POST", self.url + access_token_endpoint, headers=access_token_headers,
                                                 data=access_token_payload)

        if access_token_response.status_code == 200:
            return access_token_response.json()["token"]
        else:
            raise BaseException(access_token_response.text)


    def get_catalog_by_path(self, catalog_path):
        catalog_id_by_path_endpoint = "/api/v3/catalog/by-path" + catalog_path

        catalog_headers = {
            "Authorization": "_dremio" + self.get_access_token(),
            'Content-Type': 'application/json'
        }
        catalog_payload = {}
        catalog_id_by_path_response = requests.request("GET", self.url + catalog_id_by_path_endpoint,
                                                       headers=catalog_headers, data=catalog_payload)

        if catalog_id_by_path_response.status_code == 200:
            return catalog_id_by_path_response.json()
        else:
            raise BaseException(catalog_id_by_path_response.text)

    def format_folder(self, catalog_path):

        format_folder_endpoint = "/api/v3/catalog/"
        format_folder_headers = {
            "Authorization": "_dremio" + self.get_access_token(),
            'Content-Type': 'application/json'
        }
        catalog = self.get_catalog_by_path(catalog_path=catalog_path)
        catalog_id = self.encode_to_utf_8(catalog["id"])
        format_folder_payload = json.dumps({
            "entityType": "dataset",
            "type": "PHYSICAL_DATASET",
            "path": catalog["path"],
            "format": {
                "type": "Parquet"
            }
        })

        if catalog["entityType"] == "dataset":
            # already formatted, so alter the table or vds
            return self.alter_dataset("\"" + "\".\"".join(catalog['path']) + "\"")

        format_folder_response = requests.request("POST", self.url + format_folder_endpoint + catalog_id,
                                                  headers=format_folder_headers, data=format_folder_payload)

        if format_folder_response.status_code == 200:
            return format_folder_response.json()
        else:
            raise BaseException(format_folder_response.json())
        
    def encode_to_utf_8(self, uri):
        return urllib.parse.quote_plus(uri)

    def execute_sql_query(self, query):
        sql_query_endpoint = "/api/v3/sql"
        sql_query_payload = json.dumps({
            "sql": query
        })

        sql_query_headers = {
            "Authorization": "_dremio" + self.get_access_token(),
            'Content-Type': 'application/json'
        }
        sql_query_response = requests.request("POST", self.url + sql_query_endpoint, headers=sql_query_headers,
                                              data=sql_query_payload)
        if sql_query_response.status_code == 200:
            return sql_query_response.json()
        else:
            raise BaseException(sql_query_response.json())

    def job_api(self, job_id):
        job_api_endpoint = "/api/v3/job/" + job_id
        job_payload = {}
        job_headers = {
            "Authorization": "_dremio" + self.get_access_token(),
            'Content-Type': 'application/json'
        }
        job_api_response = requests.request("POST", self.url + job_api_endpoint, headers=job_headers, data=job_payload)
        if job_api_response.status_code == 200:
            return job_api_response.json()
        else:
            raise BaseException(job_api_response.json())
        pass

    def alter_dataset(self, dataset):
        print(dataset)
        #dataset = dataset.replace('/','"."').replace('".', '', 1)+'"'
        query = f"ALTER TABLE {dataset} REFRESH METADATA"
        print(query)
        return self.execute_sql_query(query=query)
    
    def create_vds(self,vds_name,dataset):
        dataset = dataset.replace('/','"."').replace('".', '', 1)+'"'
        query = f"create vds {vds_name} as (select * from {dataset})"
        return self.execute_sql_query(query=query)

    def check_dremio_conn(self):
        try: 
            self.get_access_token()
            return True
        except:
            return False