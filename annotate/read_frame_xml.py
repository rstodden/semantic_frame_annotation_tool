import xml.etree.ElementTree
import os

for filename in sorted(os.listdir("../fndata-1.7/frame")[:10]):
	if filename.endswith('xml'):
		root = xml.etree.ElementTree.parse("../fndata-1.7/frame/"+filename).getroot()
		print(root.attrib["name"])
		for child in root:
			if child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib["coreType"] == 'Core':
				#print(child.attrib["coreType"], child.attrib["name"])#, child.attrib["definition"])
				for childchild in child:
					if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
						print(child.attrib["name"], childchild.text)
						pass
				# add core elements to database table frame_types with id, name, description. delete tags of description before?
			elif child.tag == "{http://framenet.icsi.berkeley.edu}lexUnit" and child.attrib["POS"] == 'V':
				#print(child.attrib["name"])
				for childchild in child:
					if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
						print(child.attrib["name"])#, childchild.text)
				# add core elements to database table frame_types with id, name, description
			# pick the database description child