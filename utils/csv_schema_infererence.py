from logging import exception
import mmap
import os
import re
import random
import multiprocessing as mp
import datetime as dt
import operator
import json


class DetectType:

    def __init__(self, max_length, sep):
        self.max_length = max_length
        self.sep = sep

    def __get_local_type(self, value):
        try:
            float(value)
        except ValueError:
            return "STRING"

        if float(value).is_integer():
            return "INTEGER"
        else:
            return "FLOAT"

    def __get_date_type(self, value):

        if "T" in value:
            segments = value.split("T")
            try:
                if len(segments) == 2:
                    valid_date = False
                    d_elements = segments[0].split("-")
                    if len(d_elements) == 3 and len(d_elements[0]) in {2, 4} and \
                            len(d_elements[1]) == 2 and len(d_elements[2]) == 2:
                        dt.date(*(int(e) for e in d_elements))
                        valid_date = True
                    t_elements = segments[1].split(":")
                    valid_time = False
                    if len(t_elements) in (2, 3):
                        valid_time = (len(t_elements[0]) == 2 and 0 <= int(t_elements[0]) < 24 and
                                      len(t_elements[1]) and 0 <= int(t_elements[1]) < 60)
                        if len(t_elements) == 3:
                            valid_time = (valid_time and len(t_elements[2]) == 2 and
                                          0 <= int(t_elements[2]) < 60)
                    if valid_time and valid_date:
                        return "TIMESTAMP"

            except ValueError:
                return "STRING"

        elif "-" in value:

            segments = value.split("-")
            try:

                if len(segments) == 3 and len(segments[0]) in {2, 4} and \
                        len(segments[1]) == 2 and len(segments[2]) == 2:
                    dt.date(*(int(e) for e in segments))
                    return "DATE"
            except ValueError:
                return "STRING"
        else:

            try:
                segments = value.split(":")
                if len(segments) in {2, 3}:
                    valid = (len(segments[0]) == 2 and 0 <= int(segments[0]) < 24 and
                             len(segments[1]) and 0 <= int(segments[1]) < 60)
                    if len(segments) == 3:
                        valid = (valid and len(segments[2]) == 2 and
                                 0 <= int(segments[2]) < 60)
                    if valid:
                        return "TIME"
            except ValueError:
                return "STRING"

        return "STRING"

    def __infer_value_type(self, value, index, schema, values_type):

        try:
            if value not in values_type.keys():

                local_type = self.__get_local_type(value)

                if local_type == 'STRING':

                    if value in {"", "na", "NA", "null", "NULL"}:
                        schema[index]["nullable"] = True
                        _type = "STRING"
                    elif value in {"true", "false", "TRUE", "FALSE", "True", "False"}:
                        _type = "BOOLEAN"
                    elif len(value) < 21:
                        _type = self.__get_date_type(value)
                    else:
                        _type = local_type
                else:
                    _type = local_type

                values_type[value] = _type

                if values_type[value] not in schema[index]["types_found"].keys():
                    schema[index]["types_found"][values_type[value]] = {
                        "cnt": 1}
                else:
                    schema[index]["types_found"][values_type[value]]["cnt"] += 1
            else:

                if values_type[value] not in schema[index]["types_found"].keys():
                    schema[index]["types_found"][values_type[value]] = {
                        "cnt": 1}
                else:
                    schema[index]["types_found"][values_type[value]]["cnt"] += 1
        except:
            response = {
                "success": False,
                "code": 400,
                "error": 'Column Header Invalid',
                "message": 'Column Header Invalid contains Symbol',
                "traceback": 'Column Header Invalid contains Symbol',
                "description": 'Column Header Invalid contains Symbol'}
            return json.dumps(response), 412

    def execute(self, records, schema):
        values_type = {}
        for record in records:
            values = record.rstrip().split(self.sep)
            for index, value in enumerate(values):
                self.__infer_value_type(
                    value[0:self.max_length], index, schema, values_type)


