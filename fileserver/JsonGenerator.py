import json

def GenerateJsonTable(header, data):
    table = [dict(zip(header, map(str, row))) for row in data]
    return json.dumps(table)