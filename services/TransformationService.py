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
from transformation.DeleteTransformer import DeleteTransformer
from utils import Configuration, exception_handler, constant
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
            "addcol":AddcolTransformer(),
            "delete":DeleteTransformer()

        }

    # Function to remove commas and convert to numeric
    def remove_commas_and_convert(self,value):
        if isinstance(value, str):
            try:
                # Check if the value can be converted to a numeric type (int or float)
                numeric_value = float(value.replace(',', ''))
                if numeric_value.is_integer():
                    return int(numeric_value)
                return numeric_value
            except ValueError:
                pass
        return value


    def default_column_mapping_generator(self, file: File):
        if len(file.file_separator) == 1:
            dataframe = pd.read_csv(self.raw_file_path + file.file_name, sep=file.file_separator,engine='python')
        else:
            dataframe = pd.read_csv(self.raw_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')
        columns = dataframe.columns.tolist()
        column_mapping = {}
        for column in columns:
            column_name = column.split(",")
            for name in column_name:
                column_mapping[name] = re.sub(
                    f'[^{constant.allowed_chars}]',
                    '', 
                    name.split('=')[0].strip().replace(' ','_').replace('-',' ')
                    )
        return column_mapping
    
    def replace_variables(self,expression):
        # Define a regex pattern to match !#variable#!
        pattern = r'!#(\w+)#!'

        # Define a function to replace matched patterns
        def replace(match):
            variable = match.group(1)
            return f"dataframe['{variable}']"

        # Use re.sub with the defined function to replace the pattern
        replaced_expression = re.sub(pattern, replace, expression)
        return replaced_expression

    def custom_columns(self,dataframe):
        columns = dataframe.columns.tolist()
        for column in columns:
            if '=' in column:
                formula = self.replace_variables(column.split('=')[-1])
                try:
                    dataframe[column] = eval(formula)
                except Exception:
                    pass
                dataframe[column] = dataframe[column].fillna(0)
                #dataframe[column.split('=')[0]] = eval(formula)
                #dataframe.drop(columns= column, inplace=True)
        return dataframe

    def transform_columns(self, file: File):
        if len(file.file_separator) == 1:
            dataframe = pd.read_csv(self.raw_file_path + file.file_name, sep=file.file_separator,engine='python')
        else:
            dataframe = pd.read_csv(self.raw_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')
        dataframe = dataframe.applymap(lambda x: x.strip() if isinstance(x, str) else x).drop_duplicates()
        dataframe = dataframe.applymap(self.remove_commas_and_convert)
        dataframe = dataframe.applymap(self.remove_symbols_and_convert)
        #custom column for formulation done here
        dataframe = self.custom_columns(dataframe)
        self.write_to_file(dataframe.rename(columns=file.column_mapping), file)

    def transform_columns_(self, file: File):
        if len(file.file_separator) == 1:
            dataframe = pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator,engine='python')
        else:
            dataframe = pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')
        self.write_to_file(dataframe.rename(columns=file.column_mapping), file)

    def remove_string(self, file: File):
        if len(file.file_separator) == 1:
            dataframe = pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator,engine='python')
        else:
            dataframe = pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')
        dataframe = dataframe.replace(['\$', '%'], '', regex=True)
        self.write_to_file(dataframe, file)


    def remove_symbols_and_convert(self, value):
        if isinstance(value, str):
            try:
                # Replace '$' or '%' and remove commas
                modified_value = value.replace('$', '').replace('%', '').replace(',', '')
                numeric_value = float(modified_value)
                
                # Check if the value after modification can be converted to an integer or float
                if numeric_value.is_integer():
                    return int(numeric_value)
                return numeric_value
            except ValueError:
                pass
        return value
    
    def get_transformed_dataframe(self, file: File):
        if len(file.file_separator) == 1:
            return pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator,engine='python')
        else:
            return pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')

    def write_to_file(self, dataframe: DataFrame, file):
        if len(file.file_separator) == 1:
            dataframe.to_csv(self.transform_file_path + file.file_name, sep=file.file_separator, index=False, header=True)
        elif file.file_separator == '\t':
            dataframe.to_csv(self.transform_file_path + file.file_name, sep='\t', index=False, header=True)
        else:
            dataframe.to_csv(self.transform_file_path + file.file_name, sep='\t', index=False, header=True)


    def apply_transformations(self, file: File, transformations: dict):
        
        if len(file.file_separator) == 1:
            dataframe = pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')
        else:
            dataframe = df = pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')
        for transformation in transformations:
            try:
                dataframe = self.transformers[transformation["type"]].transform(dataframe=dataframe,
                                                                transformation_config=transformation)
            except Exception as e:
                return exception_handler.handle_exception(e)
        if type(dataframe)!= tuple:
            self.write_to_file(dataframe, file)
        return dataframe
    


    def find_date(self, file):
        Date_count = 0
        if len(file.file_separator) == 1:
            dataframe = pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')
        else:
            dataframe = pd.read_csv(self.transform_file_path + file.file_name, sep=file.file_separator, on_bad_lines='skip',engine='python')
        date_pattern = re.compile(r'(?i)\bDate\b')
        matching_column = next((col for col in dataframe.columns if date_pattern.search(col)), None)
        if matching_column:
            # Define the valid date patterns
            patterns = [
                r'^\d{4}[-/]\d{1,2}[-/]\d{1,2}$',  # Matches YYYY-M-D, YYYY-MM-DD, YYYY/M/D, YYYY/MM/DD
                r'^\d{1,2}[-/]\d{1,2}[-/]\d{4}$',  # Matches M-D-YYYY, MM-DD-YYYY, M/D/YYYY, MM/DD/YYYY
                r'^\d{1,2}(?:st|nd|rd|th) [A-Z][a-z]{2} \d{4}$',  # Matches 1st Feb 2022, 22nd Dec 2023, etc.
                r'^\d{4} [A-Z][a-z]{2} \d{1,2}$'  # Matches YYYY Mon D, e.g., 2022 Feb 22
            ]
            size = len(dataframe)
            # Create a boolean mask based on whether any pattern exists in the 'DateColumn'
            mask = dataframe[matching_column].str.match('|'.join(patterns))
            # Check if any row matches any pattern
            if mask.any():
                dataframe[matching_column] = pd.to_datetime(dataframe[matching_column], errors='coerce').dt.strftime('%Y-%m-%d')
                invalid_date_mask = dataframe[matching_column].isna()
                # Extract rows with invalid date values
                invalid_date_data_count = invalid_date_mask.sum()
                if invalid_date_data_count/size >=  int(Configuration.DATE_VALIDATION_LIMIT):
                    return False
                dataframe = dataframe[~invalid_date_mask]
            else:
                return False
            dataframe.rename(columns={matching_column:'date'}, inplace=True)
            dataframe.head()
            self.write_to_file(dataframe, file)
            return True
        else:
            return False
        
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
            elif i["type"] == "delete":
                data['data_deletion'] = i["conditions"]
        return data
