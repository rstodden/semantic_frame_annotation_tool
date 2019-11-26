from django.shortcuts import render, render_to_response, redirect
from django.http import JsonResponse, HttpResponse
from .models import *
from django.db.models import Count, Q
import xml.etree.ElementTree
import os
import re
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import register
from collections import Counter
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
import time, json
import collections
#from easymode.xslt.response import render_to_response

from django.core import serializers

"""
	connection between object models and templates. Each loaded request in the frontend will be redirected from the 
	urls to a function in this file. Each request function has to return a response, which can be a JSON response with 
	data or a template repsonse with optional included data. 
	In each function the objects or database entries can be called and changed, that includes frame models as well as
	session data and user data. 
"""


@register.filter
def get_item(dictionary, key):
	return dictionary.get(key)


@register.filter(name="times")
def times(number):
    return range(1,number)

@register.filter(name="split")
def split(value, key):
    """
        Returns the value turned into a list.
    """
    return value.split(key)

@register.filter
def modulo(num, val):
    return ((num % val) == 0) and num != 0

@register.filter
def add(num, val):
	return num+val

@register.filter
def minus(num, val):
	return num-val

annotation_states = ["assigned frame or read_sentence", "annotate_MWE", "change_frametype", "annotate_core_element", "certainty_and_comment", "overview"]


def signup(request):
	"""
	:param request: frontend request to signup
	:return: signup template if not logged in, otherwise frame list with assiged frames
	"""
	if request.user.is_authenticated:
		# if already registered and logged in, show list of frames
		username = request.user.username
		return render(request, "annotate/frames_list.html",
					  {"skipped_frames": Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=True).order_by("verb_lemma"),
					   "frames_in_progress": Frame.objects.filter(Q(user=username, current_version=True, skipped=False, annotation_state__range=[1,4]) | Q(user=username, current_version=True, skipped=False, annotation_state=4, annotated=False)).order_by("verb_lemma") ,
						"annotated_frames": Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=False, annotation_state=5).order_by("verb_lemma"),
					   "not_annotated_frames": Frame.objects.filter(user=username, annotated=False, current_version=True, annotation_state=0, skipped=False).order_by("verb_lemma"),
														 })
	if request.method == "POST":
		# if data to signup is included in request, register user
		username = request.POST.get("username")
		email = request.POST.get("email")
		password = request.POST.get("password_1")
		password_conf = request.POST.get("password_2")
		if password != password_conf:
			return render(request, "annotate/signup_annotation_tool.html",
						  {"username_error": "Password confirmation unequal password."})
		# print(username, password, email)
		if username in User.objects.values_list("username", flat=True):
			return render(request, "annotate/signup_annotation_tool.html", {"username_error": "choose another username, already in use"})
		new_user = User.objects.create_user(username=username, email=email, password=password)
		#for frame in Frame.objects.filter(annotated=False, current_version=True, user="admin", used_time=0, verb_lemma="place").order_by("verb_lemma")[:10]:
		#	frame = copy_frame(frame, user=username, annotation_state=frame.annotation_state, description="signing up")
		#	#frame.user = new_user.username
		#	frame.save(update_fields=["user"])
		new_user.save()
		user = authenticate(username=new_user.username, password=password)
		login(request, user)
		return redirect("frames_list")
		#return render(request, "annotate/frames_list.html", {"annotated_frames": Frame.objects.filter(user=username, annotated=True, current_version=True).order_by("verb_lemma"),
		#												 "not_annotated_frames": Frame.objects.filter(user=username, annotated=False, current_version=True).order_by("verb_lemma"),
		#														 })
	# if no data is included in request, show signup form
	return render(request, "annotate/signup_annotation_tool.html")


def home(request):
	# show introduction when the logo was clicked
	return render(request, "annotate/introduction.html")


def info_semantic_role(request):
	return render(request, "annotate/semantic_role_info.html", {"semantic_role_dict": SemanticRoles.objects.all()})




@login_required(login_url="login")
def admin_fuctions(request):
	"""
	:param request: frontend request to show all admin functions
	:return: template with admin fucntions
	"""
	if request.user.is_superuser:
		return render(request, "annotate/admin_functions.html")
	else:
		return render(request, "annotate/introduction.html")

def draw_dependency_tree():
	pass

def store_time_spent(request):
	"""
	saves the spent time for a change of one frame in the related database object.
	:param request: frontend redirection to save the time which was spent to change a core element.
	"""
	frame_id = request.session["frame_nr"]
	username = request.session["username"]
	if request.method == "POST":
		#frame_id = request.session["frame_nr"]
		print("frame id, time", request.session["frame_nr"])
		time_spent = request.POST.get("timeSpent")
		frame = Frame.objects.get(id=frame_id, user=username)
		frame.used_time += (time.time() - request.session["time_spent"])
		frame.time_spent += int(time_spent)
		frame.save(update_fields=["used_time", "time_spent"])
		print("time saved", frame_id, time_spent)
	return JsonResponse({"state":"success"})


def save_comments(request):
	"""
	:param request: frontend request to leave a comment or save a comment.
	:return:
	"""
	if request.method == "POST":
		text = request.POST.get("comment_text")
		new_comment = Comment(text=text)
		if request.user.is_authenticated:
			username = request.user.username
			new_comment.user = username
		new_comment.save()
		return redirect("home")
	return render(request, "annotate/comment.html")


def display_video(request):
	video_url = settings.MEDIA_URL + "video_tutorial.mp4"
	return render(request, "annotate/introduction.html", {"video_url": video_url})


# def handler404(request):
#     return render(request, "annotate/introduction.html", status=404)

# def handler500(request):
#     return render(request, "annotate/introduction.html", status=500)



@login_required(login_url="login")
def test(request):
	if request.user.is_superuser:
		with open("annotate/templates/test/test.txt", encoding="utf-8") as f:
			content_as_string = f.read()
		return render(request, "test/test.txt")
	else:
		return render(request, "annotate/introduction.html")



##################
### annotation ###
##################
def sort_dict_by_key(input_dict):
  return collections.OrderedDict({k:v for k,v in sorted(input_dict.items())})



def get_frame(frame_sentence_id, frame_position, logged_in_user, record_user, superuser="bqz", copy=False):
	"""
	recursive function to get a requested frame. If the frame is not available it will be copied from a super user
	:param frame_sentence_id: sentence id of record
	:param frame_position: position of verb of record
	:param logged_in_user: user which is logged in and for which a record is requested.
	:param record_user: user from which the data will be requested or copied if available
	:param superuser: user from which the requested data will be copied if available
	:param copy: boolean, if the frame should be copied
	:return: requested (copied) frame if available otherwise None
	"""
	frame = Frame.objects.filter(sentence_id=frame_sentence_id, position__startswith=frame_position,
								 user=record_user, current_version=True)
	if len(frame) == 1 and not copy:
		return frame[0]
	elif len(frame) == 1 and copy:
		frame = copy_frame(frame[0], user=logged_in_user, annotation_state=frame[0].annotation_state,
						   description="copied from " + superuser)
		frame.save(update_fields=["user"])
		return frame
	elif len(frame) == 0 and logged_in_user != superuser and not copy:
		frame = get_frame(frame_sentence_id, frame_position, logged_in_user, superuser, superuser, copy=True)
		return frame
	else:
		return None

def go_direction(request, direction):
	username = request.user.username
	annotation_state = int(request.POST.get("annotation_state"))
	f_type = request.POST.get("f_type")
	frame_id = request.session["frame_nr"]
	frame = Frame.objects.get(user=username, id=frame_id, current_version=True)
	if annotation_state == 0:
		description = "go " + direction + " from read sentence"
	elif annotation_state == 1:
		description = "go " + direction + " from MWE"
	elif annotation_state == 2:
		description = "go " + direction + " from frame type"
		if frame.f_type != f_type and direction == "forward":
			return JsonResponse({"error": "The frame type was not correctly saved. Please select it again."})
	elif annotation_state == 3:
		description = "go" + direction + "from core elements"
	elif annotation_state == 4:
		description = "go " + direction + " from certainty"
	else:
		description = "go "+ direction + "!"
	if direction == "forward":
		annotation_state += 1
	else:
		annotation_state -= 1
	request.session["annotation_state"] = annotation_state
	time_between_steps = time.time() - request.session["time_step"]
	frame = copy_frame(frame, annotation_state=annotation_state, used_time=time_between_steps, description=description)
	request.session["frame_nr"] = frame.id
	request.session["time_step"] = time.time()
	return JsonResponse({"annotation_state": annotation_state})


def save_mwe(request):
	frame_id = request.session["frame_nr"]
	used_time = time.time() - request.session["time_spent"]
	username = request.user.username
	check_overlapping_mwes = request.POST.get("check_overlapping_mwes")
	frame = Frame.objects.get(user=username, id=frame_id, current_version=True)
	mwe_components = [int(token_id) for token_id in request.POST.getlist("mwe_components[]")]
	request.session["mwe_components"] = mwe_components
	slot_and_mwe = False
	slot_and_mwe_id_dict = dict()
	mwe_and_mwe_overlap_dict = dict()
	identical_mwe = False
	count_identical_components = 0
	verbal_slot = False
	list_slot_tok_ids = list()
	for mwe in frame.mwe.all():
		count_identical_components = 0
		for token in mwe.components.all():
			if token.id in mwe_components:
				count_identical_components += 1
		if count_identical_components == len(mwe_components):
			identical_mwe = True
	if identical_mwe:
		# overlap 1) add mwe and delete slot
		return JsonResponse({"overlapping_mwe": False, "identical_mwe": True})

	for slot in frame.slot_element.all():
		if slot.component_type == "token" and slot.id_of_token in mwe_components:
			token = Token.objects.get(id=slot.id_of_token)
			# overlap 2)
			slot_and_mwe_id_dict[slot.id] = [token.lemma, slot.core_element_type, "token_slot", slot.id]
			list_slot_tok_ids.append(token.id)
		elif slot.component_type == "mwe":
			previous_mwe = MWE.objects.get(id=slot.id_of_mwe)
			previous_mwe_token_ids = previous_mwe.components.all().values_list("id", flat=True)
			for previous_mwe_token_id in previous_mwe_token_ids:
				if previous_mwe_token_id in mwe_components:
					# overlap 3
					slot_and_mwe_id_dict[slot.id] = [str(previous_mwe), slot.core_element_type, "mwe_slot", slot.id, previous_mwe.id]
					list_slot_tok_ids.extend(previous_mwe_token_ids)
	# todo
	if frame.sentence.token.get(position=frame.position).id in mwe_components:
		verbal_slot = True
		#print("error")
	request.session["slot_and_mwe_id_dict"] = slot_and_mwe_id_dict
	print(slot_and_mwe_id_dict)
	if len(slot_and_mwe_id_dict) == 0:
		# overlapping behavior:
		# overlap 0) if mwe overlap no slot and no mwe -> create mwe
		# overlap 1) if mwe overlaps a mwe or more mwes (without slot)-> create all if they are not the same
		#  includes # overlap 4) if mwe overlaps head -> create verbal mwe and verb addition of head. this MWe can"t add as slot
		print("create (more) mwe(s)")
		frame_results = copy_frame(frame, used_time=used_time, new_mwe=mwe_components, annotation_state=request.session["annotation_state"], description="create MWU")
		request.session["frame_nr"] = frame_results[0].id
		request.session["time_spent"] = time.time()
		return JsonResponse({"overlapping_mwe": False, "mwe_id": frame_results[1], "mwe_verb": frame_results[2],
							 "verb_addition": frame_results[0].verb_addition, "identical_mwe": False,
							 "changes": "new mwe created"})
	elif len(slot_and_mwe_id_dict) == 1:
		if verbal_slot:
			#	# overlap 5) if mwe overlaps slot and head -> delete slot & create MWe & extend head
			return JsonResponse(
				{"error": "The multiword unit cannot be created. It contains the head as well as a core element."})
		for key in slot_and_mwe_id_dict.keys():
			# overlap 2) if mwe overlaps a single token slot -> create MWE and extend slot with MWE
			# overlap 3) if mwe overlaps mwe with slot -> extend MWE & extend slot with extend MWE
			#  includes # overlap 4) if mwe overlaps head -> create verbal mwe and verb addition of head. this MWe can"t add as slot
			if slot_and_mwe_id_dict[key][2] == "token_slot":
				frame_results = copy_frame(frame, used_time=used_time, add_mwe_and_edit_slot_id=key, annotation_state=request.session["annotation_state"], new_mwe=mwe_components, overlapped_slot_type="token_slot", description="create MWU and extend slot")
				print("extend slot with new mwe")
				request.session["frame_nr"] = frame_results[0].id
				request.session["time_spent"] = time.time()
				return JsonResponse(
					{"overlapping_mwe": False, "mwe_id": frame_results[1], "mwe_verb": frame_results[2],
					 "verb_addition": frame_results[0].verb_addition, "identical_mwe": False,
					 "extended_slot": key, "changes": "mwe created and slot extended",
					 "new_core_element_id": frame_results[3].id,
					 "slot_type": frame_results[3].core_element_type, "lemma": str(frame_results[4])})
			else:
				frame_results = copy_frame(frame, used_time=used_time, add_mwe_and_edit_slot_id=key, annotation_state=request.session["annotation_state"], new_mwe=mwe_components, overlapped_slot_type="mwe_slot", delete_mwe=slot_and_mwe_id_dict[key][4], description="extend MWU and extend core element")
				print("extend old mwe slot with new mwe")
				request.session["frame_nr"] = frame_results[0].id
				request.session["time_spent"] = time.time()
				return JsonResponse(
					{"overlapping_mwe": False, "mwe_id": frame_results[1],
					 "previous_mwe_id": slot_and_mwe_id_dict[key][4], "mwe_verb": frame_results[2],
					 "verb_addition": frame_results[0].verb_addition, "identical_mwe": False,
					 "extended_slot": key, "changes": "mwe extended and slot extended",
					 "new_core_element_id": frame_results[3].id,
					 "slot_type": frame_results[3].core_element_type, "lemma": str(frame_results[4])})

	elif len(slot_and_mwe_id_dict) > 1:
		# overlap 6) if mwe overlaps more than one slot -> delete all slots and create mwe
		frame_results = copy_frame(frame, used_time=used_time, annotation_state=request.session["annotation_state"], delete_multiple_core_elements=True, list_core_element_ids=slot_and_mwe_id_dict.keys(), new_mwe=mwe_components, description="delete all slots and create MWU")
		print("delete all slots")
		request.session["frame_nr"] = frame_results[0].id
		request.session["time_spent"] = time.time()
		print(list_slot_tok_ids)
		return JsonResponse({"overlapping_mwe": False, "mwe_id": frame_results[1], "mwe_verb": frame_results[2],
							 "verb_addition": frame_results[0].verb_addition,
							 "deleted_slots": list(slot_and_mwe_id_dict.keys()),
							 "identical_mwe": False, "changes": "mwe created and slots deleted",
							 "list_slot_tok_ids": list_slot_tok_ids})
	else:
		print("error")
	return JsonResponse({"": ""})


