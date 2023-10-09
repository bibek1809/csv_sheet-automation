from pandas import DataFrame

from transformation.Transformer import Transformer


class FillNaTransformer(Transformer):

    def name(self):
        return "fillNa"

    def transform(self, dataframe: DataFrame, transformation_config: dict):
        dataframe[transformation_config["col"]] = dataframe[transformation_config["col"]].fillna(transformation_config["value"], inplace=False)
        return dataframe