class Parallel:

    def __init__(self):
        pass

    def execute(self, records, x, obj, d_schema):
        obj.execute(records, d_schema)
        return d_schema

    def parallel(self, records, obj, d_schema):
        if len(records) <= 1000000:  # Threshold for using parallel processing
            return [self.execute(records, 0, obj, d_schema)]

        cpus = mp.cpu_count()
        chunk_size = len(records) // cpus

        if chunk_size < 1:
            chunk_size = 1

        pool = mp.Pool(processes=cpus)

        results = [pool.apply_async(self.execute, args=(records[x:x + chunk_size], x, obj, d_schema)) for x in
                   range(0, len(records), chunk_size)]

        pool.close()
        pool.join()
        try:
            return [p.get() for p in results]
        except:
            response = {"success": False,
                        "code": 400,
                        "error": 'Size Exceeded',
                        "message": 'Size Exceeded Max limit reached',
                        "traceback": 'Size Exceeded Max limit reached',
                        "description": 'Size Exceeded Max limit reached'}
            return json.dumps(response), 412


class CsvSchemaInference:

    def __init__(self, portion=0.5, max_length=1000, batch_size=250000, acc=0.7, seed=1, header=True, sep=";",
                 conditions={}):
        self.portion = portion
        self.seed = seed
        self.header = header
        self.sep = sep
        self.accuracy = acc
        self.__schema = {}
        self.max_length = max_length
        self.data_types = {"STRING", "INTEGER", "FLOAT",
                           "DATETIME", "DATE", "TIME", "TIMESTAMP", "BOOLEAN"}
        self.batch_size = batch_size

        if isinstance(conditions, dict):

            if conditions:
                for k, v in conditions.items():
                    if k not in self.data_types or v not in self.data_types:
                        raise ValueError(
                            'Keys and values in conditions must be valid data types')

        self.conditions = conditions

    def __set_header(self, header):
        if len(self.sep) == 1:
            header = header.rstrip().split(self.sep)
        else:
            pattern = re.escape(self.sep) + r'|\s+'
            header = re.split(pattern, header.strip())

        for i in range(0, len(header)):
            self.__schema[i] = {
                "_name": header[i].replace('"', ''),
                "types_found": {
                },
                "nullable": False,
                "type": ""
            }

    def __estimate_count(self, filename, reader):
        buffer = reader.read(1 << 13)
        file_size = os.path.getsize(filename)
        return file_size // (len(buffer) // buffer.count(b'\n'))

    def __merge_schemas(self, schemas):

        for c_inx in self.__schema:

            for s_inx in range(0, len(schemas)):

                _v = schemas[s_inx][c_inx]

                if _v['nullable']:
                    self.__schema[c_inx]['nullable'] = True

                for k in _v['types_found']:

                    if k not in self.__schema[c_inx]['types_found'].keys():

                        self.__schema[c_inx]['types_found'][k] = {
                            "cnt": _v['types_found'][k]['cnt']
                        }
                    else:
                        self.__schema[c_inx]['types_found'][k]['cnt'] += _v['types_found'][k]['cnt']

    def check_condition(self, _types, acc):

        try:
            _type = max({k: v for k, v in _types.items() if v >= (acc * 100)}.items(),
                        key=operator.itemgetter(1))[0]

            if _type in self.conditions:
                if self.conditions[_type] in _types:
                    _type = self.conditions[_type]

        except ValueError:

            if "STRING" in _types or len(_types) > 2:
                _type = "STRING"

            else:
                if {"INTEGER", "FLOAT"}.issubset(_types):
                    _type = "FLOAT"
                else:
                    _type = "STRING"

        return _type

    def __approximate_types(self, acc=0.5):

        result = {}
        for c in self.__schema:
            _types = {}
            t = 0
            for v in self.__schema[c]['types_found']:
                t += self.__schema[c]['types_found'][v]['cnt']
                if v not in _types.keys():
                    _types[v] = self.__schema[c]['types_found'][v]['cnt']
                else:
                    _types[v] += self.__schema[c]['types_found'][v]['cnt']

            for ft in _types:
                _types[ft] = (_types[ft] * 100) / t

            _type = self.check_condition(_types, acc)

            self.__schema[c]['type'] = _type
            if self.find_higher_percentage_type(_types) is not None:
                _type = self.find_higher_percentage_type(_types)

            result[c] = {
                "name": self.__schema[c]['_name'],
                "type": _type,
                "types_found": _types,
                "total": t,
                "nullable": self.__schema[c]['nullable']
            }

        return result

    def pretty(self, d, ind=0):

        for k, v in d.items():
            print('\t' * ind + str(k))
            if isinstance(v, dict):
                self.pretty(v, ind + 1)
            else:
                print('\t' * (ind + 1) + str(v))

    def get_schema_columns(self, columns={}):

        result = {}

        for c in self.__schema:
            if self.__schema[c]["_name"] in columns:
                result[c] = {
                    "_name": self.__schema[c]["_name"],
                    "types_found": self.__schema[c]["types_found"],
                    "nullable": self.__schema[c]["nullable"],
                    "type": self.__schema[c]["type"]
                }

        return result

    def explore_schema_column(self, column):

        result = {}

        for c in self.__schema:

            if column == self.__schema[c]['_name']:

                _types = {}
                t = 0
                for v in self.__schema[c]['types_found']:
                    t += self.__schema[c]['types_found'][v]['cnt']

                    if v not in _types.keys():
                        _types[v] = self.__schema[c]['types_found'][v]['cnt']
                    else:
                        _types[v] += self.__schema[c]['types_found'][v]['cnt']

                for ft in _types:
                    _types[ft] = (_types[ft] * 100) / t

                result[c] = {
                    "name": self.__schema[c]['_name'],
                    "types_found": _types,
                    "nullable": self.__schema[c]['nullable']
                }

                break

        return result

    def find_higher_percentage_type(self, types):
        total = sum(types.values())
        if total == 0:
            return None
        percentage = {key: value / total for key, value in types.items()}
        max_key = max(percentage, key=percentage.get)

        return max_key

    def run_inference(self, filename):

        with open(filename, mode="r", encoding="ISO-8859-1") as file_obj:
            with mmap.mmap(file_obj.fileno(), length=0, access=mmap.ACCESS_READ) as map_file:

                less_header = 0

                if self.header:
                    less_header = 1

                no_lines = self.__estimate_count(
                    filename, map_file) - less_header
                portion = int(no_lines * self.portion)
                map_file.seek(0)

                if self.header:
                    self.__set_header(map_file.readline().decode("ISO-8859-1"))

                lines = []
                schemas = []
                batch_count = 0

                dtype = DetectType(self.max_length, self.sep)

                while batch_count < portion:

                    batch_count += 1
                    lines.append(map_file.readline().decode("ISO-8859-1"))

                    if batch_count % self.batch_size == 0:

                        prl = Parallel()
                        schemas_result = prl.parallel(
                            records=lines, obj=dtype, d_schema=self.__schema)

                        for schema in schemas_result:
                            schemas.append(schema)

                        lines = []

                if len(lines) > 0:

                    prl = Parallel()
                    schemas_result = prl.parallel(
                        records=lines, obj=dtype, d_schema=self.__schema)

                    for schema in schemas_result:
                        schemas.append(schema)

                    del lines
                    del batch_count

                # Joining schemas results
                self.__merge_schemas(schemas)

        # Approximate data types
        return self.__approximate_types(acc=self.accuracy)


