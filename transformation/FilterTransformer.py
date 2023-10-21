from pandas import DataFrame
from transformation.Transformer import Transformer


class FilterTransformer(Transformer):
    def name(self):
        return "filter"

    def transform(self, dataframe: DataFrame, transformation_config: list):
        print(dataframe.columns)
        col = transformation_config["col"]
        operator = transformation_config["operator"]
        value = transformation_config["value"]

        if operator == "between":
            condition = (dataframe[col] <= value[0]) & (dataframe[col] >= value[1])
            dataframe = dataframe.loc[condition]

            
        else:
            if operator == "<":
                dataframe = dataframe.loc[dataframe[col] < value]
            elif operator == ">":
                dataframe = dataframe.loc[dataframe[col] > value]
            elif operator == "=":
                dataframe = dataframe.loc[dataframe[col] == value]
            elif operator == "<=":
                dataframe = dataframe.loc[dataframe[col] <= value]
            elif operator == ">=":
                dataframe = dataframe.loc[dataframe[col] >= value]
            elif operator == "!=":
                dataframe = dataframe.loc[dataframe[col] != value]

        return dataframe
