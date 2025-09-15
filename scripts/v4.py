import os
import re
import argparse

def parse_js_file(js_file_path):
    """Parse MongoDB queries from a .js file."""
    if not os.path.exists(js_file_path):
        raise FileNotFoundError(f"JS file not found: {js_file_path}")
    
    with open(js_file_path, "r", encoding="utf-8") as file:
        content = file.read()
        print(f"DEBUG: JS file content ({len(content)} characters)")
        return content

def extract_context_from_content(content):
    """Extract context from the top of the JS file."""
    lines = content.split('\n')[:10]
    first_lines = '\n'.join(lines)
    
    context_patterns = [
        r'//\s*@?context\s*:?\s*([a-zA-Z0-9_]+)',
        r'/\*\s*@?context\s*:?\s*([a-zA-Z0-9_]+)\s*\*/',
        r'//\s*@?Context\s*:?\s*([a-zA-Z0-9_]+)',
        r'/\*\s*@?Context\s*:?\s*([a-zA-Z0-9_]+)\s*\*/',
        r'//\s*DATABASE\s*:?\s*([a-zA-Z0-9_]+)',
        r'/\*\s*DATABASE\s*:?\s*([a-zA-Z0-9_]+)\s*\*/',
    ]
    
    for pattern in context_patterns:
        match = re.search(pattern, first_lines, re.IGNORECASE)
        if match:
            context = match.group(1)
            print(f"DEBUG: Found context: '{context}'")
            return context
    
    print("DEBUG: No context found, using default 'liquibase_test'")
    return "liquibase_test"

