import json
from google.cloud import bigquery


def parse_json_schema(json_schema):

    schema_fields = []
    try:
        json_schema_parse = json_schema['items']['properties']
    except:
        json_schema_parse = json_schema

    for field_name, field_info in json_schema_parse.items():
        field_type = field_info['type']
        mode = 'REPEATED' if field_type == 'object' else 'NULLABLE'
        fields = []

        if field_type == 'string':
            bq_type = 'STRING'
            mode = 'NULLABLE'
        elif field_type == 'integer':
            bq_type = 'INTEGER'
            mode = 'NULLABLE'
        elif field_type == 'number':
            bq_type = 'FLOAT'
            mode = 'NULLABLE'
        elif field_type == 'boolean':
            bq_type = 'BOOLEAN'
            mode = 'NULLABLE'
        elif field_type == 'object':
            nested_schema = field_info.get('properties', {})
            nested_schema_fields = parse_json_schema(nested_schema)
            bq_type = 'RECORD'
            mode = 'NULLABLE'
            fields = nested_schema_fields
        elif field_type == 'array':
            try:
                items_type = field_info['items']['type']
                if items_type == 'object':
                    nested_schema = field_info['items']['properties']
                    nested_schema_fields = parse_json_schema(nested_schema)
                    bq_type = 'RECORD'
                    mode = 'REPEATED'
                    fields = nested_schema_fields
                else:
                    bq_type = items_type
                    mode = 'REPEATED'
            except:
                bq_type = 'STRING'
                mode = 'REPEATED'

        else:
            raise ValueError(f"Unsupported field type: {field_type}")

        if fields == '':
            schema_field = bigquery.SchemaField(name=field_name,
                                                field_type=bq_type,
                                                mode=mode)
        else:
            schema_field = bigquery.SchemaField(name=field_name,
                                                field_type=bq_type,
                                                mode=mode,
                                                fields=fields)

        schema_fields.append(schema_field)
    return schema_fields


def parse_json_schema_from_file(file_path):

    with open(file_path, 'r') as file:
        json_schema = json.load(file)
    return parse_json_schema(json_schema)


# parsed_schema = parse_json_schema_from_file(your_file')
# print(parsed_schema)
#  Define the job configuration
# job_config = bigquery.LoadJobConfig(
#     schema=parsed_schema,
#     skip_leading_rows=1,
#     source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
# )
