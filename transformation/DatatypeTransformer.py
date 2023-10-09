from pandas import DataFrame
import pandas as pd
from transformation.Transformer import Transformer


class DtypesTransformer(Transformer):

    def name(self):
        return "change_dtypes"

    def transform(self, dataframe: DataFrame, transformation_config: dict):
        current_dtype = dataframe[transformation_config["col"]].dtype
        if (transformation_config["col"]).lower() == 'date':
            pass

        else:
            if current_dtype == 'datetime64[ns]' and transformation_config["dtypes"] == 'object':
                dataframe[transformation_config["col"]] = dataframe[transformation_config["col"]].dt.strftime('%Y-%m-%d')
            elif current_dtype == 'object' and transformation_config["dtypes"] == 'datetime64[ns]':
                dataframe[transformation_config["col"]] = pd.to_datetime(dataframe[transformation_config["col"]], errors='coerce')

            elif current_dtype == 'int64' and transformation_config["dtypes"]  == 'datetime64[ns]':
                dataframe[transformation_config["col"]] = pd.to_datetime(dataframe[transformation_config["col"]], unit='D', origin='unix')
            elif current_dtype == 'datetime64[ns]' and transformation_config["dtypes"]  == 'int64':
                dataframe[transformation_config["col"]] = (dataframe[transformation_config["col"]]- pd.Timestamp("1970-01-01")).dt.days
            elif current_dtype == 'object' and transformation_config["dtypes"] == 'int64':
                print('Converting object to int')
                dataframe[transformation_config["col"]].fillna(0, inplace=True)
                dataframe[transformation_config["col"]] = pd.to_numeric(dataframe[transformation_config["col"]], errors='coerce', downcast='integer')

            else:
                dataframe[transformation_config["col"]].fillna(0, inplace=True)
                dataframe[transformation_config["col"]].astype(transformation_config["dtypes"])
        return dataframe