def delete_mwe(request):
	username = request.user.username
	mwe_id = request.POST.get("mwe_id")
	mwe = MWE.objects.get(id=mwe_id)
	check_overlapping = request.POST.get("check_overlapping")
	frame_id = request.session["frame_nr"]
	used_time = time.time() - request.session["time_spent"]
	frame = Frame.objects.get(user=username, id=frame_id, current_version=True)
	token_ids = [tok.id for tok in mwe.components.all()]

	mwe_components = set()
	for token in mwe.components.all():
		mwe_components.add(token.id)

	# check if tok id is also in another mwe, if yes don"t remove highlighting of this token
	mwe_tok_ids = list()
	for mwe_tok in frame.mwe.all():
		if mwe_tok.id != int(mwe_id):
			for tok in mwe_tok.components.all():
				mwe_tok_ids.append(tok.id)
	new_token_ids = list()
	for tok_id in token_ids:
		if tok_id not in mwe_tok_ids:
			new_token_ids.append(tok_id)

	slot_and_mwe_id_dict = dict()
	for slot in frame.slot_element.all():
		if slot.component_type == "token" and slot.id_of_token in mwe_components:
			token = Token.objects.get(id=slot.id_of_token)
			slot_and_mwe_id_dict[slot.id] = [token.lemma, slot.core_element_type]
		elif slot.component_type == "mwe":
			previous_mwe = MWE.objects.get(id=slot.id_of_mwe)
			previous_mwe_token_ids = previous_mwe.components.all().values_list("id", flat=True)
			for previous_mwe_token_id in previous_mwe_token_ids:
				if previous_mwe_token_id in mwe_components:
					slot_and_mwe_id_dict[slot.id] = [str(previous_mwe), slot.core_element_type]
	if check_overlapping == "true" and len(slot_and_mwe_id_dict) > 0:
		return JsonResponse({"overlapping_mwe": True, "list_of_slots": slot_and_mwe_id_dict})
	new_frame = copy_frame(frame, used_time=used_time, annotation_state=request.session["annotation_state"],
						   delete_mwe=mwe_id, description="delete MWU")
	if mwe.mwe_verb:
		new_frame.verb_addition = ""
		new_frame.position = str(new_frame.position).split('-')[0]
		new_frame.save()
	request.session["frame_nr"] = new_frame.id
	request.session["time_spent"] = time.time()
	return JsonResponse({"mwe_verb": mwe.mwe_verb, "token_ids": new_token_ids, "overlapping_mwe": False})


def change_slot_with_mwe(request):
	username = request.user.username
	# extend slot with mwe
	frame = Frame.objects.get(id=request.session["frame_nr"], user=username, current_version=True)
	used_time = time.time() - request.session["time_spent"]
	slot = Slot.objects.get(id=request.POST.get("slot_id"))
	old_slot_id = slot.id
	# print("mwe_id", request.POST.get("mwe_id"), old_slot_id)
	mwe = MWE.objects.get(id=request.POST.get("mwe_id"))
	slot.pk = None
	slot.save()
	slot.component_type = "mwe"
	slot.id_of_mwe = int(mwe.id)
	slot.id_of_token = None
	slot.role_label = None
	slot.save()
	frame.slot_element.add(slot)
	frame.save()
	frame = copy_frame(frame, delete_core_element=True, delete_id=old_slot_id, used_time=used_time,
					   annotation_state=request.session["annotation_state"], description="extend slot with MWU")
	request.session["frame_nr"] = frame.id
	request.session["time_spent"] = time.time()
	return JsonResponse({"new_core_element_id": slot.id, "old_core_element_id": old_slot_id, "mwe_lemma": str(mwe)})


def edit_core_element(request):
	username = request.user.username
	# editing core elements
	frame_to_change = Frame.objects.get(id=request.session["frame_nr"], user=username, current_version=True)
	if request.session["mwe_or_tok"] == "tok":
		slot_id = frame_to_change.slot_element.get(id_of_token=int(request.session["token_id"])).id
	else:
		slot_id = frame_to_change.slot_element.get(id_of_mwe=int(request.session["mwe_id"])).id
	request.session["core_element_id"] = slot_id
	slot_type = request.POST.get("slot_type")
	if slot_type:
		slot_type = slot_type.strip()
	references = request.POST.getlist("references[]")
	# role_label = request.POST.get("role_label")
	used_time = time.time() - request.session["time_spent"]
	new_core_element = copy_frame(frame_to_change, change_core_element=(slot_id, slot_type), used_time=used_time,annotation_state=request.session["annotation_state"], references=references, description="edit core element")

	# check if core element type exist
	check_for_coreelementtype_creating(FrameType.objects.filter(name=request.POST.get("f_type"))[0], new_core_element)
	request.session["frame_nr"] = frame_to_change.id
	request.session["time_spent"] = time.time()
	return JsonResponse(
		{"new_core_element_id": new_core_element.id, "slot_type": slot_type,
		 "frame_id": request.session["frame_nr"], "old_core_element_id": slot_id,
		 "token_id": request.session["token_id"], "semantic_role": new_core_element.role_label})


def check_references(new_slot, references):
	if "c" in references:
		new_slot.reference_c = True
	else:
		new_slot.reference_c = False
	if "d" in references:
		new_slot.reference_d = True
	else:
		new_slot.reference_d = False
	if "r" in references:
		new_slot.reference_r = True
	else:
		new_slot.reference_r = False
	new_slot.save()
	return new_slot


def add_core_element(request):
	username = request.user.username
	slot_type = request.POST.get("slot_type")
	if slot_type:
		slot_type = slot_type.strip()
	f_type = request.session["frame_type"]  # request.POST.get("f_type")
	references = request.POST.getlist("references[]")
	f_nr = request.session["frame_nr"]
	frame = Frame.objects.get(id=f_nr, user=username, current_version=True)
	used_time = time.time() - request.session["time_spent"]

	frame = copy_frame(frame, used_time=used_time, annotation_state=request.session["annotation_state"],
					   description="add core element")
	if request.session["mwe_or_tok"] == "tok":
		token = Token.objects.get(id=request.session["token_id"])
		new_slot = Slot(frame_id=frame.id, id_of_token=token.id, component_type="token", core_element_type=slot_type)
		new_slot.save()
		check_for_coreelementtype_creating(FrameType.objects.filter(name=f_type)[0], new_slot)
		new_slot = check_references(new_slot, references)
		frame.slot_element.add(new_slot)
		frame.save()
		request.session["frame_nr"] = frame.id
		request.session["time_spent"] = time.time()
		return JsonResponse({"id": new_slot.id, "position": token.position, "word_form": token.word_form,
							 "slot_type": slot_type, "token_id": token.id, "frame_id": request.session["frame_nr"],
							 "multiword_component": False, "token_lemma": token.lemma})
	else:
		possible_mwes = int(request.session["mwe_id"])
		mwe = MWE.objects.get(id=possible_mwes)
		word_form = " ".join(mwe.components.all().order_by("position").values_list("word_form", flat=True))
		position = ";".join([str(pos) for pos in mwe.components.all().order_by("position").values_list("position", flat=True)])
		lemma = " ".join(mwe.components.all().order_by("position").values_list("lemma", flat=True))
		token_ids = ";".join([str(pos) for pos in mwe.components.all().order_by("position").values_list("id", flat=True)])
		new_slot = Slot(frame_id=frame.id, id_of_mwe=mwe.id, component_type="mwe", core_element_type=slot_type)
		new_slot.save()
		new_slot = check_references(new_slot, references)
		check_for_coreelementtype_creating(FrameType.objects.filter(name=f_type)[0], new_slot)
		frame.slot_element.add(new_slot)
		frame.save()
		request.session["frame_nr"] = frame.id
		request.session["time_spent"] = time.time()
		return JsonResponse({"id": new_slot.id, "position": position, "word_form": word_form,
							 "slot_type": slot_type, "token_id": token_ids,
							 "frame_id": request.session["frame_nr"],
							 "multiword_component": True, "token_lemma": lemma})


def delete_core_element(request):
	# deleting core elements
	username = request.user.username
	f_nr = request.session["frame_nr"]
	delete_slot_of_mwe = int(request.POST.get("delete_slot_of_mwe"))
	print(delete_slot_of_mwe, f_nr)
	frame_element_to_change = Frame.objects.get(id=f_nr, user=username, current_version=True)
	used_time = time.time() - request.session["time_spent"]
	if delete_slot_of_mwe == 1:
		slot = Slot.objects.get(id=request.POST.get("core_element_id"))
		core_element_id = slot.id
		if slot.component_type == "token":
			token_ids = slot.id_of_token
			token_positions = Token.objects.get(id=token_ids).position
			request.session["mwe_or_tok"] = "token"
		else:
			token_ids = list()
			token_positions = list()
			mwe_token = MWE(id=slot.id_of_mwe)
			mwe_token = mwe_token.components.all()
			for mwc in mwe_token:
				token_ids.append(str(mwc.id))
				token_positions.append(str(mwc.position))
			token_ids = ";".join(token_ids)
			token_positions = ";".join(token_positions)
			request.session["mwe_or_tok"] = "mwe"

	else:
		if request.session["mwe_or_tok"] == "tok":
			core_element_id = frame_element_to_change.slot_element.get(id_of_token=request.session["token_id"]).id
			token_ids = request.session["token_id"]
			token_positions = request.session["token_position"]
		else:
			core_element_id = frame_element_to_change.slot_element.get(id_of_mwe=request.session["mwe_id"]).id
			token_ids = list()
			token_positions = list()
			mwe_token = MWE(id=Slot.objects.get(id=core_element_id).id_of_mwe).components.all()
			for mwc in mwe_token:
				token_ids.append(str(mwc.id))
				token_positions.append(str(mwc.position))
			token_ids = ";".join(token_ids)
			token_positions = ";".join(token_positions)
	frame_element_to_change = copy_frame(frame_element_to_change, delete_core_element=True, delete_id=core_element_id, used_time=used_time, annotation_state=request.session["annotation_state"], description="delete core element")
	request.session["frame_nr"] = frame_element_to_change.id
	request.session["time_spent"] = time.time()

	return JsonResponse({"frame_id": request.session["frame_nr"], "old_core_element_id": core_element_id,
						 "token_ids": token_ids, "annotation_state": request.session["annotation_state"],
						 "mwe_or_tok": request.session["mwe_or_tok"], "token_positions": token_positions})


def get_refereces(slot):
	return slot.core_element_type, slot.reference_c, slot.reference_d, slot.reference_r

def change_core_types(request):
	# searching possible core types
	username = request.user.username
	mwe_id = request.POST.get("mwe_id")
	token_position = request.POST.get("token_position")
	request.session["token_position"] = token_position
	request.session["token_id"] = request.POST.get("token_id")
	frame_id = request.session["frame_nr"]
	# comment = request.POST.get("comment")
	# certainty_value = request.POST.get("certainty_scale")
	frame = Frame.objects.get(user=username, id=frame_id, current_version=True)
	frame_type = frame.f_type  # request.POST.get("f_type")
	checked_type = None
	# check if mwe.
	possible_mwes = frame.mwe.filter(components__id=request.session["token_id"])
	dict_mwes = dict()
	# saved_role_label = None
	c_ref, d_ref, r_ref = False, False, False
	if len(possible_mwes) == 0:
		count_mwes = 0
		request.session["token_id"] = request.POST.get("token_id")
		request.session["mwe_or_tok"] = "tok"
		if Frame.objects.get(id=frame_id, user=username).slot_element.filter(id_of_token=request.session["token_id"]):
			slot = Frame.objects.get(id=frame_id, user=username).slot_element.get(
				id_of_token=request.session["token_id"])
			checked_type, c_ref, d_ref, r_ref = get_refereces(slot)
	elif len(possible_mwes) == 1:
		request.session["mwe_id"] = possible_mwes[0].id
		request.session["mwe_or_tok"] = "mwe"
		count_mwes = 1
		dict_mwes[possible_mwes[0].id] = " ".join(
			possible_mwes[0].components.order_by("position").values_list("lemma", flat=True))
		if Frame.objects.get(id=frame_id, user=username).slot_element.filter(id_of_mwe=possible_mwes[0].id):
			slot = Frame.objects.get(id=frame_id, user=username).slot_element.get(id_of_mwe=request.session["mwe_id"])
			checked_type, c_ref, d_ref, r_ref = get_refereces(slot)
	elif mwe_id:
		request.session["mwe_id"] = int(mwe_id)
		request.session["mwe_or_tok"] = "mwe"
		count_mwes = 1
		mwe_with_id = MWE.objects.get(id=mwe_id)
		dict_mwes[mwe_with_id.id] = " ".join(
			mwe_with_id.components.order_by("position").values_list("lemma", flat=True))

		if Frame.objects.get(id=frame_id, user=username).slot_element.filter(id_of_mwe=mwe_id):
			slot = Frame.objects.get(id=frame_id, user=username).slot_element.get(id_of_mwe=mwe_id)
			checked_type, c_ref, d_ref, r_ref = get_refereces(slot)
	else:
		count_mwes = len(possible_mwes)
		request.session["mwe_id"] = list(possible_mwes.values_list("id", flat=True))
		request.session["mwe_or_tok"] = "mwe"
		for mwe in possible_mwes:
			dict_mwes[mwe.id] = " ".join(mwe.components.order_by("position").values_list("lemma", flat=True))
		# saved_role_label = None
		c_ref, d_ref, r_ref = False, False, False
	core_type_dict = dict()
	all_slot_types = list()
	for frame_type_element in FrameType.objects.filter(name=frame_type):
		for core_type in frame_type_element.core_types.all():
			if core_type.name == checked_type and (core_type.core_type == "core" or core_type.core_type == "core_unexpressed"):
				core_type_dict[core_type.name] = {"definition": core_type.definition, "id": core_type.id, "checked": True}
			elif core_type.name == checked_type:
				core_type_dict[core_type.name] = {"definition": core_type.definition, "id": core_type.id, "checked": True, "non-core": True}
			elif (core_type.core_type == "core" or core_type.core_type == "core_unexpressed") and core_type.name != checked_type and not core_type.new_custom_value:
				core_type_dict[core_type.name] = {"definition": core_type.definition, "id": core_type.id, "checked": False}
			elif (core_type.core_type == "core" or core_type.core_type == "core_unexpressed") and core_type.name != checked_type and not core_type.new_custom_value:
				core_type_dict[core_type.name] = {"definition": core_type.definition, "id": core_type.id, "checked": False}
			elif core_type.core_type == "new_custom" or core_type.new_custom_value == True:
				pass
			else:
				# non core
				all_slot_types.append(core_type.name)
	additional_core_type = dict()
	request.session["frame_type"] = frame_type
	return JsonResponse(
		{"frame_type": frame_type, "selection_core_types": core_type_dict, "additional_core_type": additional_core_type,
		 "all_slot_types": sorted(all_slot_types), "count_mwes": count_mwes, "dict_mwes": dict_mwes,
		 "c_ref": c_ref, "d_ref": d_ref, "r_ref": r_ref})


def save_frame_type(request):
	# saving frame type after selecting a new input choice
	username = request.user.username
	frame_type = request.POST.get("f_type")
	if frame_type:
		frame_type = frame_type.strip()
	frame_id = request.session["frame_nr"]
	comment = request.POST.get("comment")
	frame = Frame.objects.get(user=username, id=frame_id, current_version=True)
	frame_verb = frame.verb_lemma + ".v"
	if request.POST.get("other_f_type"):
		# change and add new custom frame type
		new_frame_type = change_and_save_new_frame_type(frame_type, frame_verb, frame=frame, save_core_types=False)
	elif frame_type not in FrameType.objects.values_list("name", flat=True) and AnnotationSettings.objects.get(id=1).custom_frame_type:
		new_frame_type = change_and_save_new_frame_type(frame_type, frame_verb, frame=frame, save_core_types=True)
	list_possible_slot_types = list(FrameType.objects.get(name=frame_type).core_types.filter(core_type="non_core").values_list("name", flat=True))

	used_time = time.time() - request.session["time_spent"]
	frame_and_delete_dict = copy_frame(frame, used_time=used_time, list_possible_slot_types=list_possible_slot_types, delete_elements_on_frametype_change=True, annotation_state=request.session["annotation_state"], description="save frame type and delete wrong slots")
	if type(frame_and_delete_dict) == list:
		frame = frame_and_delete_dict[0]
		delete_elements = frame_and_delete_dict[1]
	else:
		frame = frame_and_delete_dict
		delete_elements = dict()
	frame.f_type = frame_type
	frame.annotated = True
	frame.comment = comment
	frame.save(update_fields=["f_type", "annotated", "comment", "change_id"])

	request.session["frame_nr"] = frame.id
	request.session["time_spent"] = time.time()
	request.session["frame_type"] = frame_type
	return JsonResponse({"delete_elements": delete_elements, "frame_id": request.session["frame_nr"]})


