# Validate students.xml against students.xsd   (pip install lxml)
from lxml import etree

schema = etree.XMLSchema(etree.parse("students.xsd"))
doc = etree.parse("students.xml")

if schema.validate(doc):
    print("XML is VALID according to the XSD")
else:
    print("XML is INVALID:")
    for error in schema.error_log:
        print(" -", error.message)
