def GenerateCsvWithHeader(header, data):
    table = []
    table.append(header)
    for row in data:
        table.append(row)
    outputTable = "\n".join("; ".join('"{}"'.format(str(ceil)) \
        for ceil in line) for line in table)
    return outputTable

def GenerateCsvString(iterableObj):
    return "; ".join(map(str, iterableObj))