def get_frame_data(request, get_user=None):
	additional_frame_type = ''
	username = request.user.username
	frame_identifiers = request.path_info.split("_")
	if len(frame_identifiers) != 3:
		return redirect("frame_not_found")
	#frame_verb = frame_identifiers[1]
	frame_position = frame_identifiers[1]
	frame_sentence_id = frame_identifiers[2]
	# redirected from frame_list show frame detail page the first time
	if get_user:
		frame = get_frame(frame_sentence_id, frame_position, username, username, get_user)
	else:
		frame = get_frame(frame_sentence_id, frame_position, username, username)
	if not frame:
		return redirect("frame_not_found")
	annotation_state = frame.annotation_state
	request.session["annotation_state"] = annotation_state
	# if annotation_state == 0:
	request.session["frame_nr"] = frame.id
	frame_id = request.session["frame_nr"]
	frame_verb = frame.verb_lemma
	if AnnotationSettings.objects.get(id=1).custom_frame_type:
		possible_frame_types = FrameType.objects.filter(lexUnits__verb__exact=frame_verb + ".v")
	else:
		possible_frame_types = FrameType.objects.filter(
			Q(lexUnits__verb__exact=frame_verb + ".v", new_custom_value=False))
	synonym_frame_type_dict = collections.OrderedDict()
	synonyms_list = Synonyms.objects.filter(verb=frame_verb + ".v")
	"""for synonym in synonyms_list:
		if AnnotationSettings.objects.get(id=1).custom_frame_type:
			frame_type_list = FrameType.objects.filter(lexUnits__verb = synonym.synonym).values_list("name", flat=True)
		else:
			frame_type_list = FrameType.objects.filter(lexUnits__verb=synonym.synonym, new_custom_value=False).values_list("name", flat=True)
		if len(frame_type_list) > 0:
			synonym_frame_type_dict[synonym.synonym[:-2]] = list()
			if synonym.xml_ids:
				for xml_id, frame_type_name in zip(synonym.xml_ids.split(";"), frame_type_list):
				#for xml_id, frame_type_name in zip(range(len(frame_type_list)), frame_type_list):
					 synonym_frame_type_dict[synonym.synonym[:-2]].append([xml_id, frame_type_name])
		# for type_of_frame in frame_type_list:
		#	if type_of_frame.name in synonym_frame_type_dict:
		#		synonym_frame_type_dict[type_of_frame.name].append(synonym[:-2])
		#	else:
		#		synonym_frame_type_dict[type_of_frame.name] = [synonym[:-2]]"""
	synonym_frame_type_dict = sort_dict_by_key(synonym_frame_type_dict)
	if frame.f_type not in possible_frame_types.values_list("name", flat=True):
		additional_frame_type = frame.f_type
	verb_examples = {}
	# select all frame types which are unequal to the already suggested ones
	if AnnotationSettings.objects.get(id=1).custom_frame_type:
		request.session["all_frame_types"] = list(
			FrameType.objects.filter(~Q(lexUnits__verb__exact=frame_verb + ".v")).values_list("name", flat=True))
	else:
		request.session["all_frame_types"] = list(
			FrameType.objects.filter(~Q(lexUnits__verb__exact=frame_verb + ".v"),
									 Q(new_custom_value=False)).values_list("name", flat=True))
	for verb_id in frame.verb_ids.split(";")[:-1]:
		if verb_id != "None":
			if AnnotationSettings.objects.get(id=1).custom_frame_type:
				verb_examples[FrameType.objects.get(lexUnits__xml_id=verb_id).name] = verb_id
			else:
				verb_examples[FrameType.objects.get(lexUnits__xml_id=verb_id, new_custom_value=False).name] = verb_id
	request.session["frame_nr"] = frame_id
	request.session["time_spent"] = time.time()
	request.session["time_step"] = time.time()
	all_mwes = frame.mwe.all()
	mwe_positions = set()
	vmwe_positions = set()
	for mwe in all_mwes:
		for position in mwe.components.values_list("position", flat=True):
			if mwe.mwe_verb and str(position) != frame.position.split('-')[0]:
				vmwe_positions.add(position)
			else:
				mwe_positions.add(position)

	if len(Frame.objects.filter(user=username, annotated=True, current_version=True)) > 0:
		first_annotation = False
	else:
		first_annotation = True
	core_element_positions = list()
	core_elements_dict = dict()
	token_slots = frame.slot_element.filter(id_of_token__isnull=False)
	mwe_slots = frame.slot_element.filter(id_of_mwe__isnull=False)
	if token_slots:
		for slot in token_slots:
			token = Token.objects.get(id=slot.id_of_token)
			core_elements_dict[slot.id] = {"lemma": token.lemma, "slot_type": slot.core_element_type, "semantic_role": slot.role_label}
			core_element_positions.append(token.position)
	if mwe_slots:
		for slot in mwe_slots:
			lemma_string = ""
			for mwe_token in MWE.objects.get(id=slot.id_of_mwe).components.all():
				core_element_positions.append(mwe_token.position)
				lemma_string += mwe_token.lemma + " "
				core_elements_dict[slot.id] = {"slot_type": slot.core_element_type, "lemma": lemma_string}
	return render(request, "annotate/frame_detail.html", {"frame": frame,
														  "selection_frame_types": possible_frame_types,
														  "core_element_positions": core_element_positions,
														  "verb_examples": verb_examples,
														  "additional_frame_type": additional_frame_type,
														  "multiword_component_positions": mwe_positions,
														  "vmwe_positions": vmwe_positions,
														  "comment": frame.comment,
														  "certainty": frame.certainty,
														  "annotation_state": annotation_state, "all_mwes": all_mwes,
														  "first_annotation": first_annotation,
														  "core_elements_dict": core_elements_dict,
														  "synonym_frame_type_dict": synonym_frame_type_dict,
														  "add_custom_frame_types": AnnotationSettings.objects.get(
															  id=1).custom_frame_type,
														  "add_custom_element_types": AnnotationSettings.objects.get(
															  id=1).custom_element_type})


@login_required(login_url="login")
def frame_detail(request,a=None,b=None):
	"""
	produce the most important page: the annotation page. The function is called when editing, adding, deleting,
	changing core types, changing frame types and seeing the current state of the frame.
	:return: if changes on core element or frame type, returns a json response which data will be integrated in the
				frontend. Everytime the detail template will be returned including the sentence representation,
				frame representation, frame type selection.
	"""
	username = request.user.username
	additional_frame_type = ""
	if request.method == "POST":
		change_type = request.POST.get("change_type")
		if change_type == "go_forward":
			return go_direction(request, "forward")
		elif change_type == "go_back":
			return go_direction(request, "back")
		elif change_type == "save_mwe":
			return save_mwe(request)
		elif change_type == "delete_mwe":
			return delete_mwe(request)
		elif change_type == "change_slot_with_mwe":
			return change_slot_with_mwe(request)
		elif change_type == "edit":
			return edit_core_element(request)
		elif change_type == "add":
			return add_core_element(request)
		elif change_type == "delete":
			return delete_core_element(request)
		elif change_type == "change_core_types":
			return change_core_types(request)
		elif change_type == "save_frame_type":
			print(1111)
			return save_frame_type(request)
		else:
			print("something went wrong.")
			return render(request, "annotate/frames_list.html")
	else:
		if request.GET.get("user"):
			return get_frame_data(request, request.GET.get("user"))
		else:
			return get_frame_data(request, None)


@login_required(login_url="login")
def skip_sentence(request):
	if request.user.is_authenticated:
		username = request.user.username
		request.session["username"] = username
		print(username)
	else:
		return render(request, "annotate/introduction.html")
	if request.method == "POST":
		#frame_type = request.POST.get("f-type")
		frame_id = request.session["frame_nr"]
		skip_reason = request.POST.get("skip_reason")
		print(skip_reason)
		frame = Frame.objects.get(user=username, id=frame_id, current_version=True)
		frame_verb = frame.verb_lemma+".v"
		used_time = time.time() - request.session["time_spent"]
		annotation_state = request.session["annotation_state"]
		frame = copy_frame(frame, used_time=used_time, annotation_state=annotation_state, skipped=True, description="skip sentence")
		frame.annotated = True
		frame.skip_reason = skip_reason
		frame.save(update_fields=["comment", "certainty", "annotated", "skip_reason"])
		request.session["frame_nr"] = frame.id
		request.session["time_spent"] = time.time()
		return JsonResponse({"page_name": "frame_list"})
	else:
		new_user = ExtendedUser(username=username, ip_adress=request.META["REMOTE_ADDR"], browser=request.META["HTTP_USER_AGENT"])
		new_user.save()
	request.session["annotation_state"] = 0
	return render(request, "annotate/frames_list.html", {"skipped_frames": Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=True).order_by("verb_lemma"),
														 "frames_in_progress": Frame.objects.filter(Q(user=username, current_version=True, skipped=False, annotation_state__range=[1,4]) | Q(user=username, current_version=True, skipped=False, annotation_state=4, annotated=False)).order_by("verb_lemma") ,
														 "annotated_frames": Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=False, annotation_state=5).order_by("verb_lemma"),
														 "not_annotated_frames": Frame.objects.filter(user=username, annotated=False, current_version=True, annotation_state=0, skipped=False).order_by("verb_lemma"),
														 })


def change_and_save_new_frame_type(frame_type, frame_verb, frame=None, save_core_types=False, assign_to_lex=False):
	"""
		check if a frame type with the name exist already. If not a new one will be created, also the core element types
		can be added to it, if save_core_types is true. That"s the case, when a new custom frame type was inserted.
		If a frame type exist with the same, it will be checked if the combination with the verb lemma is allowed so far,
		if not it will assigned (-> check for lexical unit creating).
		:param frame_type: name of the new frame type
		:param frame_verb: verb of the frame
		:param frame: frame object, add core elements to the frame object when save core types is enabled
		:param save_core_types: boolean to add new core types to the frame object or not.
		:return:
	"""
	frame_type_object = FrameType.objects.filter(name=frame_type)
	if len(frame_type_object) > 0:
		# if the frame type already exist assign the verb and lexunits to it
		if assign_to_lex:
			new_frame_type = check_for_lexicalunit_creating(frame_type_object[0], frame_verb)
		else:
			new_frame_type = frame_type_object
		#print("frame type exist, assign verb")
	else:
		# if there is no object with this frame type name, create a new one
		if AnnotationSettings.objects.get(id=1).custom_frame_type:
			new_frame_type = FrameType(name=frame_type, new_custom_value=True)
			new_frame_type.save()
			new_frame_type = check_for_lexicalunit_creating(new_frame_type, frame_verb, created=True)
			#print("create a new frame")
		else:
			raise LookupError

	if save_core_types:
		print("add coretype")
		for slot in frame.slot_element.all():
			#print(slot.slot_type, "slot assigned to frametype", type(slot))
			check_for_coreelementtype_creating(new_frame_type, slot)

	return new_frame_type


def check_for_lexicalunit_creating(frame_type_object, frame_verb, created=False):
	"""
	used to create or change the lexicalunits of a frametype
	if a new frametype name was used or a frametype was assigned to a new verb, assign the lexical unit to the frametype
	:param frame_type_object: FrameType object with inserted frame name in free text field
	:param frame_verb: verb of the frame. Needed to assign to the new frametype
	:return:
	"""
	"""if created == True:
		new_lexunit = LexicalUnits(verb=frame_verb, new_custom_value=True)
		new_lexunit.save()
		frame_type_object.lexUnits.add(new_lexunit)
		frame_type_object.save()
	else:"""
	if len(frame_type_object.lexUnits.all().filter(verb=frame_verb)) == 0:
		# check if verb is already assigned to frame
		#lexunit_objects = LexicalUnits.objects.filter(verb=frame_verb)
		if len(LexicalUnits.objects.filter(verb=frame_verb, xml_id__isnull=True)) == 1:
			# if one object without xml id exist assign this one and dont create a new one
			frame_type_object.lexUnits.add(LexicalUnits.objects.filter(verb=frame_verb, xml_id__isnull=True)[0])
			frame_type_object.save()
			#print("assign new verb")
		else:
			# if one (which is not assigned to xml id, without this combination in framenet), more or zero objects with same lemma, create new lexunit withput xmlid
			new_lexunit = LexicalUnits(verb=frame_verb, new_custom_value=True, xml_id=None)
			new_lexunit.save()
			frame_type_object.lexUnits.add(new_lexunit)
			frame_type_object.save()
			#print("create new word")
	else:
		# verb is already assigned, maybe add new core types
		pass
	return frame_type_object


def check_for_coreelementtype_creating(new_frame_type, slot):
	"""
	check if the slot type is already assigned to the frame type. If there are more than one slot type with the same
	name but different xml ids create a new core element object. If a core element withput xml id already exist assign
	this one. return the frame type object with the changed core element types. useful when a necessarry core element type
	is missing, this will be added to the selection of the frame type which make the following annotations easier.
	:param new_frame_type: new frame type object
	:param slot: name of the new slot type
	:return: new frame type object with or withnot assigned slot type
	"""
	if len(new_frame_type.core_types.all().filter(name=slot.core_element_type)) == 0 and AnnotationSettings.objects.get(id=1).custom_element_type:
		new_slot_type = CoreElementType(name=slot.core_element_type, new_custom_value=True, core_type="new_custom")
		new_slot_type.save()
		# Create more elements if a custom one with same name exists?
		new_frame_type.core_types.add(new_slot_type)
		new_frame_type.save()
	else:
		# slot type is already asigned
		pass
	return new_frame_type



def change_slot_for_copy(old_core_element, new_mwe_object):
	# change slot
	new_slot_object = old_core_element
	new_slot_object.pk = None
	new_slot_object.save()
	new_slot_object.component_type = "mwe"
	new_slot_object.id_of_token = None
	new_slot_object.id_of_mwe = new_mwe_object.id
	new_slot_object.role_label = None
	new_slot_object.save()
	return new_slot_object


def create_extended_slot(frame_object, type_of_slot, old_core_element, new_mwe, old_components=None):
	new_mwe_object = MWE()
	new_mwe_object.save()
	lemma_string = ""
	for token_id in new_mwe:
		token = Token.objects.get(id=token_id)
		if type_of_slot == "tok":
			if str(token.position) in frame_object.position.split('-'):
				new_mwe_object.mwe_verb = True
			else:
				lemma_string += "_" + token.lemma
		else:
			if token_id not in old_components:
				lemma_string += "_" + token.lemma
			#new_mwe_object.components.add(token)
		new_mwe_object.components.add(token)
		new_mwe_object.save()
	if type_of_slot == "mwe":
		for token_id in old_components:
			token = Token.objects.get(id=token_id)
			lemma_string += "_" + token.lemma
			new_mwe_object.components.add(token)
			new_mwe_object.save()
	frame_object.mwe.add(new_mwe_object)
	frame_object.save()
	new_slot_object = change_slot_for_copy(old_core_element, new_mwe_object)

	frame_object.slot_element.add(new_slot_object)
	frame_object.save()
	return frame_object, new_slot_object


