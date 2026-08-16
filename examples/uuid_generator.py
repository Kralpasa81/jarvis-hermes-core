import uuid
"""
Simple UUID generator utility
Generates various types of UUIDs for different use cases
"""

def generate_uuid(uuid_type='default'):
    """
    Generate UUID based on type
    
    Args:
        uuid_type (str): Type of UUID to generate
            'default' - Standard UUID4
            'hex' - UUID4 in hex format
            'int' - UUID4 as integer
            'urn' - UUID4 as URN
    
    Returns:
        str: Generated UUID
    """
    if uuid_type == 'default':
        return str(uuid.uuid4())
    elif uuid_type == 'hex':
        return uuid.uuid4().hex
    elif uuid_type == 'int':
        return uuid.uuid4().int
    elif uuid_type == 'urn':
        return uuid.uuid4().urn
    else:
        raise ValueError(f"Invalid UUID type: {uuid_type}")


if __name__ == "__main__":
    # Basic usage examples
    print("Default UUID:", generate_uuid())
    print("Hex UUID:", generate_uuid('hex'))
    print("Integer UUID:", generate_uuid('int'))
    print("URN UUID:", generate_uuid('urn'))