class SchemaInference:
    DATATYPE_RANK = {
        "INTEGER": 1,
        "FLOAT": 2,
        "DOUBLE": 3,
        "STRING": 4,
        "DATE": 5
    }

    def __datatype_merger(self, datatype_1, datatype_2):
        return datatype_1 if SchemaInference.DATATYPE_RANK[datatype_1] >= \
                             SchemaInference.DATATYPE_RANK[datatype_2] else datatype_2

    def __merge_schema(self, schema_1, schema_2):
        if schema_1 is None:
            return schema_2
        else:
            types_found = {}
            for k, v in schema_1['types_found'].items():
                types_found[k] = v * schema_1['total']

            for k, v in schema_2['types_found'].items():
                types_found[k] = v * schema_2['total'] + \
                    types_found[k] if k in types_found else 0

            total_records = schema_1['total'] + schema_2['total']

            for k, v in types_found.items():
                types_found[k] = v / total_records

            return {
                'name': schema_1['name'],
                'type': self.__datatype_merger(schema_1['type'], schema_2['type']),
                'nullable': schema_1['nullable'] and schema_2['nullable'],
                'total': total_records,
                'types_found': types_found
            }

    def merge_schemas(self, schemas_1, schemas_2):
        merged_schemas = {}
        for schema in schemas_1:
            merged_schemas[schema['name']] = schema

        for schema in schemas_2:
            merged_schema = self.__merge_schema(
                merged_schemas[schema['name']] if schema['name'] in merged_schemas else None, schema)
            merged_schemas[merged_schema['name']] = merged_schema

        return merged_schemas
