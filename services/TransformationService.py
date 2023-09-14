import pandas as pd
from pandas import DataFrame
import re
from entity.File import File
from transformation.DatatypeTransformer import DtypesTransformer
from transformation.FillNaTransformer import FillNaTransformer
from transformation.FilterTransformer import FilterTransformer
from transformation.RenameTransformer import RenameTransformer
from transformation.RegexTransformer import RegexTrasformer
from transformation.DropcolTransformer import DropcolTransformer
from transformation.AddcolTransformer import AddcolTransformer
from utils import Configuration,constant

class TransformationService:

    def __init__(self):
        self.raw_file_path = Configuration.RAW_FILE_PATH
        self.transform_file_path = Configuration.TRANSFORM_FILE_PATH
        self.transformers = {
            "rename": RenameTransformer(),
            "fillNa": FillNaTransformer(),
            "dtypes": DtypesTransformer(),
            "filter": FilterTransformer(),
            "regex": RegexTrasformer(),
            "drop_column":DropcolTransformer(),
            "addcol":AddcolTransformer()

        }




    def default_column_mapping_generator(self, file: File):
        if len(file.seperator) == 1:
            dataframe = pd.read_csv(self.raw_file_path + file.file_name, sep=file.seperator,engine='python')
        else:
            dataframe = pd.read_csv(self.raw_file_path + file.file_name, sep=file.seperator, on_bad_lines='skip',engine='python')
        columns = dataframe.columns.tolist()
        column_mapping = {}
        for column in columns:
            column_name = column.split(",")
            for name in column_name:
                column_mapping[name] = re.sub(f'[^{constant.allowed_chars}]', '', name)
        return column_mapping

    def transform_columns(self, file: File):
        if len(file.seperator) == 1:
            dataframe = pd.read_csv(self.raw_file_path + file.file_name, sep=file.seperator,engine='python')
        else:
            dataframe = pd.read_csv(self.raw_file_path + file.file_name, sep=file.seperator, on_bad_lines='skip',engine='python')
        self.write_to_file(dataframe.rename(columns=file.column_mapping), file)

    def get_transformed_dataframe(self, file: File):
        if len(file.seperator) == 1:
            return pd.read_csv(self.transform_file_path + file.file_name, sep=file.seperator,engine='python')
        else:
            return pd.read_csv(self.transform_file_path + file.file_name, sep=file.seperator, on_bad_lines='skip',engine='python')

    def write_to_file(self, dataframe: DataFrame, file):
        if len(file.seperator) == 1:
            dataframe.to_csv(self.transform_file_path + file.file_name, sep=file.seperator, index=False, header=True)
        elif file.seperator == '\t':
            dataframe.to_csv(self.transform_file_path + file.file_name, sep='\t', index=False, header=True)
        else:
            dataframe.to_csv(self.transform_file_path + file.file_name, sep='\t', index=False, header=True)


    def apply_transformations(self, file: File, transformations: dict):
        
        if len(file.seperator) == 1:
            dataframe = pd.read_csv(self.transform_file_path + file.file_name, sep=file.seperator,engine='python')
        else:
            dataframe = df = pd.read_csv(self.transform_file_path + file.file_name, sep=file.seperator, on_bad_lines='skip',engine='python')
        try:
            dataframe["date"] = dataframe["date"].dt.strftime('%Y-%m-%d')
        except:
            dataframe['date'] = pd.to_datetime(dataframe['date']).dt.strftime('%Y-%m-%d')
        for transformation in transformations:
            dataframe = self.transformers[transformation["type"]].transform(dataframe=dataframe,
                                                                transformation_config=transformation)
        self.write_to_file(dataframe, file)
        return dataframe
    
    def get_transformations_details(self,transformations: dict):
        data = {}  # Initialize an empty dictionary

        for i in transformations:
            col_name = i["col"]
            
            # Create a dictionary for the column if it doesn't exist
            if col_name not in data:
                data[col_name] = {}

            if i["type"] == 'rename':
                data[col_name]["renamed_column"] = i["new_col"]
            elif i["type"] == 'fillNa':
                data[col_name]["default_value"] = i["value"]
            elif i["type"] == 'dtypes':
                data[col_name]["default_dtypes"] = i["dtypes"]
            elif i["type"] == 'filter':
                data[col_name]["filter_used"] = {"operator": i['operator'], "value": i['value']}
            elif i["type"] == 'regex':
                data[col_name]["value_replace"] = {"value_replaced": i['regex'], "value_added": i['replace_by']}
            elif i["type"] == 'drop_column':
                data[col_name]['column_drop'] = True
            elif i["type"] == "addcol":
                data[col_name]['new_column'] = {"is_new": True}
        return data
