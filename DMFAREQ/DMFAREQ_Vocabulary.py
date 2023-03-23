import csv
import re

import sys
sys.path.append("../")
from helper import *

outfile = open("DMFAREQ_Vocabulary.ttl", "w", encoding="utf-8")

# HEADER
# TODO maybe change ontology namespace
outfile.write("""
@prefix : <http://kg.socialsecurity.be/ont/dmfa#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dc: <http://purl.org/dc/terms/#> .
@base <http://kg.socialsecurity.be/ont/dmfa#> .

<http://kg.socialsecurity.be/ont/dmfa#> rdf:type owl:Ontology .
""")

domainDict = {}

# Classes - Entities
# TODO think of presence, card,...
rootBFxml = xmlRoot('VersCplt_BFDMFAREQ20223FR.xml', encoding="iso-8859-1")
for bf in rootBFxml:

    className = bf.find("XmlLabel").text
    identifier = bf.find("Code").text
    labelEn = re.sub(r"(\w)([A-Z])", r"\1 \2", className)
    labelFr = bf.find("Nom").text
    commentFr = addTripleQuotes(bf.find("Description").text)
    presenceFr = addTripleQuotes(bf.find("Presence").text)

    strToWrite = ""
    strToWrite = appendIfNotNone(strToWrite, ':{} a owl:Class;', className)
    strToWrite = appendIfNotNone(strToWrite, 'dc:identifier "{}";', identifier)
    strToWrite = appendIfNotNone(strToWrite, 'rdfs:label "{}"@en;', labelEn)
    strToWrite = appendIfNotNone(strToWrite, 'rdfs:label "{}"@fr;', labelFr)
    strToWrite = appendIfNotNone(strToWrite, 'rdfs:comment {}@fr;', commentFr)
    strToWrite = appendIfNotNone(strToWrite, ':presence {}@fr;', presenceFr)

    outfile.write(strToWrite + "\n .")

    attributes = bf.findall("Zones")
    for att in attributes:
        if att.text:
            key = att.text.split(' ', 1)[0]
            if key not in domainDict.keys():
                domainDict[key] = [":" + className]
            else:
                domainDict[key].append(":" + className)


# DatatypeProperties - Attributes

rootZones = xmlRoot('VersCpltDMFAREQ20223FR.xml', "iso-8859-1")
for zone in rootZones:

    DPName = zone.find("LabelXml").text
    identifier = zone.find("Code").text
    labelEn = re.sub(r"(\w)([A-Z])", r"\1 \2", DPName)
    labelFr = zone.find("Title").text
    commentFr = addTripleQuotes(zone.find("Description").text)
    presenceFr = addTripleQuotes(zone.find("Presence").text)
    isDefinedByFr = addTripleQuotes(zone.find("DomaineDeDefinition").text)
    domain = """
            [ a owl:Class ;
                owl:unionOf ({})
            ]
    """.format(" ".join(domainDict[identifier]))
    length = zone.find("Longueur").text
    typeFr = addTripleQuotes(zone.find("Type").text)

    strToWrite = ""
    strToWrite = appendIfNotNone(
        strToWrite, ':{} a owl:DatatypeProperty;', DPName)
    strToWrite = appendIfNotNone(strToWrite, 'dc:identifier "{}";', identifier)
    strToWrite = appendIfNotNone(strToWrite, 'rdfs:label "{}"@en;', labelEn)
    strToWrite = appendIfNotNone(strToWrite, 'rdfs:label "{}"@fr;', labelFr)
    strToWrite = appendIfNotNone(strToWrite, 'rdfs:comment {}@fr;', commentFr)
    strToWrite = appendIfNotNone(strToWrite, ':presence {}@fr;', presenceFr)
    strToWrite = appendIfNotNone(strToWrite, 'rdfs:domain {};', domain)
    strToWrite = appendIfNotNone(
        strToWrite, 'rdfs:isDefinedBy {}@fr;', isDefinedByFr)
    strToWrite = appendIfNotNone(strToWrite, ':length {};', length)
    strToWrite = appendIfNotNone(strToWrite, ':type {}@fr;', typeFr)

    outfile.write(strToWrite + "\n.\n")

# ObjectProperties - Relation
# CSV file should have been generated with DmfA_Relation_Base.py and annotated
relationCSV = open("DMFAREQ_Relation_Base.csv", encoding="utf-8")
relationTable = csv.reader(relationCSV, delimiter=",") # From,To,Domain,Range
next(relationTable, None)

for row in relationTable:

    relationName = "R_" + row[0] + "_" + row[1]
    domain = row[2]
    range = row[3]

    outfile.write("""
    :{} a owl:ObjectProperty;
        rdfs:domain :{};
        rdfs:range :{};
    .
    """.format(relationName, domain, range))

relationCSV.close()

outfile.close()
