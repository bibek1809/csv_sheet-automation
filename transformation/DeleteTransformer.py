from pandas import DataFrame
from transformation.Transformer import Transformer


class DeleteTransformer(Transformer):
    def name(self):
        return "delete"

    def transform(self, dataframe: DataFrame, transformation_config: dict):
        conditions = transformation_config['conditions']
        condition = None
        for col, value in conditions.items():
            col_condition = (dataframe[col] == value)
            if condition is None:
                condition = col_condition
            else:
                condition = condition & col_condition
        if condition is not None:
            dataframe = dataframe.loc[~condition]

        return dataframe
