from datetime import datetime

# Cast the data types
def cast_data_types(data, data_types):
    for item in data:
        for key, value in item.items():
            print(key)
            if key in data_types:
                if isinstance(data_types[key], dict):
                    cast_data_types([value], data_types[key])                
                elif isinstance(data_types[key], list):
                    for nested_item in value:
                        cast_data_types([nested_item], data_types[key][0])
                        for nested_key in data_types[key][0].keys():
                            if nested_key not in nested_item:
                                if key not in item:
                                    if value == int:
                                        nested_item[nested_key] = None                                      
                                    else:
                                        nested_item[nested_key] = ""  

                elif data_types[key].__name__ == 'datetime':
                    try:
                        item[key] = str(datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f %Z'))          
                    except:
                        item[key] = str(datetime.strptime(value, '%Y-%m-%d %H:%M:%S'))                                               
                else:
                    data_type = data_types[key]
                    item[key] = data_type(value)  

    return data

# Cast the data types + fill in missing fields
def fill_in_missing_keys(data, data_types):
    data_cast = cast_data_types(data, data_types)
    for item in data_cast:
        for key, value in data_types.items():
            if key not in item.keys():
                if value == int:
                    item[key] = None
                elif isinstance(data_types[key], list):
                    item[key] = []
                    if len(data_types[key]) > 0:
                        for nested_key, nested_value in data_types[key][0].items():
                            data_type_value = nested_value.__name__
                            if data_type_value == 'int':
                                dict_added = {nested_key: None}
                            else:
                                dict_added = {nested_key: ""}
                            item[key].append(dict_added)
    
                elif isinstance(data_types[key], dict):
                    item[key] = {}
                    for nested_key in value:
                        data_type_value = value[nested_key].__name__
                        if data_type_value == 'int':
                            item[key][nested_key] = None
                        else:
                            item[key][nested_key] = ""          
                else:
                    item[key] = ""
        return data_cast