def copy_frame(frame_object, delete_core_element=False, delete_id=None, delete_elements_on_frametype_change=False,
			   list_possible_slot_types = [], change_core_element=("core_element_id","slot_type"), used_time=0,
			   comment=None,certainty_value=None, user=None, annotation_state=0, time_spent=0, new_mwe=None, delete_mwe=None,
			   references=[], role_label=None, skipped=False, change_slot_id=None, add_mwe_and_edit_slot_id=None,
			   delete_multiple_core_elements=False, list_core_element_ids=[], overlapped_slot_type=None, description=""):
	"""
	create a copy from the current frame object, set the current version
	of the old object to false and the copied one to true. All core elements will be created new and assigend again to
	the new frame, because otherwise a history of changes is not possible. If a new core element will be added, all old
	core elements will be copied and the new one will also be added. If a old core element was changed a tuple was inserted
	as change_core_element, where the first value is the database id of the core element and the second value the new
	slot type. For changing the core element, the old one will be copied and changed afterwards. If a core element will
	be deleted, delete_core_element is equal to a core element id of the old core elements, this core element will be
	skipped and all other will be assigned to the new frame type. If the frame types changes and core element types
	doesn"t fit anymore they will be deleted in the same way.
	"""
	old_core_elements = frame_object.slot_element.all()
	#old_mwc = frame_object.multiword_component.all()
	old_mwes = frame_object.mwe.all()


	if not user:
		# if username given keep old and new frame as current version
		frame_object.current_version = False
	old_sentence = frame_object.sentence
	frame_object.save()
	frame_object.pk = None
	frame_object.save()
	frame_object.sentence = old_sentence
	frame_object.current_version = True
	frame_object.change_id += 1
	frame_object.used_time = used_time
	frame_object.description_of_change = description
	if time_spent != 0:
		frame_object.time_spent += time_spent
	frame_object.annotation_state = annotation_state
	if user:
		frame_object.user = user
	frame_object.comment = comment
	if certainty_value and certainty_value != frame_object.certainty:
		frame_object.certainty = certainty_value
	frame_object.save()
	delete_elements = dict()
	new_slot = None
	for old_core_element in old_core_elements:
		old_core_element_id = old_core_element.id
		if delete_core_element and delete_id == old_core_element_id:
			print("element deleted")
			pass
		elif delete_multiple_core_elements and old_core_element_id in list_core_element_ids:
			pass
		elif delete_elements_on_frametype_change:
			if old_core_element.core_element_type not in list_possible_slot_types:
				if old_core_element.component_type == "token":
					token = Token.objects.get(id=old_core_element.id_of_token)
					delete_elements[old_core_element.id] = {"token_id": token.id,
													"token_position": token.position}
				elif old_core_element.component_type == "mwe":
					mwe = MWE.objects.get(id=old_core_element.id_of_mwe)
					mwe_positions = ""
					token_ids = ""
					for element in mwe.components.all():
						mwe_positions += str(element.position)+";"
						token_ids += str(element.id)+";"
					#mwe_positions = ";".join([str(position) for position in mwe.components.values_list("position", flat=True)])
					delete_elements[old_core_element.id] = {"mwe_id": mwe.id,
													"mwe_position": mwe_positions[:-1], "token_ids": token_ids[:-1]}
			else:
				frame_object.slot_element.add(old_core_element)
				frame_object.save()
		elif change_core_element[0] == old_core_element_id:
			new_slot = old_core_element
			new_slot.pk = None
			new_slot.core_element_type = change_core_element[1]
			new_slot.role_label = None
			new_slot.save()
			new_slot = check_references(new_slot, references)
			frame_object.slot_element.add(new_slot)
			frame_object.save()
			print("change slot", change_core_element[0], old_core_element_id, new_slot.id)

		elif add_mwe_and_edit_slot_id == old_core_element_id:
			# str(previous_mwe), slot.core_element_type, "mwe_slot", slot.id
			# add mwe
			if overlapped_slot_type == "token_slot":
				# overlap 2) if mwe overlaps a single token slot -> create MWE and extend slot with MWE
				frame_object, new_slot_object = create_extended_slot(frame_object, "tok", old_core_element, new_mwe)
			else:
				# overlap 3) if mwe overlaps mwe with slot -> extend MWE & extend slot with extend MWE
				new_mwe_object = MWE.objects.get(id=delete_mwe)
				old_components = new_mwe_object.components.values_list("id", flat=True)
				new_mwe_object.pk = None
				new_mwe_object.save()
				frame_object, new_slot_object = create_extended_slot(frame_object, "mwe", old_core_element, new_mwe, old_components=old_components)
		else:
			# append old core element without changes
			frame_object.slot_element.add(old_core_element)
			frame_object.save()
	for mwe in old_mwes:
		#print(delete_mwe, mwe.id, type(mwe.id), type(delete_mwe))
		if delete_mwe and int(delete_mwe) == mwe.id:
			pass
		else:
			frame_object.mwe.add(mwe)
			frame_object.save()
	if new_mwe and not add_mwe_and_edit_slot_id:
		# new_mwe = ids of mwe components
		new_mwe_object = MWE()
		new_mwe_object.save()
		lemma_string = ""
		pos_string = ""
		for token_id in new_mwe:
			token = Token.objects.get(id=token_id)
			if str(token.position) in frame_object.position.split('-'):
				new_mwe_object.mwe_verb = True
			else:
				lemma_string += "_"+token.lemma
				pos_string += "-"+str(token.position)
			new_mwe_object.components.add(token)
			new_mwe_object.save()
		frame_object.mwe.add(new_mwe_object)
		#frame_object.verb_lemma = lemma_string
		#print(lemma_string)
		if new_mwe_object.mwe_verb:
			frame_object.verb_addition = lemma_string
			frame_object.position += pos_string
		print(frame_object, frame_object.verb_addition, frame_object.position)
		frame_object.save()
	#print("frame object", frame_object)
	#print("in func", delete_elements)
	if skipped:
		frame_object.skipped = True
		frame_object.save()
	else:
		frame_object.skipped = False
		frame_object.skip_reason = ""
		frame_object.save()
	if new_slot:
		return new_slot
	if len(delete_elements.keys()) > 0:
		return [frame_object, delete_elements]
	if new_mwe:
		if add_mwe_and_edit_slot_id:
			return [frame_object, new_mwe_object.id, new_mwe_object.mwe_verb, new_slot_object, new_mwe_object]
		else:
			return [frame_object, new_mwe_object.id, new_mwe_object.mwe_verb]
	return frame_object



##########################
##### cleaning db ########
##########################


@login_required(login_url="login")
def delete_wrong_types(request):
	if request.user.is_superuser:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		directory_path = os.path.join(base_dir,"fndata-1.7/frame/")
		if request.method == "POST":
			list_ids_lex = request.POST.getlist("delete_ids_lexicalunits")
			list_ids_core = request.POST.getlist("delete_ids_elementtypes")
			for element in list_ids_lex:
				element = element.split("_")
				frame_type_id = element[0]
				new_frame_type = FrameType.objects.get(id=frame_type_id)
				lexunit = LexicalUnits.objects.get(id=element[1])
				new_frame_type.lexUnits.remove(lexunit)
			for element in list_ids_core:
				element = element.split("_")
				frame_type_id = element[0]
				new_frame_type = FrameType.objects.get(id=frame_type_id)
				element_type = CoreElementType.objects.get(id=element[1])
				new_frame_type.core_types.remove(element_type)
			return render(request, "annotate/admin_functions.html")

		else:
			output_dict_core, output_dict_lex = dict(), dict()
			for nr, filename in enumerate(sorted(os.listdir(directory_path))):

				if filename.endswith("xml"):
					list_core_elements = list()
					list_core_unexpressed = list()
					list_lexunits = list()
					list_non_core = list()
					# print(nr, len(os.listdir(directory_path)))
					root = xml.etree.ElementTree.parse(directory_path + filename).getroot()
					# if len(FrameType.objects.filter(name=root.attrib["name"], xml_id=root.attrib["ID"])) == 1:

					for child in root:
						if child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib["coreType"] == "Core":
							list_core_elements.append(child.attrib["name"])
						elif child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib[
							"coreType"] == "Core-Unexpressed":
							list_core_unexpressed.append(child.attrib["name"])
						elif child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib[
							"coreType"] != "Core-Unexpressed" and child.attrib["coreType"] != "Core":
							list_non_core.append(child.attrib["name"])
						elif child.tag == "{http://framenet.icsi.berkeley.edu}lexUnit" and child.attrib["POS"] == "V":
							# print(child.attrib["name"])
							list_lexunits.append(child.attrib["name"])

					for new_frame_type in FrameType.objects.filter(name=root.attrib["name"], xml_id=root.attrib["ID"]):
						for element_type in new_frame_type.core_types.all():
							if element_type.name not in list_core_elements and element_type.name not in list_core_unexpressed and element_type.name not in list_non_core:
								output_dict_core[str(new_frame_type.id) + "_" + str(element_type.id)] = {"frame_type_name": new_frame_type.name, "element_type_name": element_type.name, "current_number": len(Frame.objects.filter(f_type=new_frame_type.name, slot_element__core_element_type=element_type.name, current_version=1)), "total_number": len(Frame.objects.filter(f_type=new_frame_type.name, slot_element__core_element_type=element_type.name))}
								#print(new_frame_type.name, new_frame_type.id, element_type.name, element_type.core_type,
								#	  element_type.id, len(Frame.objects.filter(f_type=new_frame_type.name,
								#												slot_element__core_element_type=element_type.name)),
								#	  len(Frame.objects.filter(f_type=new_frame_type.name,
								#							   slot_element__core_element_type=element_type.name,
								#							   current_version=1)))

						for lexunit in new_frame_type.lexUnits.all():
							if lexunit.verb not in list_lexunits:
								output_dict_lex[str(new_frame_type.id) + "_" + str(lexunit.id)] = {"frame_type_name": new_frame_type.name, "element_type_name": lexunit.verb,"current_number": len(Frame.objects.filter(verb_lemma=lexunit.verb[:-2], f_type=new_frame_type.name,current_version=1, annotation_state=5)), "total_number": len(Frame.objects.filter(verb_lemma=lexunit.verb[:-2], f_type=new_frame_type.name))}
								# times annotated in all current and old records, times listed in current version, verb, frame_type



			for new_frame_type in FrameType.objects.filter(new_custom_value=True):
				for element_type in new_frame_type.core_types.all():
					if element_type.name not in list_core_elements and element_type.name not in list_core_unexpressed and element_type.name not in list_non_core:
						output_dict_core[str(new_frame_type.id) + "_" + str(element_type.id)] = {
							"frame_type_name": new_frame_type.name, "element_type_name": element_type.name,
							"current_number": len(Frame.objects.filter(f_type=new_frame_type.name,
																	   slot_element__core_element_type=element_type.name,
																	   current_version=1)), "total_number": len(
								Frame.objects.filter(f_type=new_frame_type.name,
													 slot_element__core_element_type=element_type.name))}


				for lexunit in new_frame_type.lexUnits.all():
					if lexunit.verb not in list_lexunits:
						output_dict_lex[str(new_frame_type.id) + "_" + str(lexunit.id)] = {
							"frame_type_name": new_frame_type.name, "element_type_name": lexunit.verb,
							"current_number": len(
								Frame.objects.filter(verb_lemma=lexunit.verb[:-2], f_type=new_frame_type.name,
													 current_version=1)), "total_number": len(
								Frame.objects.filter(verb_lemma=lexunit.verb[:-2], f_type=new_frame_type.name))}
				# times annotated in all current and old records, times listed in current version, verb, frame_type
			return render(request, "annotate/delete_types.html", {"output_dict_lex": output_dict_lex, "output_dict_core": output_dict_core})

	return render(request, "annotate/introduction.html")


@login_required(login_url="login")
def delete_non_lexicalized_frames(request):
	if request.user.is_superuser:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		directory_path = os.path.join(base_dir, "fndata-1.7/frame/")
		list_nonlexic_frames = list()
		list_frames = list()
		list_wrong_frames = list()
		list_semtype = set()
		list_semtype_2 = set()
		frame_list = list()
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		with open(os.path.join(base_dir,"data/frame-index.html"), encoding="utf-8") as f:
			contetn = f.readlines()
		for child in contetn:
			if "<verb>" in child:
				element = child.split("<verb>")[1].split("</")[0]
				frame_list.append(element)
		for frametype in FrameType.objects.filter(new_custom_value=False):
			if frametype.name not in frame_list:
				print("http://corpora.phil.hhu.de/framenet/fndata-1.7/frame/" + frametype.name + ".xml")

		for nr, filename in enumerate(sorted(os.listdir(directory_path))):

			if filename.endswith("xml"):
				root = xml.etree.ElementTree.parse(directory_path + filename).getroot()
				# if len(FrameType.objects.filter(name=root.attrib["name"], xml_id=root.attrib["ID"])) == 1:
				new_frame_type = FrameType.objects.filter(name=root.attrib["name"], xml_id=root.attrib["ID"])
				list_frames.append(root.attrib["name"])
				for child in root:
					# <semType name="Non-Lexical Frame" ID="16"/>
					if child.tag == "{http://framenet.icsi.berkeley.edu}semType" and child.attrib["name"] == "Non-Lexical Frame":
						for frame_type in new_frame_type:
							list_semtype_2.add(root.attrib["name"])
							list_nonlexic_frames.append(root.attrib["name"])
							#print(Frame.objects.filter(current_version=1, f_type=frame_type.name))
							frame_type.delete()
						# break because it is deleted and dont need to test the other condition for the following childs
						break
							#print(frame_type.name)

		return render(request, "annotate/admin_functions.html", {"success": "Non-Lexical Frames deleted."})
	else:
		return render(request, "annotate/introduction.html")




@login_required(login_url="login")
def set_sorting_order(request):
	if request.user.is_authenticated:
		if request.method == "POST":
			print(request.POST.get("id_element"), request.POST.get("value_element"))
			request.session["current_head_of_order"] = request.POST.get("id_element")
			if request.POST.get("value_element") == "none":
				# none = descending ajax is faster than tablesorter
				request.session["current_value_of_order"] = "descending"
			else:
				request.session["current_value_of_order"] = request.POST.get("value_element")

			return JsonResponse({"": ""})
	else:
		return render(request, "annotate/introduction.html")




@login_required(login_url="login")
def delete_old_framenet_types(request):
	if request.user.is_superuser:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		directory_path = os.path.join(base_dir, "fndata-1.7/frame/")
		output_old_core, output_old_frames, output_dict_frames = set(), set(), dict()
		output_file_frames = "" # save all frame types and the row id to rebuild it
		output_file_core = ""  # save all core types and the row id to rebuild it
		user_names = User.objects.values_list("username",  flat=True)
		output = dict()
		for user_name in user_names:
			output[user_name] = set()
		#output = {"behrang":set(), "behrang2": set(), "admin": set(), "julia":set(), "adiseu": set(), "regina": set(), "juliatest": set(), "test":set()}
		for nr, filename in enumerate(sorted(os.listdir(directory_path))):

			if filename.endswith("xml"):
				list_core_elements, list_core_unexpressed, list_lexunits, list_non_core = list()
				root = xml.etree.ElementTree.parse(directory_path + filename).getroot()
				output_dict_frames[root.attrib["name"]] = {"core": set(), "non-core": set(), "verb": set()}

				for child in root:
					if child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib["coreType"] == "Core":
						output_dict_frames[root.attrib["name"]]["core"].add(child.attrib["name"])
					elif child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib[
						"coreType"] == "Core-Unexpressed":
						output_dict_frames[root.attrib["name"]]["core"].add(child.attrib["name"])
					elif child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib[
						"coreType"] != "Core-Unexpressed" and child.attrib["coreType"] != "Core":
						output_dict_frames[root.attrib["name"]]["non-core"].add(child.attrib["name"])
					elif child.tag == "{http://framenet.icsi.berkeley.edu}lexUnit" and child.attrib["POS"] == "V":
						# print(child.attrib["name"])
						output_dict_frames[root.attrib["name"]]["verb"].add(child.attrib["name"])

		#print(output_dict_frames)
		counter = 0
		counter_frame = 0
		output_string = ""
		for frame in Frame.objects.filter(current_version=1, annotation_state__gt=0):
			frame_type = frame.f_type
			if frame_type not in output_dict_frames.keys() and frame_type != "":
				# frame.f_type = ""
				# frame.save(update_fields=["f_type"])
				output_old_frames.add(frame.verb_lemma+"_"+frame_type)
				counter_frame += 1
				output[frame.user].add(str(frame.sentence_id) + " " +frame.verb_lemma + " " + frame_type + "_" + slot.core_element_type)
				output_string += "http://sfa.phil.hhu.de/frame_"+frame.verb_lemma+"_"+str(frame.position)+"_"+str(frame.sentence_id)+" "+frame.user+"\n"

				#print(frame.f_type, frame.user, frame.sentence_id, frame.position)
			elif frame_type == "":
				pass
			else:
				for slot in frame.slot_element.all():
					if slot.core_element_type not in output_dict_frames[frame_type]["core"]:
						#frame.slot_element.remove(slot)
						output_string += "http://sfa.phil.hhu.de/frame_"+frame.verb_lemma+"_"+str(frame.position)+"_"+str(frame.sentence_id)+" "+frame.user+"\n"
						output_old_core.add(frame_type+"_"+slot.core_element_type)
						output[frame.user].add(str(frame.sentence_id)+" "+frame.verb_lemma+" "+frame_type+"_"+slot.core_element_type)
						counter += 1
		response = HttpResponse(output_string, content_type="text/plain")
		response["Content-Disposition"] = "attachment; filename'old_slots_in_annotated_records.txt'"
		return response

	return render(request, "annotate/introduction.html")


