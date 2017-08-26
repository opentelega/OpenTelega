import json

def GenerateJsonTable(header, data):
    table = [dict(zip(header, map(str, row))) for row in data]
    return json.dumps(table)

def DecodeJsonIntoTable(jsonString, header):
    content = []
    decodedJson = json.loads(jsonString)
    for row in decodedJson:
        content.append(tuple(map(lambda x:row[x], header)))
    return content
