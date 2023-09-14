from pandas import DataFrame

from transformation.Transformer import Transformer


class AddcolTransformer(Transformer):

    def name(self):
        return "addcol"

    def transform(self, dataframe: DataFrame, transformation_config: dict):
        """
            Add a new column to a DataFrame based on the specified transformation_config.

            Parameters:
            - dataframe: The DataFrame to which the new column will be added.
            - transformation_config: A dictionary containing the following keys:
                - 'COL': The name of the new column.
                - 'OPERATOR': The operation to perform ('ADD', 'SUBTRACT', 'DIVIDE', 'LEFT', 'REPLACE').
                - 'OPERATE_COLUMNS': A list containing 1 or 2 column names from the DataFrame.
                - 'replacer' (optional): A dictionary for replacing specific values.
                - 'consttotake' (optional): Integer specifying how many characters to take from a column when 'OPERATOR' is 'LEFT'.
                - 'take_all' (optional): Boolean, if True, takes the entire column when 'OPERATOR' is 'LEFT'.

            Returns:
            - The modified DataFrame with the new column.
            """
        if 'COL' not in transformation_config or 'OPERATOR' not in transformation_config or 'OPERATE_COLUMNS' not in transformation_config:
            raise ValueError("Transformation dictionary must contain 'COL', 'OPERATOR', and 'OPERATE_COLUMNS' keys.")

        new_column_name = transformation_config['COL']
        operator = transformation_config['OPERATOR']
        operate_columns = transformation_config['OPERATE_COLUMNS']

        if new_column_name in dataframe.columns:
            raise ValueError(f"Column '{new_column_name}' already exists in the DataFrame.")

        if operator == 'ADD':
            if len(operate_columns) != 2:
                raise ValueError("For 'ADD' operation, 'OPERATE_COLUMNS' must contain exactly 2 column names.")
            dataframe[new_column_name] = dataframe[operate_columns[0]] + dataframe[operate_columns[1]]
        elif operator == 'SUBTRACT':
            if len(operate_columns) != 2:
                raise ValueError("For 'SUBTRACT' operation, 'OPERATE_COLUMNS' must contain exactly 2 column names.")
            dataframe[new_column_name] = dataframe[operate_columns[0]] - dataframe[operate_columns[1]]
        elif operator == 'DIVIDE':
            if len(operate_columns) != 2:
                raise ValueError("For 'DIVIDE' operation, 'OPERATE_COLUMNS' must contain exactly 2 column names.")
            dataframe[new_column_name] = dataframe[operate_columns[0]] / dataframe[operate_columns[1]]
        elif operator == 'LEFT':
            if len(operate_columns) != 1:
                raise ValueError("For 'LEFT' operation, 'OPERATE_COLUMNS' must contain exactly 1 column name.")
            
            if 'consttotake' in transformation_config and 'take_all' in transformation_config:
                raise ValueError("Both 'consttotake' and 'take_all' cannot be specified together.")
            
            if 'consttotake' in transformation_config:
                consttotake = transformation_config['consttotake']
                dataframe[new_column_name] = dataframe[operate_columns[0]].str[:consttotake]
            elif 'take_all' in transformation_config and transformation_config['take_all']:
                dataframe[new_column_name] = dataframe[operate_columns[0]]
            else:
                raise ValueError("Either 'consttotake' or 'take_all' must be specified for 'LEFT' operation.")
        elif operator == 'REPLACE':
            if len(operate_columns) != 1 or 'replacer' not in transformation_config:
                raise ValueError("For 'REPLACE' operation, 'OPERATE_COLUMNS' must contain exactly 1 column name, and 'replacer' must be specified.")
            replacer = transformation_config['replacer']
            for key, value in replacer.items():
                dataframe[new_column_name] = dataframe[operate_columns[0]].str.replace(key, value)
        else:
            raise ValueError(f"Unsupported operator: '{operator}'")

        return dataframe






