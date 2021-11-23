def get_attribute_list(attributes):
    merged_attributes = {}
    for attribute in attributes:
        if attribute['attributes']:
            for i, (key, value_list) in enumerate(attribute['attributes'].items()):
                if key not in merged_attributes:
                    merged_attributes[key] = value_list.copy()
                else:
                    for value in value_list:
                        if value not in merged_attributes[key]:
                            merged_attributes[key].append(value)

    return merged_attributes