def change_core_elements_to_slots(frame_object, user=None):
	"""
		copy all frame objects and save thire core element objects as slot objects
	"""
	old_core_elements = frame_object.core_elements.all()
	#old_mwc = frame_object.multiword_component.all()
	old_mwes = frame_object.mwe.all()
	if not user:
		# if username given keep old and new frame as current version
		frame_object.current_version = False
	old_sentence = frame_object.sentence
	frame_object.save()
	frame_object.pk = None
	frame_object.save()
	frame_object.sentence = old_sentence
	frame_object.current_version = True
	#frame_object.change_id += 1
	#frame_object.used_time = used_time
	frame_object.save()

	for old_core_element in old_core_elements:
		#old_core_element_id = old_core_element.id

		# append old core element without changes
		# convert core element to slot element wit id = token
		#old_core_element
		token = Token.objects.get(sentence_id=old_core_element.sentence_id, position=old_core_element.position)
		new_core_element = Slot(component_type="token", core_element_type=old_core_element.slot_type,
								xml_id=old_core_element.xml_id, id_of_token=token.id)
		new_core_element.save()
		frame_object.slot_element.add(new_core_element)
		frame_object.save()
	if len(frame_object.slot_element.all()) > 0:
		for slot in frame_object.slot_element.all():
			# append old core element without changes
			frame_object.slot_element.add(slot)
			frame_object.save()
	for mwe in old_mwes:
		frame_object.mwe.add(mwe)
		frame_object.save()
	return frame_object



###########################
#### creating database ####
###########################



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@login_required(login_url="login")
def convert_core_elements(request):
	"""
	"""
	if request.user.is_superuser:
		for nr, frame_object in enumerate(Frame.objects.filter(current_version=True)):
			change_core_elements_to_slots(frame_object)
			if not nr%250:
				print(nr)

		return render(request, "annotate/admin_functions.html")
	return render(request, "annotate/introduction.html")


#@login_required(login_url="login")
def get_sentence_ids(file_frames):
	"""
	No request function. Get ids of the sentences of the inserted frames and return them if they are not inserted in
	the database so far.
	:param file_frames: path to frame file
	:return: sentence ids which are not in database
	"""
	with open(file_frames, encoding="utf-8") as f:
		content = f.readlines()

	sentence_ids = dict()
	sentence_counter = 0
	if len(content[0].strip().split(" ")[0]) >= 3 and content[0].strip().split(" ")[0].startswith("#"):
		for line in content:
			split_line = line.strip().split(" ")
			sentence_id = split_line[0][1:]
			if not Sentence.objects.filter(sentence_id__exact=sentence_id):
				sentence_ids[sentence_id] = False
			else:
				sentence_counter += 1
	if sentence_counter == len(content):
		return sentence_ids

	return sentence_ids


@login_required(login_url="login")
def insert_frames(request):
	"""
	Superuser function. Insert frames into database. In frontend a file with frames can be selected which will be
	saved in database. Old frames can be deleted before. Check if sentences are already in database or
	have to be inserted before. If insertion was successfull superuser will redirected to assign users.
	:param request: frontend request to insert new frames
	:return: show upload form, if request data exist, load frames to database
	"""
	if request.user.is_superuser:
		if request.method == "POST" and request.FILES["frame_file"]:
			frame_file = request.FILES["frame_file"]
			drop_frames = request.POST.get("drop_frames")
			if not drop_frames:
				drop_frames = False
			else:
				drop_frames = True
			print(drop_frames)
			fs = FileSystemStorage()
			filename = fs.save(frame_file.name, frame_file)
			uploaded_file_url = fs.url(filename)
			#sentence_ids = get_sentence_ids("upload/"+str(uploaded_file_url))
			#if not sentence_ids:
			#	return render(request, "annotate/upload_frames.html", {"error":"wrong file format"})
			base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			with open(os.path.join(base_dir, "data/parameters.json")) as f:
				parameter = json.load(f)
			frames_count, list_added, list_wrong_id = read_frames_to_db(os.path.join(base_dir,"upload/"+str(uploaded_file_url)), delete_previous=drop_frames, position_starting_at_zero=parameter["parameters"]["position_starting_at_zero"])
			#print(frames_count, list_wrong_id)
			if len(frames_count) != 0 and len(list_wrong_id) != 0:
				return render(request, "annotate/upload_frames.html", {"error": "something went wrong with the input file. The frames in the following lines were already in the database:"+ ",".join([str(linenr) for linenr in frames_count])+" and the records in the following lines have a wrong verb position: "+ ",".join([str(linenr) for linenr in list_wrong_id])})
			elif len(frames_count) != 0:
				return render(request, "annotate/upload_frames.html", {"error": "something went wrong with the input file. The frames in the following lines were already in the database:"+ ",".join([str(linenr) for linenr in frames_count])})
			elif len(list_wrong_id) != 0:
				return render(request, "annotate/upload_frames.html", {"error": "something went wrong with the input file. The records in the following lines have a wrong verb position: "+ ",".join([str(linenr) for linenr in list_wrong_id])})
			#request.session["added_frames"] = list_added
			return redirect("assign_users")
		return render(request, "annotate/upload_frames.html")
	return render(request, "annotate/introduction.html")


@login_required(login_url="login")
def insert_framenet_files(request):
	"""
	:param request: frontend request to insert FrameNet data. Path to FrameNet data is hard coded. The button click
	starts the process directly.
	:return: template, if inserted back to admin functions
	"""
	if request.user.is_superuser:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		frame_xml_path = os.path.join(base_dir,"fndata-1.7/frame/")
		read_frame_xml_files(frame_xml_path)
		return render(request, "annotate/admin_functions.html")
	return render(request, "annotate/introduction.html")


@login_required(login_url="login")
def add_non_corelements_to_db(request):
	"""
	add non corelelement types and core unexpressed to the database.
	Only needed if database was filled with core elements only
	"""
	if request.user.is_superuser:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		frame_xml_path = os.path.join(base_dir,"fndata-1.7/frame/")
		read_frame_xml_files(frame_xml_path, add_non_core=True)
		return render(request, "annotate/admin_functions.html")
	return render(request, "annotate/introduction.html")



@login_required(login_url="login")
def add_synonyms(request):
	if request.user.is_superuser:
		if request.method == "POST" and request.FILES["synonym_file"]:
			synonyms_file = request.FILES["synonym_file"]
			print(synonyms_file)
			fs = FileSystemStorage()
			filename = fs.save(synonyms_file.name, synonyms_file)
			uploaded_file_url = fs.url(filename)
			base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			with open(os.path.join(base_dir,"upload/"+str(uploaded_file_url)), encoding="utf-8") as synonyms_file:
				content = synonyms_file.readlines()
			for line in content:
				splitted_line = line.strip().split(" ")
				verb = splitted_line[0]
				synonyms = splitted_line[1:]
				for synonym in synonyms:
					lexunit_ids = [str(xml_id) for xml_id in LexicalUnits.objects.filter(verb=synonym+".v", xml_id__isnull=False).values_list("xml_id", flat=True)]
					if len(lexunit_ids) > 0:
						#print(verb, synonym, ";".join(lexunit_ids))
						new_synonym = Synonyms(verb=verb+".v", synonym=synonym+".v", xml_ids=";".join(lexunit_ids))
					else:
						new_synonym = Synonyms(verb=verb + ".v", synonym=synonym + ".v")
						#print(verb, synonym)
					new_synonym.save()

			return render(request, "annotate/add_synonyms.html", {"success": "All synonyms added."})
		return render(request, "annotate/add_synonyms.html")
	else:
		return render(request, "annotate/introduction.html")


@login_required(login_url="login")
def add_role_labels(request):
	if request.user.is_superuser:
		if request.method == "POST" and request.FILES["role_file"]:
			role_file = request.FILES["role_file"]
			print(role_file)
			fs = FileSystemStorage()
			filename = fs.save(role_file.name, role_file)
			uploaded_file_url = fs.url(filename)
			base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			with open(os.path.join(base_dir,"upload/"+str(uploaded_file_url)), encoding="utf-8") as role_file:
				content = role_file.readlines()
			for line in content:
				splitted_line = line.strip().split(" ")
				sentence_id = int(splitted_line[0][1:])
				head_position = int(splitted_line[1])+1
				head = splitted_line[2]
				frames = Frame.objects.filter(sentence_id=sentence_id, position=head_position, current_version=True)
				#print(sentence_id, head_position, frames)
				if len(splitted_line) > 3:
					for slot in splitted_line[3:]:
						splitted_slot = slot.split("-:-")
						token = splitted_slot[0]
						token_position = int(splitted_slot[1]) +1
						semantic_role = splitted_slot[2]
						for frame in frames:
							for slot in frame.slot_element.all():
								if slot.role_label == None:
									if slot.component_type == "token":
										token = Token.objects.get(id=slot.id_of_token)
										if token_position == token.position:
											#print(frame.id, sentence_id, token.lemma, semantic_role)
											slot.role_label = semantic_role
											slot.save(update_fields=["role_label"])
									else:
										mwe = MWE.objects.get(id=slot.id_of_mwe)
										for token in mwe.components.all():
											if token.position == token_position:
												#print(frame.id, "MWE", sentence_id, token.lemma, semantic_role)
												slot.role_label = semantic_role
												slot.save(update_fields=["role_label"])
						#print(sentence_id, head_position, token, semantic_role)
			return render(request, "annotate/add_semantic_roles.html", {"success": "All role labels added."})
		return render(request, "annotate/add_semantic_roles.html")
	else:
		return render(request, "annotate/introduction.html")

@login_required(login_url="login")
def add_semantic_role_table(request):
	"""add new role labels to table or change labels through delete all and read file again."""
	if request.user.is_superuser:
		if request.method == "POST":
			print(request.POST.get("delete_previous"))
			if request.POST.get("delete_previous"):
				SemanticRoles.objects.all().delete()
			role_file = request.FILES["role_file"]
			print(role_file)
			fs = FileSystemStorage()
			filename = fs.save(role_file.name, role_file)
			uploaded_file_url = fs.url(filename)
			base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			with open(os.path.join(base_dir,"upload/" + str(uploaded_file_url)), encoding="utf-8") as role_file:
				content = role_file.readlines()
			for nr, line in enumerate(content):
				if line.startswith("|") and nr > 3:
					line = line.strip()
					columns = line.split("|")
					if columns[1].strip() not in SemanticRoles.objects.all().values_list("name", flat=True):
						new_role = SemanticRoles(name=columns[1].strip(), definition=columns[2].strip())
						new_role.save()
			return render(request, "annotate/add_semantic_roles.html", {"success": "All role labels added."})
		return render(request, "annotate/change_semantic_roles.html")
	else:
		return render(request, "annotate/introduction.html")



def read_sentences_to_db(content, sentence_ids, filename):
	"""
		reads the sentences of the frame file which are not inserted so far to the database. All lines of the file in
		conllu format will be interated. A sentence object will be build if all tokens of it was appended to a list and
		when a new id was found. A token object will be created for each line of the file which is not empty or don"t
		start with a hash. A sentence object includes the id and a manytomany relation to the tokens.
		The tokens include the position, wordform, lemma and dependency relations.
		:param file_sentences_st: sentence file stanford
		:param file_psd: sentence file psd
		:param sentence_ids: ids of the sentences which are not inserted in the database so far
		:return: list of sentence objects
	"""
	sentence_list = list()
	sentence_id = ""
	token_list = list()
	sentence_id_keys = sentence_ids.keys()


	for nr, line in enumerate(content):
		if line[0] == "#":

			if sentence_id != "" and len(token_list) != 0:
				# add sentence to database if the full sentence was read
				sentence = Sentence(sentence_id=sentence_id)
				sentence.save()
				for token in token_list:
					sentence.token.add(token)
					sentence.save()
				#print(sentence.token.all())
				sentence_list.append(sentence)
				sentence_ids[sentence_id] = True
			sentence_id = line[1:].strip()
			if sentence_id in sentence_id_keys and sentence_ids[sentence_id] == False:
				#print(sentence_id)
				token_list = list()
			else:
				sentence_id = ""

		elif line != "\n" and sentence_id != "":
			line = line.strip().split("\t")
			token = Token(position=line[0], word_form=line[1], lemma=line[2], dep_nr=line[6], dep_rel=line[7],
						  sentence_id=sentence_id)
			token.save()
			token_list.append(token)
		if not nr%1000:
			print("lines from file:", nr, len(content), "sentences_from ids", len(sentence_list), len(sentence_id_keys),
				  filename)
	if sentence_id != "" and len(token_list) != 0:
		# add sentence to database if the full sentence was read
		sentence = Sentence(sentence_id=sentence_id)
		sentence.save()
		for token in token_list:
			sentence.token.add(token)
			sentence.save()
		# print(sentence.token.all())
		sentence_list.append(sentence)
		sentence_ids[sentence_id] = True
	return sentence_list


def increase_mwu(string_position):
	return "_".join([str(int(value) + 1) for value in string_position.split('_')])


def increase_position_by_one(content_lines):
	"""
		if the positions of the tokens and core elements in the file starts with 0 instead of 1, all ids will be
		increased by 1.
		:return: new content with increased ids.
	"""
	new_content = list()
	for nr, line in enumerate(content_lines):
		current_line = line.strip().split(" ")
		sentence_id = current_line[0][1:]
		frame = current_line[2].split(".")
		#content_lines[nr][3:]
		if "_" in current_line[1]:
			increased_values = increase_mwu(current_line[1])
			new_line = [current_line[0], increased_values, frame[0] + "." + frame[1]]
		else:
			new_line = [current_line[0], str(int(current_line[1])+1), frame[0] + "." + frame[1]]
		for slot in current_line[3:]:
			slot_parts = slot.split(":")
			if "_" in slot_parts[1].split("-")[1]:
				position = increase_mwu(slot_parts[1].split("-")[1])
			else:
				position = str(int(slot_parts[1].split("-")[1]) + 1)
			word = slot_parts[0]
			if word == "$NUMBER$-":
				word = Sentence.objects.get(sentence_id=sentence_id).token.get(position=position).word_form
			slot_type = slot_parts[-1]
			new_line.append(":".join([word, "-"+position+"-", slot_type]))
		new_line.append("\n")
		new_content.append(" ".join(new_line))
	return new_content


