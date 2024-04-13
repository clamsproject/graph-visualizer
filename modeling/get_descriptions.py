import requests
import xml.etree.ElementTree as ET

# Make the API request
response = requests.get("https://americanarchive.org/api.xml?fl=id,title,xml&rows=100&start=1")

# Check if the request was successful
if response.status_code == 200:
    # Parse the XML data
    root = ET.fromstring(response.text)

    docs = root.find('response').find('docs')

    all_descriptions = {}

    for doc in docs:
        id = doc.find('id').text
        xml_str = doc.find('xml')
        xml = ET.fromstring(xml_str.text)
        descriptions = xml.findall('{http://www.pbcore.org/PBCore/PBCoreNamespace.html}pbcoreDescription')
        longest_description = max([" ".join(d.text.split()) for d in descriptions], key=len)
        print(longest_description)
        if longest_description and "No other information" not in longest_description \
                               and "No information" not in longest_description \
                               and "No description" not in longest_description:
            all_descriptions[id] = longest_description
    
    print(all_descriptions)

else:
    print("Failed to fetch data from the API")