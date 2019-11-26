from models import *


def read_sentences(file_sentences):
	sentence_list = list()
	sentence_id = ''
	token_list = list()

	with open(file_sentences, encoding="utf-8") as input_file:
		content = input_file.readlines()
	for line in content:
		if line[0] == '#':
			if sentence_id != '' and len(token_list) != 0:
				# add sentence to database if the full sentence was read
				sentence = Sentence(sentence_id=sentence_id)
				sentence.save()
				for token in token_list:
					sentence.token.add(token)
				sentence.save()
				sentence_list.append(sentence)
			sentence_id = line[1:].strip()
			token_list = list()

		elif line != '\n':
			line = line.strip().split('\t')
			token = Token(position=line[0], word_form=line[1], lemma=line[2], dep_nr=line[6], dep_rel=line[7],
						  sentence_id=sentence_id)
			token.save()
			token_list.append(token)
	print(sentence_list)
	return sentence_list


def read_frames(file_frames, file_sentences):
	sentence_dict = read_sentences(file_sentences)
	frame_dict = dict()
	with open(file_frames, encoding="utf-8") as input_file:
		content = input_file.readlines()
	for nr, line in enumerate(content):
		core_elements_dict = dict()
		line = line.strip().split(' ')
		sentence_identifier = line[0][1:]
		frame = line[2].split('.')
		#frame_dict[sentence_identifier + '_' + line[1]] = {'sentence_id': sentence_id, 'sentence': sentence_dict[sentence_id],
		#										   'position': line[1],
		#										   "frame": frame, 'verb': frame[0], 'f-type': frame[1],
		#										   'core_elements': core_elements_dict}
		frame_object = Frame(id=nr, sentence_id=sentence_identifier, position=line[1], verb_lemma=frame[0], f_type=frame[1],
							 user="test", sentence=Sentence.objects.get(sentence_id__exact=sentence_identifier))
		frame_object.save()
		# add sentence and core elements
		for nr, element in enumerate(line[3:]):
			parts_of_element = element.split('-:-')
			#core_elements_dict[nr] = {'lemma': parts_of_element[0],
			#						  'position': parts_of_element[1],
			#						  'slot_type': parts_of_element[2]}
			core_element = CoreElement(position=parts_of_element[1], word_form=parts_of_element[0], slot_type=parts_of_element[2])
			frame_object.core_elements.add(core_element)

	return frame_dict




