import json

def generate_dynamic_field_schema(user_request):
    """
    Dynamically generates a fieldSchema based on the user's request.

    Args:
        user_request (dict): A dictionary containing the user's requested fields and their details.

    Returns:
        dict: A dynamically generated fieldSchema.
    """
    field_schema = {
        "fields": {}
    }

    for field_name, field_details in user_request.items():
        field_type = field_details.get("type", "string")
        method = field_details.get("method", "generate")
        description = field_details.get("description", f"Field for {field_name}")

        field_entry = {
            "type": field_type,
            "method": method,
            "description": description
        }

        # Add additional properties for arrays or objects
        if field_type == "array":
            field_entry["items"] = field_details.get("items", {"type": "string"})
        elif field_type == "object":
            field_entry["properties"] = field_details.get("properties", {})

        field_schema["fields"][field_name] = field_entry

    return field_schema

# Example usage
user_request = {
    "CustomField1": {
        "type": "string",
        "method": "generate",
        "description": "A custom string field"
    },
    "CustomArrayField": {
        "type": "array",
        "method": "classify",
        "description": "A custom array field",
        "items": {
            "type": "string"
        }
    }
}

dynamic_schema = generate_dynamic_field_schema(user_request)
print(json.dumps(dynamic_schema, indent=2))