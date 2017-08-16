from lxml import etree

def GenerateXmlTable(header, data):
    table = [dict(zip(header, row)) for row in data]
    root = etree.Element("root")
    for d in table:
        dataElement = etree.Element("element")
        for k in d.keys():
            cellElement = etree.Element(str(k))
            cellElement.text = str(d[k])
            dataElement.append(cellElement)
        root.append(dataElement)
    return etree.tostring(root)