def extract_mongodb_operations(content):
    """Extract MongoDB operations from JS content."""
    operations = []
    
    # Remove comments first
    content_no_comments = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
    content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
    
    patterns = {
        'insertMany': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.insertMany\(\s*(\[.*?\])\s*\)',
        'insertOne': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.insertOne\(\s*(\{.*?\})\s*\)',
        'updateOne': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.updateOne\(\s*(\{.*?\})\s*,\s*(\{.*?\})\s*(?:,\s*(\{.*?\}))?\s*\)',
        'updateMany': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.updateMany\(\s*(\{.*?\})\s*,\s*(\{.*?\})\s*(?:,\s*(\{.*?\}))?\s*\)',
        'replaceOne': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.replaceOne\(\s*(\{.*?\})\s*,\s*(\{.*?\})\s*(?:,\s*(\{.*?\}))?\s*\)',
        'deleteOne': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.deleteOne\(\s*(\{.*?\})\s*\)',
        'deleteMany': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.deleteMany\(\s*(\{.*?\})\s*\)',
        'createIndex': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.createIndex\(\s*(\{.*?\})\s*(?:,\s*(\{.*?\}))?\s*\)',
        'dropIndex': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.dropIndex\(\s*(["\'][^"\']*["\']|\{.*?\})\s*\)',
        'createCollection': r'db\.createCollection\(\s*["\']([^"\']+)["\']\s*(?:,\s*(\{.*?\}))?\s*\)',
        'dropCollection': r'db\.(?:getCollection\(["\']([^"\']+)["\']\)|([a-zA-Z_][a-zA-Z0-9_]*))\.drop\(\s*\)',
        'dropCollection_direct': r'db\.dropCollection\s*\(\s*["\']([^"\']+)["\']\s*\)\s*;?',
        'dropCollection_getCollection': r'db\.getCollection\s*\(\s*["\']([^"\']+)["\']\s*\)\s*\.drop\s*\(\s*\)\s*;?',
        'dropCollection_dot': r'db\.([a-zA-Z_][a-zA-Z0-9_]*)\s*\.drop\s*\(\s*\)\s*;?',
    }
    
    for operation_type, pattern in patterns.items():
        for match in re.finditer(pattern, content_no_comments, re.DOTALL):
            groups = match.groups()
            
            operation = {
                'type': operation_type,
                'collection': groups[0] or groups[1] if len(groups) > 1 else groups[0],
                'raw_match': match.group(0)
            }
            
            # Handle different parameter structures
            if operation_type in ['insertMany', 'insertOne']:
                operation['documents'] = groups[2] if len(groups) > 2 else groups[1]
            elif operation_type in ['updateOne', 'updateMany', 'replaceOne']:
                operation['filter'] = groups[2] if len(groups) > 2 else groups[1]
                operation['update'] = groups[3] if len(groups) > 3 else groups[2]
                operation['options'] = groups[4] if len(groups) > 4 and groups[4] else None
            elif operation_type in ['deleteOne', 'deleteMany']:
                operation['filter'] = groups[2] if len(groups) > 2 else groups[1]
            elif operation_type == 'createIndex':
                operation['index_key'] = groups[2] if len(groups) > 2 else groups[1]
                operation['options'] = groups[3] if len(groups) > 3 and groups[3] else None
            elif operation_type == 'dropIndex':
                operation['index_spec'] = groups[2] if len(groups) > 2 else groups[1]
            elif operation_type == 'createCollection':
                operation['options'] = groups[1] if len(groups) > 1 and groups[1] else None
            elif operation_type in ['dropCollection_direct', 'dropCollection_getCollection', 'dropCollection_dot']:
                operation['type'] = 'dropCollection'
                operation['collection'] = groups[0]
            
            operations.append(operation)
    
    print(f"DEBUG: Found {len(operations)} operations")
    return operations

def clean_json_for_xml(json_str):
    """Clean and format JSON for XML inclusion."""
    if not json_str:
        return "{}"
    return json_str.strip()

def extract_date_from_version(version_string):
    """Extract date from version string."""
    match = re.search(r'^(\d{8})_', version_string)
    if match:
        return match.group(1)
    return None

def extract_file_number_from_version(version_string):
    """Extract file number from version string."""
    match = re.search(r'^(\d{8})_(\d+)', version_string)
    if match:
        return int(match.group(2))
    return 1

def generate_liquibase_xml(version, operations, author_name, context):
    """Generate Liquibase XML with date-based changeset IDs."""
    
    date_part = extract_date_from_version(version)
    file_number = extract_file_number_from_version(version)
    
    if not date_part:
        base_version_num = re.search(r'(\d+)', version)
        base_version_num = base_version_num.group(1) if base_version_num else "1"
    else:
        base_version_num = f"{date_part}_{file_number}"
    
    xml_lines = []
    xml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_lines.append('<databaseChangeLog')
    xml_lines.append('    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"')
    xml_lines.append('    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
    xml_lines.append('    xmlns:mongodb="http://www.liquibase.org/xml/ns/dbchangelog-ext"')
    xml_lines.append('    xsi:schemaLocation="')
    xml_lines.append('        http://www.liquibase.org/xml/ns/dbchangelog')
    xml_lines.append('        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-4.5.xsd')
    xml_lines.append('        http://www.liquibase.org/xml/ns/dbchangelog-ext')
    xml_lines.append('        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-ext.xsd">')

    if not operations:
        xml_lines.append(f'    <changeSet id="{base_version_num}" author="{author_name}" context="{context}">')
        xml_lines.append('        <!-- No MongoDB operations found in the JS file -->')
        xml_lines.append('    </changeSet>')
    else:
        for i, operation in enumerate(operations):
            op_type = operation['type']
            collection = operation['collection']
            
            if len(operations) == 1:
                changeset_id = base_version_num
            else:
                changeset_id = f"{base_version_num}.{i+1}"
            
            xml_lines.append(f'    <changeSet id="{changeset_id}" author="{author_name}" context="{context}">')
            
            try:
                if op_type == 'createCollection':
                    xml_lines.append(f'        <mongodb:createCollection collectionName="{collection}" />')
                    
                elif op_type == 'createIndex':
                    index_key = clean_json_for_xml(operation['index_key'])
                    index_name = f"{collection}_index_{i+1}"
                    
                    xml_lines.append('        <mongodb:runCommand>')
                    xml_lines.append('            <mongodb:command><![CDATA[')
                    xml_lines.append('            {')
                    xml_lines.append(f'                "createIndexes": "{collection}",')
                    xml_lines.append('                "indexes": [')
                    xml_lines.append('                    {')
                    xml_lines.append(f'                        "key": {index_key},')
                    xml_lines.append(f'                        "name": "{index_name}"')
                    xml_lines.append('                    }')
                    xml_lines.append('                ]')
                    xml_lines.append('            }')
                    xml_lines.append('            ]]></mongodb:command>')
                    xml_lines.append('        </mongodb:runCommand>')
                    
                elif op_type == 'insertOne':
                    doc_content = clean_json_for_xml(operation['documents'])
                    xml_lines.append(f'        <mongodb:insertOne collectionName="{collection}">')
                    xml_lines.append('            <mongodb:document><![CDATA[')
                    xml_lines.append(f'            {doc_content}')
                    xml_lines.append('            ]]></mongodb:document>')
                    xml_lines.append('        </mongodb:insertOne>')
                    
                elif op_type == 'insertMany':
                    docs_content = clean_json_for_xml(operation['documents'])
                    if not docs_content.strip().startswith('['):
                        docs_content = f"[{docs_content}]"
                    
                    xml_lines.append(f'        <mongodb:insertMany collectionName="{collection}">')
                    xml_lines.append('            <mongodb:documents><![CDATA[')
                    xml_lines.append(f'            {docs_content}')
                    xml_lines.append('            ]]></mongodb:documents>')
                    xml_lines.append('        </mongodb:insertMany>')
                    
                elif op_type in ['updateOne', 'updateMany']:
                    filter_json = clean_json_for_xml(operation['filter'])
                    update_json = clean_json_for_xml(operation['update'])
                    multi = "true" if op_type == "updateMany" else "false"
                    
                    xml_lines.append('        <mongodb:runCommand>')
                    xml_lines.append('            <mongodb:command><![CDATA[')
                    xml_lines.append('            {')
                    xml_lines.append(f'                "update": "{collection}",')
                    xml_lines.append('                "updates": [')
                    xml_lines.append('                    {')
                    xml_lines.append(f'                        "q": {filter_json},')
                    xml_lines.append(f'                        "u": {update_json},')
                    xml_lines.append(f'                        "multi": {multi}')
                    xml_lines.append('                    }')
                    xml_lines.append('                ]')
                    xml_lines.append('            }')
                    xml_lines.append('            ]]></mongodb:command>')
                    xml_lines.append('        </mongodb:runCommand>')
                    
                elif op_type == 'replaceOne':
                    filter_json = clean_json_for_xml(operation['filter'])
                    replacement_json = clean_json_for_xml(operation['update'])
                    
                    xml_lines.append('        <mongodb:runCommand>')
                    xml_lines.append('            <mongodb:command><![CDATA[')
                    xml_lines.append('            {')
                    xml_lines.append(f'                "findAndModify": "{collection}",')
                    xml_lines.append(f'                "query": {filter_json},')
                    xml_lines.append(f'                "update": {replacement_json},')
                    xml_lines.append('                "new": true')
                    xml_lines.append('            }')
                    xml_lines.append('            ]]></mongodb:command>')
                    xml_lines.append('        </mongodb:runCommand>')
                    
                elif op_type in ['deleteOne', 'deleteMany']:
                    filter_json = clean_json_for_xml(operation['filter'])
                    limit = 1 if op_type == "deleteOne" else 0
                    
                    xml_lines.append('        <mongodb:runCommand>')
                    xml_lines.append('            <mongodb:command><![CDATA[')
                    xml_lines.append('            {')
                    xml_lines.append(f'                "delete": "{collection}",')
                    xml_lines.append('                "deletes": [')
                    xml_lines.append('                    {')
                    xml_lines.append(f'                        "q": {filter_json},')
                    xml_lines.append(f'                        "limit": {limit}')
                    xml_lines.append('                    }')
                    xml_lines.append('                ]')
                    xml_lines.append('            }')
                    xml_lines.append('            ]]></mongodb:command>')
                    xml_lines.append('        </mongodb:runCommand>')
                    
                elif op_type == 'dropIndex':
                    index_spec = operation['index_spec']
                    if index_spec.startswith('"') or index_spec.startswith("'"):
                        index_name = index_spec.strip('"\'')
                        xml_lines.append(f'        <mongodb:dropIndex collectionName="{collection}" indexName="{index_name}" />')
                    else:
                        xml_lines.append(f'        <mongodb:dropIndex collectionName="{collection}">')
                        xml_lines.append('            <mongodb:keys><![CDATA[')
                        xml_lines.append(f'            {clean_json_for_xml(index_spec)}')
                        xml_lines.append('            ]]></mongodb:keys>')
                        xml_lines.append('        </mongodb:dropIndex>')
                    
                elif op_type == 'dropCollection':
                    xml_lines.append(f'        <mongodb:dropCollection collectionName="{collection}" />')
                    
            except Exception as e:
                xml_lines.append(f'        <!-- Error processing {op_type}: {str(e)} -->')
            
            xml_lines.append('    </changeSet>')

    xml_lines.append('</databaseChangeLog>')
    return '\n'.join(xml_lines)

def write_to_file(xml_content, output_file_path):
    """Write XML content to a file."""
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write(xml_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Liquibase XML from JS file.")
    parser.add_argument("--js_file", required=True, help="Path to the .js file.")
    parser.add_argument("--version", required=True, help="Version for the XML changeset.")
    parser.add_argument("--author", required=True, help="Author for the changeset.")
    parser.add_argument("--repo", required=True, help="GitHub repository.")
    parser.add_argument("--branch", required=True, help="Target branch.")
    parser.add_argument("--token", required=True, help="GitHub token.")
    parser.add_argument("--no-pr", action="store_true", help="Skip PR creation.")
    args = parser.parse_args()

    try:
        print(f"Processing JS file: {args.js_file}")
        content = parse_js_file(args.js_file)
        
        context = extract_context_from_content(content)
        print(f"Using context: '{context}'")
        
        operations = extract_mongodb_operations(content)
        
        xml_content = generate_liquibase_xml(args.version, operations, args.author, context)
        
        # Generate XML file in same directory as JS file
        js_dir = os.path.dirname(args.js_file)
        js_filename = os.path.basename(args.js_file)
        xml_filename = os.path.splitext(js_filename)[0] + '.xml'
        changeset_file_path = os.path.join(js_dir, xml_filename)
        
        write_to_file(xml_content, changeset_file_path)
        print(f"✅ XML file generated: {changeset_file_path}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        exit(1)