def read_frames_to_db(file_frames, delete_previous=False, position_starting_at_zero = True):
	"""
	reads the content of file_frames. If delere_previous all previous frames will be deleted, otherwise not.
	if frame name has numbers instead of letters, the file will be encoded.
	if the positions of the core elements starting with 0 instead of 1, they will be increased.
	it will be checjed whether the sentence of the new frame is already in the database or not and in case it will added.
	the frames (on frame in each sentence, sentence id, verb lemma, position and core elements splitted with a blank)
	will be inserted in the database. Each frame get an object with values of sentence_id, position, verb lemma,
	used time, and default values like current version = True and annotated = False. The core elements get an own object
	with values like slot type, position and word form. They will be assigned to the frame types with a manytomany
	relation.
	:param file_frames: selected file names with frames
	:param delete_previous: boolean to decide if previous data should be deleted or not
	:param position_starting_at_zero: boolean if ids of core element positions in the file starts with 0
	:return: integer of missing sentences to assign the frames
	"""

	# delete old frames
	if delete_previous:
		Frame.objects.all().delete()
		Slot.objects.all().delete()
		MWE.objects.all().delete()
		Slot.objects.all().delete()

	# add file format control here
	with open(file_frames, encoding="utf-8") as input_file:
		content = input_file.readlines()

	if position_starting_at_zero:
		# increase position (already implemented in decode frames)
		content = increase_position_by_one(content)

	# insert sentence if not in db
	sentence_ids = get_sentence_ids(file_frames)
	if len(sentence_ids) > 0:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		with open(os.path.join(base_dir, "data/parameters.json")) as f:
			parameter = json.load(f)
		for file_name in parameter["parameters"]["sentence_files"]:
			file_sentences = os.path.join(base_dir, file_name)
			with open(file_sentences, encoding="utf-8") as input_file:
				sentence_content = input_file.readlines()
			read_sentences_to_db(sentence_content, sentence_ids, file_name)

	count_missing_sent = 0
	count_present_sent = 0
	list_doubel = list()
	list_wrong_id = list()
	list_added = list()
	for nr, line in enumerate(content):
		print(line)
		line = line.strip().split(" ")
		sentence_identifier = line[0][1:]
		frame = line[2].split(".")
		verb_ids = ""
		if len(Sentence.objects.get(sentence_id__exact=sentence_identifier).token.filter(position=line[1])) == 1 and frame[0] != Sentence.objects.get(sentence_id__exact=sentence_identifier).token.get(position=line[1]).lemma:
			list_wrong_id.append(nr + 1)
			continue
		#	pass
		for verb in LexicalUnits.objects.filter(verb=frame[0]+".v"):
			verb_ids += str(verb.xml_id)+";"
		check_if_frame_exist = Frame.objects.filter(id_of_sentence=sentence_identifier, position=line[1])
		if len(check_if_frame_exist) == 0:
			if "_" in frame[0]:
				verb_split = frame[0].split('_')
				position = line[1].replace("_", "-")
				frame_object = Frame(id_of_sentence=sentence_identifier, position=position, verb_lemma=verb_split[0],
							 verb_ids=verb_ids, f_type=frame[1], user="admin", verb_addition='_'+'_'.join(verb_split[1:]),
							 sentence=Sentence.objects.get(sentence_id__exact=sentence_identifier), annotated=False)
				frame_object.save()
				mwu = create_mwu(position.split('-'), sentence_identifier, "vmwe")
				frame_object.mwe.add(mwu)
				frame_object.save()
			else:
				frame_object = Frame(id_of_sentence=sentence_identifier, position=line[1], verb_lemma=frame[0],
									 verb_ids=verb_ids, f_type=frame[1], user="admin",
									 sentence=Sentence.objects.get(sentence_id__exact=sentence_identifier),
									 annotated=False)
			frame_object.save()
			list_added.append(frame_object.id)
			# add sentence and core elements
			for core_nr, element in enumerate(line[3:]):
				parts_of_element = element.split("-:-")
				# @todo: use coreleementtype model instead of slottype string
				# buy_up-:-8_9-:-Action
				slot_ids = parts_of_element[1]
				slot_values = parts_of_element[0]
				if '_' in slot_ids:
					mwu = create_mwu(slot_ids.split('_'), sentence_identifier, frame_object)
					frame_object.mwe.add(mwu)
					frame_object.save()
					core_element = create_slot(mwu.id, "mwe", parts_of_element[2])
				else:
					token_id = Token.objects.get(sentence_id=sentence_identifier, position=slot_ids).id
					#core_element = Slot(id_of_token=token.id, component_type="token", core_element_type=parts_of_element[2])
					core_element = create_slot(token_id, "token", parts_of_element[2])

				if not Sentence.objects.filter(sentence_id=sentence_identifier):
					count_missing_sent += 1
					print("sentence_missing")
				else:
					count_present_sent += 1
					frame_object.slot_element.add(core_element)
					frame_object.save()
		else:
			unannotated_frames = Frame.objects.filter(id_of_sentence=sentence_identifier, verb_lemma=frame[0], position=line[1], current_version=True, annotation_state=0, annotated = False, skipped = False)
			changed_frame_type = False
			for frame_object in unannotated_frames:
				if frame_object.f_type != frame[1]:
					changed_frame_type = True
					frame_object.f_type = frame[1]
					for fe in frame_object.slot_element.all():
						frame_object.slot_element.remove(fe)
					frame_object.save(update_fields=["f_type"])
					for core_nr, element in enumerate(line[3:]):
						parts_of_element = element.split("-:-")
						token = Token.objects.get(sentence_id=sentence_identifier, position=parts_of_element[1])
						core_element = create_slot(token.id, "token", parts_of_element[2])
						core_element.save()
						if not Sentence.objects.filter(sentence_id=sentence_identifier):
							count_missing_sent += 1
							print("sentence_missing")
						else:
							count_present_sent += 1
							frame_object.slot_element.add(core_element)
							frame_object.save()
			if not changed_frame_type:
				list_doubel.append(nr+1)
		if not nr%250:
			print("read frames", nr, "of", len(content))
	print(count_missing_sent, "missing of ", len(content), round(count_missing_sent/len(content), 2)*100)

	return list_doubel, list_added, list_wrong_id


def create_mwu(slot_ids, sent_id, type=None):
	if type == "vmwe":
		new_mwe_object = MWE(mwe_verb=True)
	else:
		new_mwe_object = MWE()
	new_mwe_object.save()
	for slot_id in slot_ids:
		token = Token.objects.get(sentence_id=sent_id, position=slot_id)
		new_mwe_object.components.add(token)
		new_mwe_object.save()
	return new_mwe_object

def create_slot(id, component_type, fe_type):
	if component_type == "token":
		core_element = Slot(id_of_token=id, component_type=component_type, core_element_type=fe_type)

	else:
		core_element = Slot(id_of_mwe=id, component_type=component_type, core_element_type=fe_type)
	core_element.save()
	return core_element

def read_frame_xml_files(directory_path, add_non_core=False):
	"""
	no request function. Load all lexical units and framenet types of FrameNet into the database.
	FrameType objects will be created and all assigend Lexical Units and Core Element Types will be added. Creates
	the base of the system, the seelction of the frame type and the slot types will be based on this data.
	The FrameType and slot types will be enriched with defintions, xml ids and their names.
	:param directory_path: path to the framenet data.
	"""
	for nr, filename in enumerate(sorted(os.listdir(directory_path))):
		if filename.endswith("xml"):
			non_lexicalized = False
			print(nr, len(os.listdir(directory_path)))
			root = xml.etree.ElementTree.parse(directory_path+filename).getroot()
			if len(FrameType.objects.filter(name=root.attrib["name"], xml_id=root.attrib["ID"])) == 1:
				new_frame_type = FrameType.objects.get(name=root.attrib["name"], xml_id=root.attrib["ID"])
			elif len(FrameType.objects.filter(name=root.attrib["name"], xml_id=root.attrib["ID"])) == 0:
				new_frame_type = FrameType(name=root.attrib["name"], xml_id=root.attrib["ID"])
				new_frame_type.save()
			else:
				print("more than one frame type with id and name", root.attrib["name"], root.attrib["ID"])
			for child in root:
				if child.tag == "{http://framenet.icsi.berkeley.edu}semType" and (child.attrib[
					"name"] == "Non-Lexical Frame"):
					non_lexicalized = True
				if add_non_core:
					if child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib["coreType"] == "Core-Unexpressed" and non_lexicalized == False:
						if len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) > 0:
							print("doublicate id", child.attrib["name"], child.attrib["ID"])
						else:
							new_core_element_type = CoreElementType(name=child.attrib["name"], xml_id=child.attrib["ID"], core_type="core_unexpressed")
							new_core_element_type.save()
							for childchild in child:
								if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
									new_core_element_type.definition = re.sub("<[^<]+?>", "", childchild.text)
									new_core_element_type.save()
							new_frame_type.core_types.add(new_core_element_type)
							new_frame_type.save()
					if child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib["coreType"] != "Core-Unexpressed" and child.attrib["coreType"] != "Core" and non_lexicalized == False:
						if len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) > 0:
							pass
						else:
							new_core_element_type = CoreElementType(name=child.attrib["name"], xml_id=child.attrib["ID"], core_type="non_core")
							new_core_element_type.save()
							for childchild in child:
								if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
									new_core_element_type.definition = re.sub("<[^<]+?>", "", childchild.text)
									new_core_element_type.save()
							new_frame_type.core_types.add(new_core_element_type)
							new_frame_type.save()
				else:
					if child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib["coreType"] == "Core" and non_lexicalized == False:
						if len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) > 0:
							pass
						else:
							new_core_element_type = CoreElementType(name=child.attrib["name"], xml_id=child.attrib["ID"], core_type="core")
							new_core_element_type.save()
							for childchild in child:
								if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
									new_core_element_type.definition = re.sub("<[^<]+?>", "", childchild.text)
									new_core_element_type.save()
							new_frame_type.core_types.add(new_core_element_type)
							new_frame_type.save()
					elif child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib["coreType"] == "Core-Unexpressed" and non_lexicalized == False:
						if len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) > 0:
							print("doublicate id", child.attrib["name"], child.attrib["ID"])
						else:
							new_core_element_type = CoreElementType(name=child.attrib["name"], xml_id=child.attrib["ID"], core_type="core_unexpressed")
							new_core_element_type.save()
							for childchild in child:
								if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
									new_core_element_type.definition = re.sub("<[^<]+?>", "", childchild.text)
									new_core_element_type.save()
							new_frame_type.core_types.add(new_core_element_type)
							new_frame_type.save()
					elif child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib["coreType"] != "Core-Unexpressed" and child.attrib["coreType"] != "Core" and non_lexicalized == False:
						if len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) > 0:
							pass
						else:
							new_core_element_type = CoreElementType(name=child.attrib["name"], xml_id=child.attrib["ID"], core_type="non_core")
							new_core_element_type.save()
							for childchild in child:
								if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
									new_core_element_type.definition = re.sub("<[^<]+?>", "", childchild.text)
									new_core_element_type.save()
							new_frame_type.core_types.add(new_core_element_type)
							new_frame_type.save()
					elif child.tag == "{http://framenet.icsi.berkeley.edu}lexUnit" and child.attrib["POS"] == "V" and non_lexicalized == False:
						#print(child.attrib["name"])
						if len(LexicalUnits.objects.filter(verb=child.attrib["name"], xml_id=child.attrib["ID"])) > 0:
							pass
						else:
							new_lexical_unit = LexicalUnits(verb=child.attrib["name"], xml_id=child.attrib["ID"])
							new_lexical_unit.save()
							new_frame_type.lexUnits.add(new_lexical_unit)
							new_frame_type.save()
	return 0



@login_required(login_url="login")
def insert_missing_frames(request):
	if request.user.is_superuser:
		base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		with open(os.path.join(base_dir,"data/frame-list-valid.txt"), encoding="utf-8") as f:
			content = f.readlines()
		frame_type_list = list()
		for nr, line in enumerate(content):
			if nr != 0:
				frametype = line.split("\t")[0]
				if frametype not in FrameType.objects.filter(new_custom_value=0).values_list("name", flat=True):
					frame_type_list.append(frametype)
					#child.attrib["name"] == "Non-perspectivalized_frame")
		print(frame_type_list)
		for frame_type in frame_type_list:
			non_lexicalized = False
			base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			root = xml.etree.ElementTree.parse(os.path.join(base_dir,"fndata-1.7/frame/" + frame_type+".xml")).getroot()
			if len(FrameType.objects.filter(name=root.attrib["name"], xml_id=root.attrib["ID"])) == 1:
				new_frame_type = FrameType.objects.get(name=root.attrib["name"], xml_id=root.attrib["ID"])
			elif len(FrameType.objects.filter(name=root.attrib["name"], xml_id=root.attrib["ID"])) == 0:
				new_frame_type = FrameType(name=root.attrib["name"], xml_id=root.attrib["ID"])
				new_frame_type.save()
			else:
				print("more than one frame type with id and name", root.attrib["name"], root.attrib["ID"])
				raise LookupError
			for child in root:
				if child.tag == "{http://framenet.icsi.berkeley.edu}semType" and (child.attrib["name"] == "Non-Lexical Frame"):
					non_lexicalized = True

				if child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib[
					"coreType"] == "Core" and non_lexicalized == False:
					if len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) == 1:
						new_core_element_type = CoreElementType.objects.get(name=child.attrib["name"], xml_id=child.attrib["ID"])
						new_frame_type.core_types.add(new_core_element_type)
						new_frame_type.save()
					elif len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) == 0:
						new_core_element_type = CoreElementType(name=child.attrib["name"], xml_id=child.attrib["ID"],
																core_type="core")
						new_core_element_type.save()
						for childchild in child:
							if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
								new_core_element_type.definition = re.sub("<[^<]+?>", "", childchild.text)
								new_core_element_type.save()
						new_frame_type.core_types.add(new_core_element_type)
						new_frame_type.save()
				elif child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib[
					"coreType"] == "Core-Unexpressed" and non_lexicalized == False:
					if len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) == 1:
						new_core_element_type = CoreElementType.objects.get(name=child.attrib["name"], xml_id=child.attrib["ID"])
						new_frame_type.core_types.add(new_core_element_type)
						new_frame_type.save()
					elif len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) == 0:
						new_core_element_type = CoreElementType(name=child.attrib["name"], xml_id=child.attrib["ID"],
																core_type="core_unexpressed")
						new_core_element_type.save()
						for childchild in child:
							if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
								new_core_element_type.definition = re.sub("<[^<]+?>", "", childchild.text)
								new_core_element_type.save()
						new_frame_type.core_types.add(new_core_element_type)
						new_frame_type.save()
				elif child.tag == "{http://framenet.icsi.berkeley.edu}FE" and child.attrib[
					"coreType"] != "Core-Unexpressed" and child.attrib["coreType"] != "Core" and non_lexicalized == False:
					if len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) == 1:
						new_core_element_type = CoreElementType.objects.get(name=child.attrib["name"], xml_id=child.attrib["ID"])
						new_frame_type.core_types.add(new_core_element_type)
						new_frame_type.save()
					elif len(CoreElementType.objects.filter(name=child.attrib["name"], xml_id=child.attrib["ID"])) == 0:
						new_core_element_type = CoreElementType(name=child.attrib["name"], xml_id=child.attrib["ID"],
																core_type="non_core")
						new_core_element_type.save()
						for childchild in child:
							if childchild.tag == "{http://framenet.icsi.berkeley.edu}definition":
								new_core_element_type.definition = re.sub("<[^<]+?>", "", childchild.text)
								new_core_element_type.save()
						new_frame_type.core_types.add(new_core_element_type)
						new_frame_type.save()
				elif child.tag == "{http://framenet.icsi.berkeley.edu}lexUnit" and child.attrib[
					"POS"] == "V" and non_lexicalized == False:
					# print(child.attrib["name"])
					if len(LexicalUnits.objects.filter(verb=child.attrib["name"], xml_id=child.attrib["ID"])) == 1:
						new_lexical_unit = LexicalUnits.objects.get(verb=child.attrib["name"], xml_id=child.attrib["ID"])
						new_frame_type.lexUnits.add(new_lexical_unit)
						new_frame_type.save()
					elif len(LexicalUnits.objects.filter(verb=child.attrib["name"], xml_id=child.attrib["ID"])) == 0:
						new_lexical_unit = LexicalUnits(verb=child.attrib["name"], xml_id=child.attrib["ID"])
						new_lexical_unit.save()
						new_frame_type.lexUnits.add(new_lexical_unit)
						new_frame_type.save()
		return render(request, "annotate/admin_functions.html")
	else:
		return render(request, "annotate/introduction.html")

