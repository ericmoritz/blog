import sys
import json
data = json.load(sys.stdin)
for person in data["people"]:
    address = person.get("address", {})
    works_for = person.get("worksFor", {})
    works_for_address = works_for.get("address", {})

    print """
{name} lives in {city}, {state}.
They work for {workName} in {workCity}, {workState}.
    """.format(
    	name=person.get("name", ""),
        city=address.get("addressLocality", "???"),
        state=address.get("addressRegion", "???"),
    	workName=works_for.get("name", "???"),
        workCity=works_for_address.get("addressLocality", "???"),
    	workState=works_for_address.get("addressRegion", "???")
    )
