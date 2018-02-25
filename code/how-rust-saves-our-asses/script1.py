import sys
import json
data = json.load(sys.stdin)
for person in data["people"]:
    print """
{name} lives in {city}, {state}.
They work for {workName} in {workCity}, {workState}.
    """.format(
    	name=person["name"],
    	city=person["address"]["addressLocality"],
    	state=person["address"]["addressRegion"],
        workName=person["worksFor"]["name"],
    	workCity=person["worksFor"]["address"]["addressLocality"],
    	workState=person["worksFor"]["address"]["addressRegion"],
    )