@login_required
def frame_definition(request):
	""" frontend request to show the local stored xml file. not in use at the moment.
	"""
	frame_name = request.path_info[18:]
	#with open("fndata-1.7/frame/"+frame_name+".xml") as f:
	#	xml_content = f.read()
	#return HttpResponse(xml_content) #, content_type="text/xml")
	#return render(request, "fndata-1.7/frame/"+frame_name+".xml")
	response = render_to_response("fndata-1.7/frame/"+frame_name+".xml")
	response["Content-Type"] = "application/xml;"
	return response


@login_required(login_url="login")
def set_annotation_settings(request):
	if request.user.is_superuser:
		annotation_settings = AnnotationSettings.objects.get(id=1)
		if request.method == "POST":
			element_type = request.POST.get("add_custom_element_types")
			frame_type = request.POST.get("add_custom_frame_types")
			if element_type:
				annotation_settings.custom_element_type = True
			else:
				annotation_settings.custom_element_type = False
			if frame_type:
				annotation_settings.custom_frame_type = True
			else:
				annotation_settings.custom_frame_type = False
			annotation_settings.save()
			print(element_type, frame_type)
			return render(request, "annotate/admin_functions.html")

		else:
			return render(request, "annotate/set_settings.html", {"custom_element_type": annotation_settings.custom_element_type, "custom_frame_type": annotation_settings.custom_frame_type})

	return render(request, "annotate/introduction.html")


@login_required(login_url="login")
def assign_users_frames(request):
	"""
	:param request: frontend request to assign users to frames. User and frames can be selected in frontend.
					In the backend the assigend user will be changed in the database.
	:return: form to select frames and user for assiging process.
	"""
	if request.user.is_superuser:
		if request.method == "POST":
			selected_frames_verb = request.POST.getlist("frame_selection_verb")
			selected_frames_type = request.POST.getlist("frame_selection_type")
			selected_frames_date = request.POST.getlist("frame_selection_date")
			selected_frames_not_assigned = request.POST.getlist("frame_selection_not_assigned")
			if selected_frames_type and not selected_frames_verb and not selected_frames_date and not selected_frames_not_assigned:
				selected_frames = selected_frames_type
			elif selected_frames_verb and not selected_frames_type and not selected_frames_date and not selected_frames_not_assigned:
				selected_frames = selected_frames_verb
			elif selected_frames_date and not selected_frames_type and not selected_frames_verb and not selected_frames_not_assigned:
				selected_frames = selected_frames_date
			elif selected_frames_not_assigned and not selected_frames_date and not selected_frames_type and not selected_frames_verb:
				selected_frames = selected_frames_not_assigned
			else:
				assigned_frames = set()
				for frame in Frame.objects.filter(Q(current_version=True), ~Q(user="admin")):
					assigned_frames.add(str(frame.id_of_sentence) + "_" + str(frame.position) + "_" + frame.verb_lemma)
				not_assigned_frames = list()
				for frame_object in Frame.objects.filter(current_version=True):
					if str(frame_object.id_of_sentence) + "_" + str(
							frame_object.position) + "_" + frame_object.verb_lemma not in assigned_frames:
						not_assigned_frames.append(frame_object)
				not_assigned_frames = sorted(not_assigned_frames, key=lambda x: (x.f_type, x.verb_lemma))

				return render(request, "annotate/assign_users.html", {"success": "Not assigned because no frame record or a frame record of more than one columns were selected.", "frame_list_verb": Frame.objects.filter(current_version=True, annotated=False,
													 				user="admin", annotation_state=0).order_by("verb_lemma"),
					   												"frame_list_type": Frame.objects.filter(current_version=True, annotated=False,
															   user="admin", annotation_state=0).order_by("f_type"),
																  "user_list": User.objects.all().values_list(
																	  "username", flat=True), "frame_list_date": Frame.objects.filter(current_version=True, annotated=False,
															   user="admin", annotation_state=0).order_by("-timestamp"),
																	  "frame_list_not_assigned":not_assigned_frames})
			user = request.POST.get("user_selection")
			not_assigned_someoneelse = request.POST.get("not_assigned_frames")
			assigned_frames = set()
			if not_assigned_someoneelse:
				for frame in Frame.objects.filter(Q(current_version=True),~Q(user="admin")):
					assigned_frames.add(str(frame.id_of_sentence) + "_" + str(frame.position) + "_" + frame.verb_lemma)
			else:
				for frame in Frame.objects.filter(current_version=True, user=user):
					assigned_frames.add(str(frame.id_of_sentence)+"_"+str(frame.position)+"_"+ frame.verb_lemma)
			nr_assigned = 0
			list_assigned = list()
			for frame_object in Frame.objects.filter(id__in=selected_frames):
				if str(frame_object.id_of_sentence)+"_"+str(frame_object.position)+"_"+ frame_object.verb_lemma not in assigned_frames:
					new_frame = copy_frame(frame_object, user=user, annotation_state=0, description="frame assigned to user")
					nr_assigned += 1
					list_assigned.append(frame_object.verb_lemma+ " "+str(frame_object.id_of_sentence)+":"+str(frame_object.position))

			assigned_frames = set()
			for frame in Frame.objects.filter(Q(current_version=True), ~Q(user="admin")):
				assigned_frames.add(str(frame.id_of_sentence) + "_" + str(frame.position) + "_" + frame.verb_lemma)
			not_assigned_frames = list()
			for frame_object in Frame.objects.filter(current_version=True):
				if str(frame_object.id_of_sentence) + "_" + str(
						frame_object.position) + "_" + frame_object.verb_lemma not in assigned_frames:
					not_assigned_frames.append(frame_object)
			not_assigned_frames = sorted(not_assigned_frames, key=lambda x: (x.f_type, x.verb_lemma))

			return render(request, "annotate/assign_users.html", {"success": str(nr_assigned)+" of selected " + str(len(selected_frames))+" frames assigned to " + user + ". ",
																  "frame_list_verb": Frame.objects.filter(current_version=True, annotated=False,
													 				user="admin", annotation_state=0).order_by("verb_lemma"),
					   												"frame_list_type": Frame.objects.filter(current_version=True, annotated=False,
															   user="admin", annotation_state=0).order_by("f_type"), "frame_list_date": Frame.objects.filter(current_version=True, annotated=False,
															   user="admin", annotation_state=0).order_by("-timestamp"),
																  "user_list": User.objects.all().values_list(
																	  "username", flat=True), "assigned_frames": list_assigned,
																  "frame_list_not_assigned": not_assigned_frames})

		assigned_frames = set()
		for frame in Frame.objects.filter(Q(current_version=True), ~Q(user="admin")):
			assigned_frames.add(str(frame.id_of_sentence) + "_" + str(frame.position) + "_" + frame.verb_lemma)
		not_assigned_frames = list()
		for frame_object in Frame.objects.filter(current_version=True):
			if str(frame_object.id_of_sentence) + "_" + str(
					frame_object.position) + "_" + frame_object.verb_lemma not in assigned_frames:
				not_assigned_frames.append(frame_object)
		not_assigned_frames = sorted(not_assigned_frames, key=lambda x: (x.f_type, x.verb_lemma))

		return render(request, "annotate/assign_users.html",
					  {"frame_list_verb": Frame.objects.filter(current_version=True, annotated=False,
													 user="admin", annotation_state=0).order_by("verb_lemma"),
					   "frame_list_type": Frame.objects.filter(current_version=True, annotated=False,
															   user="admin", annotation_state=0).order_by("f_type"),
					"frame_list_date": Frame.objects.filter(current_version=True, annotated=False,
															   user="admin", annotation_state=0).order_by("-timestamp"),
					   "frame_list_not_assigned": not_assigned_frames,
					   "user_list": User.objects.all().values_list("username", flat=True), "success":None})
	else:
		return render(request, "annotate/introduction.html")


##########################
### export databse ###
##########################


@login_required(login_url="login")
def export_database(request):
	"""
		Frontend request to export selected frames to a textfile. Different selection options like user, frame name, ...
		List the current version of the annotation of all selected frames.
		:param request: frontend request to export frames of the database.
		:return: text file with selected frame.
	"""
	# create directory
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	if not os.path.isdir(os.path.join(base_dir,"data/export")):
		os.makedirs(os.path.join(base_dir,"data/export"))
	if request.user.is_superuser:
		if request.method == "POST":
			selected_frames = Frame.objects.filter(current_version=True).order_by("sentence_id")
			if request.POST.get("annotated_frames") and request.POST.get("not_annotated_frames"):
				selected_frames = selected_frames
			elif request.POST.get("annotated_frames"):
				annotated_frames = Frame.objects.filter(annotated=True, skipped=False, annotation_state=5)
				selected_frames = selected_frames & annotated_frames
			elif request.POST.get("not_annotated_frames"):
				not_annotated_frames = Frame.objects.filter(annotated=False)
				selected_frames = selected_frames & not_annotated_frames
			if request.POST.get("frames_with_comments"):
				commented_frames = Frame.objects.filter(comment__isnull=False)
				selected_frames = selected_frames & commented_frames

			user_selection = request.POST.getlist("user_selection")
			frame_type_selection = request.POST.getlist("frametype_selection")
			verb_selection = request.POST.getlist("verb_selection")
			if user_selection:
				user_selection_frames = Frame.objects.filter(user__in=user_selection)
				selected_frames = selected_frames & user_selection_frames
			if frame_type_selection:
				frame_type_frames = Frame.objects.filter(f_type__in=frame_type_selection)
				selected_frames = selected_frames & frame_type_frames
			if verb_selection:
				verb_type_frames = Frame.objects.filter(verb_lemma__in=verb_selection)
				selected_frames = selected_frames & verb_type_frames
			count_changes = request.POST.get("count_changes")
			time_per_frame = request.POST.get("time_per_frame")
			print(len(selected_frames))

			frame_file_content = []
			mwe_file_content = []
			semantic_role_file_content = []
			coercions_file_content = []
			metadata_file_content = []
			comment_file_content = []
			task_1_file_content = []
			task_2_2_file_content = []
			if len(selected_frames) > 0:
				frame_output = ""
				for frame_nr, frame in enumerate(selected_frames):
					frame_output = str(frame)
					mwe_output = ""
					semantic_role_output = ""
					coercions_output = ""
					frame_position = str(frame.position).replace("-", "_")
					output = "#"+str(frame.sentence_id) + " " + frame_position + " " + frame.verb_lemma+frame.verb_addition
					task_1 = output + "."+frame.f_type+"\n"
					sentence = " ".join(Sentence.objects.get(sentence_id=frame.sentence_id).token.values_list("word_form", flat=True))
					used_time = Frame.objects.filter(sentence_id=frame.sentence_id, user=frame.user, position=frame.position, verb_lemma=frame.verb_lemma).values_list("used_time", flat=True)
					# todo: check this! time for adding mwe and core elements is part of used time of a step. usefull for calculating time per step and time per change, but can"t sum
					metadata_output = output + " "+ str(frame.id) + " " +frame.user  + " " + str(frame.change_id) + " " + str(frame.time_spent) + " " + str(sum(used_time)) +" "+ str(frame.timestamp)
					# + interannotator agreement
					if frame.comment:
						comment_file_content.append(output+ " " + frame.comment+"\n")
					# if mwes:
					all_mwes = frame.mwe.all()
					all_semantic_labels = frame.slot_element.filter(role_label__isnull=False)
					all_coercions = frame.slot_element.filter(Q(reference_d=True)|Q(reference_c=True)|Q(reference_r=True))
					if len(all_semantic_labels) > 0:
						semantic_role_output = output + ".na"
					if len(all_coercions) > 0:
						#print("C",all_coercions.values_list("reference_d", "reference_c", "reference_r"))
						coercions_output = output
					if len(all_mwes) > 0:
						mwe_output = output
					for slot in frame.slot_element.all():
						if slot.component_type == "token":
							token = Token.objects.get(id=slot.id_of_token)
							slot_str = token.lemma + "-:-" + str(token.position) + "-:-"
							#frame_output += " " + slot_str
						else:
							mwe = MWE.objects.get(id=slot.id_of_mwe)
							mwe_positions = list()
							for token in mwe.components.all():
								mwe_positions.append(str(token.position))
							mwe_positions = "_".join(mwe_positions)
							slot_str = str(mwe) + "-:-" + mwe_positions + "-:-"
							mwe_output += " " + str(mwe) + "-:-" + mwe_positions
						if slot.role_label:
							semantic_role_output += " " + slot_str + slot.role_label

						if slot.reference_c or slot.reference_d or slot.reference_r:
							coercions_output += " "+slot_str
						if slot.reference_c:
							coercions_output += "C"
						if slot.reference_d:
							coercions_output += "D"
						if slot.reference_r:
							coercions_output += "R"
					frame_file_content.append(frame_output + "\n")
					metadata_file_content.append(metadata_output + "\n")
					task_1_file_content.append(task_1)
					if semantic_role_output != "":
						semantic_role_file_content.append(semantic_role_output+"\n")
					if mwe_output != "":
						mwe_file_content.append(mwe_output+"\n")
					if coercions_output != "":
						coercions_file_content.append(coercions_output+"\n")
					# frame_output = task-2.1.txt
					# semantic_role_output = task-2.2.txt
				with open(os.path.join(base_dir,"data/export/task-2.1.txt"), "w", encoding="utf-8") as output_file:
					output_file.writelines(frame_file_content)
				with open(os.path.join(base_dir,"data/export/task-1.txt"), "w", encoding="utf-8") as output_file:
					output_file.writelines(task_1_file_content)
				#with open("data/export/task-2.2.txt", "w", encoding="utf-8") as output_file:
				#	output_file.writelines(semantic_role_file_content)
				with open(os.path.join(base_dir,"data/export/multiwordunits.txt"), "w", encoding="utf-8") as output_file:
					output_file.writelines(mwe_file_content)
				with open(os.path.join(base_dir,"data/export/metadata.txt"), "w", encoding="utf-8") as output_file:
					output_file.writelines(metadata_file_content)
				with open(os.path.join(base_dir,"data/export/coercions.txt"), "w", encoding="utf-8") as output_file:
					output_file.writelines(coercions_file_content)
				with open(os.path.join(base_dir,"data/export/comments.txt"), "w", encoding="utf-8") as output_file:
					output_file.writelines(comment_file_content)
				shutil.make_archive(os.path.join(base_dir,"data/exported_files"), "zip", root_dir=os.path.join(base_dir,"data/"), base_dir="export/")
				filelist = [f for f in os.listdir(os.path.join(base_dir,"data/export"))]
				#for f in filelist:
				#	os.remove(os.path.join("data/export", f))
				with open(os.path.join(base_dir,"data/exported_files.zip"), "rb") as file_zip:
					resp = HttpResponse(file_zip, content_type="application/zip")
				resp["Content-Disposition"] = "attachment; filename="+"exported_files.zip"
				os.remove(os.path.join(base_dir,("data/exported_files.zip")))
				return resp
			else:
				return render(request, "annotate/export_database.html",
							  {"user_list": User.objects.all().values_list("username", flat=True),
							   "verb_list": sorted(list(set(Frame.objects.filter(current_version=True).values_list("verb_lemma", flat=True)))),
							   "frametype_list": sorted(
								   list(set(Frame.objects.filter(current_version=True).values_list("f_type", flat=True)))),
							   "error": "No frames for the current settings."})

		else:
			return render(request, "annotate/export_database.html",
						  {"user_list": User.objects.all().values_list("username", flat=True),
						   "verb_list": sorted(list(set(Frame.objects.filter(current_version=True).values_list("verb_lemma", flat=True)))),
						   "frametype_list": sorted(list(set(Frame.objects.filter(current_version=True).values_list("f_type", flat=True))))})
	else:
		return render(request, "annotate/introduction.html")


#@login_required(login_url="login")
def export_metadata(selected_frames, count_changes, time_per_frame):
	meta_data = ""
	for frame in selected_frames:
		frame_position = frame.position.replace('-', '_')
		meta_data += str(frame.id_of_sentence) +"\t" + str(frame_position) + "\t" + frame.verb_lemma
		if count_changes:
			meta_data += "\t" + str(frame.change_id)
		if time_per_frame:
			meta_data += "\t" + str(frame.time_spent)
		meta_data += "\n"
	return meta_data



