from pandas import DataFrame

from transformation.Transformer import Transformer


class DropcolTransformer(Transformer):

    def name(self):
        return "drop_columns"

    def transform(self, dataframe: DataFrame, transformation_config: dict):
        """Parameters:
        - dataframe: The DataFrame to which the new column will be added.
        - transformation_config: A dictionary containing the following keys:
            - 'COL': The name of the column to be drop.
        """
        return dataframe.drop(columns=transformation_config["col"],inplace=True)
