from pandas import DataFrame

from transformation.Transformer import Transformer


class RegexTrasformer(Transformer):

    def name(self):
        return "regex"

    def transform(self, dataframe: DataFrame, transformation_config: dict):
        dataframe[transformation_config["col"]] = dataframe[transformation_config["col"]].str.replace(transformation_config["regex"], transformation_config["replace_by"], regex=False)
        return dataframe