@login_required(login_url="login")
def export_history(request):
	"""
	export history of selected frame to a textfile. List all changes of the annotation of the selected frame.
	:param request: frontend request to export history of frames of the database.
	:return: text file with history of selected frame.
	"""
	if request.user.is_superuser:
		if request.method == "POST":
			selected_frames = request.POST.getlist("frame_selection")
			print("selected frames", selected_frames)
			for frame_settings in selected_frames:
				frame_settings = frame_settings.split("_")
				output = ["sentence_id position verb.f-type core-elements unique_key annotation_state used_time username description_of_change date time\n"]
				frame = Frame.objects.filter(sentence_id=frame_settings[0], position=frame_settings[1]).order_by("change_id")
				for change in frame:
					output_string = str(change)+" "+ str(change.id) +" "+ "_".join(annotation_states[max(0,change.annotation_state-1)].split(" "))+ " "+str(change.used_time)+" "+str(change.user)+" "
					if change.description_of_change:
						output_string += "_".join(change.description_of_change.split(" "))+" "+str(change.timestamp)+ "\n"
					else:
						output_string += "_ " + str(change.timestamp) + "\n"
					output.append(output_string)

				response = HttpResponse(output, content_type="text/plain")
				response["Content-Disposition"] = "attachment; filename='history_"+str(frame_settings[0])+"_"+str(frame_settings[1])+".txt'"
				return response
		else:
			print("problem with frame number")
		return render(request, "annotate/export_history_of_frame.html", {"frame_list": Frame.objects.filter(current_version=True, annotated=True).order_by("verb_lemma")})
	return render(request, "annotate/introduction.html")




########################
### overview frames ###
########################



def update_filter(change_value, search_filter, value, count_all):
	if change_value == "next" and search_filter.end < count_all:
		search_filter.start = search_filter.end
		search_filter.end = search_filter.end + int(search_filter.count)
	# add min(len_set) here to get an end and dont index in nothing
	elif change_value == "last":
		search_filter.start = count_all-int(search_filter.count)
		search_filter.end = count_all
	elif change_value == "prev":
		search_filter.start = max(0, search_filter.start - int(search_filter.count))
		search_filter.end = search_filter.start + int(search_filter.count)
	elif change_value == "first":
		search_filter.start = 0
		search_filter.end = int(search_filter.count)
	elif change_value == "number_elements":
		search_filter.count = int(value)
		search_filter.start = 0
		search_filter.end = int(search_filter.count)
	elif change_value == "search_verb":
		search_filter.search_verb = value
		search_filter.start = 0
		search_filter.end = int(search_filter.count)
	elif change_value == "search_sent_id":
		if not value:
			search_filter.search_sent_id = None
			search_filter.start = 0
			search_filter.end = int(search_filter.count)
		else:
			search_filter.search_sent_id = int(value)
			search_filter.start = 0
			search_filter.end = int(search_filter.count)
	elif change_value == "search_frame":
		search_filter.search_frame = value
		search_filter.start = 0
		search_filter.end = int(search_filter.count)
	elif change_value == "search_certainty":
		search_filter.search_certainty = int(value)
		search_filter.start = 0
		search_filter.end = int(search_filter.count)
	search_filter.save()
	return search_filter


def get_filtersettings(username):
	if len(FilterSettingsAnnotated.objects.filter(username=username).values_list("username", flat=True)) == 0:
		search_filter_annotated = FilterSettingsAnnotated(username=username)
		search_filter_annotated.save()
	else:
		search_filter_annotated = FilterSettingsAnnotated.objects.get(username=username)

	if len(FilterSettingsUnannotated.objects.filter(username=username).values_list("username", flat=True)) == 0:
		search_filter_unannotated = FilterSettingsUnannotated(username=username)
		search_filter_unannotated.save()
	else:
		search_filter_unannotated = FilterSettingsUnannotated.objects.get(username=username)

	if len(FilterSettingsInprogress.objects.filter(username=username).values_list("username", flat=True)) == 0:
		search_filter_inprogress = FilterSettingsInprogress(username=username)
		search_filter_inprogress.save()
	else:
		search_filter_inprogress = FilterSettingsInprogress.objects.get(username=username)

	if len(FilterSettingsSkipped.objects.filter(username=username).values_list("username", flat=True)) == 0:
		search_filter_skipped = FilterSettingsSkipped(username=username)
		search_filter_skipped.save()
	else:
		search_filter_skipped = FilterSettingsSkipped.objects.get(username=username)
	return search_filter_annotated, search_filter_unannotated, search_filter_inprogress, search_filter_skipped



def check_removable_frame_types(frame):
	#custom_lexunits = LexicalUnits.objects.filter(verb=frame.verb_lemma+".v", new_custom_type=0)
	for frametype in FrameType.objects.filter(lexUnits__verb=frame.verb_lemma+".v", lexUnits__new_custom_value=True):
		#print(Frame.objects.filter(Q(verb_lemma=frame.verb_lemma, current_version=1), Q(id!=frame.id)).values_list("f_type", flat=True), frametype.name != frame.f_type, frametype.name not in Frame.objects.filter(Q(verb_lemma=frame.verb_lemma, current_version=1), Q(id!=frame.id)).values_list("f_type", flat=True))
		frame_objects = Frame.objects.filter(Q(verb_lemma=frame.verb_lemma, current_version=1, annotation_state=5))
		if frametype.name not in frame_objects.values_list("f_type", flat=True):
			lexunit = LexicalUnits.objects.get(verb=frame.verb_lemma+".v", new_custom_value=True)
			frametype.lexUnits.remove(lexunit)
	#if len(custom_lexunits) == 1:
	return 1


def get_records_by_query(search_filter, records_type, username):
	# query_dict = request.session["current_query_"+records_type]
	if records_type == "annotated":
		frame_records = Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=False, annotation_state=5)
	elif records_type == "skipped":
		frame_records = Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=True)
	elif records_type == "frames_in_progress":
		frame_records = Frame.objects.filter(Q(user=username, current_version=True, skipped=False, annotation_state__range=[1, 4]) | Q(
						user=username, current_version=True, skipped=False, annotation_state=4,	annotated=False))
	elif records_type == 'not_annotated_frames':
		frame_records = Frame.objects.filter(user=username, annotated=False, current_version=True,
															 annotation_state=0, skipped=False)
	nr_all_records = len(frame_records)
	#request.session["nr_all_frames_" + records_type] = len(frame_records)
	if search_filter.search_verb:
		frame_records = frame_records.filter(verb_lemma__istartswith=search_filter.search_verb.lower())
		#print("verb", len(frame_records))
	if search_filter.search_frame:
		frame_records = frame_records.filter(f_type__istartswith=search_filter.search_frame)
		#print("frame", len(frame_records))
	if search_filter.search_certainty:
		frame_records = frame_records.filter(certainty=search_filter.search_certainty)
		#print("certainty", len(frame_records))
	if search_filter.search_sent_id:
		frame_records = frame_records.filter(sentence_id=search_filter.search_sent_id)
		#print("sentid",len(frame_records))
	start_value = search_filter.start
	end_value = search_filter.end
	return frame_records.order_by("-timestamp", "verb_lemma", "id_of_sentence", "position")[start_value:end_value], nr_all_records, len(frame_records)
#[request.session["current_query_position_start_"+records_type]:request.session["current_query_position_end_"+records_type]]



@login_required(login_url="login")
def frames_list(request):
	"""
		shows the frame_list. Will be shown after login and after saving a frame. Is splitted into not annotated and
		already annotated frames. If request data is sent (when redirected from frame_detail) save last changes on frame
		to database.
	"""
	if request.user.is_authenticated:
		username = request.user.username
		request.session["username"] = username
		print(username)
	else:
		return render(request, "annotate/introduction.html")
	request.session["all_verbs"] = list(
		Frame.objects.filter(user=username, current_version=True).order_by("verb_lemma").values_list("verb_lemma",
																									 flat=True).distinct())
	search_filter_annotated, search_filter_unannotated, search_filter_inprogress, search_filter_skipped = get_filtersettings(username)

	if request.method == "POST":
		# used after saving
		#frame_type = request.POST.get("f-type")
		record_type = request.POST.get("record_type")

		if record_type != None:
			change_value = request.POST.get("change_value")
			if record_type == "annotated":
				search_filter = update_filter(change_value, search_filter_annotated, request.POST.get("value"), len(Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=False, annotation_state=5).values_list("id", flat=True)))
			elif record_type == "skipped":
				search_filter = update_filter(change_value, search_filter_skipped, request.POST.get("value"), len(Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=True).values_list("id", flat=True)))
			elif record_type == "not_annotated_frames":
				search_filter = update_filter(change_value, search_filter_unannotated, request.POST.get("value"), len(Frame.objects.filter(user=username, annotated=False, current_version=True, annotation_state=0, skipped=False).values_list("id", flat=True)))
			elif record_type == "frames_in_progress":
				search_filter = update_filter(change_value, search_filter_inprogress, request.POST.get("value"), len(Frame.objects.filter(Q(user=username, current_version=True, skipped=False, annotation_state__range=[1, 4]) | Q(user=username, current_version=True, skipped=False, annotation_state=4,	annotated=False)).values_list("id", flat=True)))
			else:
				return JsonResponse({"error": "Something went wrong."})
			frame_records, nr, nrc = get_records_by_query(search_filter, record_type, username)
			return HttpResponse(serializers.serialize('json', frame_records),
								content_type="application/json")



		#save previous frame (use function)
		frame_id = request.session["frame_nr"]
		certainty_value = request.POST.get("certainty_scale")
		comment = request.POST.get("comment")
		#print("session frame_id", frame_id, certainty_value, comment, request.POST)
		if len(Frame.objects.filter(user=username, id=frame_id, current_version=False)) > 0:
			annotated_frames = Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=False,annotation_state=5).order_by("-timestamp", "verb_lemma", "id_of_sentence", "position")

			return render(request, "annotate/frames_list.html", {
				"skipped_frames": Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=True).order_by("-timestamp", "verb_lemma", "id_of_sentence", "position"),
				"frames_in_progress": Frame.objects.filter(Q(user=username, current_version=True, skipped=False, annotation_state__range=[1, 4]) | Q(user=username, current_version=True, skipped=False, annotation_state=4, annotated=False)).order_by("-timestamp", "verb_lemma", "id_of_sentence", "position"),
				"annotated_frames": annotated_frames,
				"not_annotated_frames": Frame.objects.filter(user=username, annotated=False, current_version=True, annotation_state=0, skipped=False).order_by("verb_lemma", "id_of_sentence", "position"),
				})
		frame = Frame.objects.get(user=username, id=frame_id, current_version=True)
		frame_verb = frame.verb_lemma+".v"
		used_time = time.time() - request.session["time_spent"]
		annotation_state = request.session["annotation_state"]
		if request.POST.get("slider_draft") == "on":
			if annotation_state == 5:
				annotation_state = 4
			print(request.POST.get("slider_draft"), annotation_state)
		else:
			if annotation_state < 5:
				annotation_state += 1
			change_and_save_new_frame_type(frame.f_type, frame_verb, frame=None, save_core_types=False,
										   assign_to_lex=True)
		frame = copy_frame(frame, used_time=used_time, annotation_state=annotation_state, description="save and go back to list")
		check_removable_frame_types(frame)
		frame.annotated = True
		frame.comment = comment
		if certainty_value and certainty_value != frame.certainty:
			frame.certainty = certainty_value
		frame.save(update_fields=["comment", "certainty", "annotated"])

	request.session["annotation_state"] = 0
	frame_records_in_progress, nr_all_progress, nr_current_progress = get_records_by_query(search_filter_inprogress, "frames_in_progress", username)
	frame_records_unannotated, nr_all_unannotated, nr_current_unannotated = get_records_by_query(search_filter_unannotated, "not_annotated_frames", username)
	frame_records_annotated, nr_all_annotated, nr_current_annotated = get_records_by_query(search_filter_annotated, "annotated", username)
	frame_records_skipped, nr_all_skipped, nr_current_skipped = get_records_by_query(search_filter_skipped, "skipped", username)


	return render(request, "annotate/frames_list.html", {"search_filter_annotated": search_filter_annotated, "search_filter_unannotated": search_filter_unannotated, "search_filter_skipped": search_filter_skipped, "search_filter_inprogress": search_filter_inprogress,
														 "skipped_frames": frame_records_skipped,
														 "frames_in_progress": frame_records_in_progress,
														 "annotated_frames": frame_records_annotated,
														 "not_annotated_frames": frame_records_unannotated,
														 "nr_all_annotated": nr_all_annotated, "nr_all_inprogress": nr_all_progress,
														 "nr_all_skipped": nr_all_skipped, "nr_all_unannotated": nr_all_unannotated,
														 "nr_current_annotated": nr_current_annotated, "nr_current_inprogress": nr_current_progress,
														 "nr_current_skipped": nr_current_skipped, "nr_current_unannotated": nr_current_unannotated

														 })

@login_required(login_url="login")
def frame_not_found(request):
	"""
	If a frame is not found a error message is shown on the frame list page. The user is redirected to the frame list page.
	"""
	username = request.user.username
	search_filter_annotated, search_filter_unannotated, search_filter_inprogress, search_filter_skipped = get_filtersettings(username)
	frame_records_in_progress, nr_all_progress, nr_current_progress = get_records_by_query(search_filter_inprogress,"frames_in_progress",username)
	frame_records_unannotated, nr_all_unannotated, nr_current_unannotated = get_records_by_query(search_filter_unannotated, "not_annotated_frames", username)
	frame_records_annotated, nr_all_annotated, nr_current_annotated = get_records_by_query(search_filter_annotated,"annotated", username)
	frame_records_skipped, nr_all_skipped, nr_current_skipped = get_records_by_query(search_filter_skipped, "skipped",username)

	return render(request, "annotate/frames_list.html", {"search_filter_annotated": search_filter_annotated,
														 "search_filter_unannotated": search_filter_unannotated,
														 "search_filter_skipped": search_filter_skipped,
														 "search_filter_inprogress": search_filter_inprogress,
														 "skipped_frames": frame_records_skipped,
														 "frames_in_progress": frame_records_in_progress,
														 "annotated_frames": frame_records_annotated,
														 "not_annotated_frames": frame_records_unannotated,
														 "nr_all_annotated": nr_all_annotated,
														 "nr_all_inprogress": nr_all_progress,
														 "nr_all_skipped": nr_all_skipped,
														 "nr_all_unannotated": nr_all_unannotated,
														 "nr_current_annotated": nr_current_annotated,
														 "nr_current_inprogress": nr_current_progress,
														 "nr_current_skipped": nr_current_skipped,
														 "nr_current_unannotated": nr_current_unannotated,
														 "message": "Your frame URL is wrong or there are two instances of the record requested, check the identifiers in the URL or contact the system operators."
														 })
	return render(request, 'annotate/frames_list.html', {
		'skipped_frames': Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=True).order_by('verb_lemma'),
		'frames_in_progress': Frame.objects.filter(Q(user=username, current_version=True, skipped=False, annotation_state__range=[1, 4]) | Q(user=username, current_version=True, skipped=False, annotation_state=4, annotated=False)).order_by("-timestamp", 'verb_lemma', "id_of_sentence", "position")[0:140],
		'annotated_frames': Frame.objects.filter(user=username, annotated=True, current_version=True, skipped=False, annotation_state=5).order_by("-timestamp", 'verb_lemma', "id_of_sentence", "position")[0:540],
		'not_annotated_frames': Frame.objects.filter(user=username, annotated=False, current_version=True, annotation_state=0, skipped=False).order_by('verb_lemma', "id_of_sentence", "position")[0:150],
		"message": "Your frame URL is wrong or there are two instances of the record requested, check the identifiers in the URL or contact the system operators."})

