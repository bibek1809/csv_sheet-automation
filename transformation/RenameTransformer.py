from pandas import DataFrame

from transformation.Transformer import Transformer


class RenameTransformer(Transformer):

    def name(self):
        return "rename"

    def transform(self, dataframe: DataFrame, transformation_config: dict):
        return dataframe.rename(columns={transformation_config["col"]: transformation_config["new_col"]}, inplace=False)
