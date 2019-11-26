#from ..models import *
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

class LoggedInUser(models.Model):
		# https://dev.to/fleepgeek/prevent-multiple-sessions-for-a-user-in-your-django-application-13oo
		# Model to store the list of logged in users
	user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='logged_in_user', on_delete=models.CASCADE)
	# Session keys are 32 characters long
	session_key = models.CharField(max_length=32, null=True, blank=True)

	def __str__(self):
		return self.user.username

class ExtendedUser(models.Model):

	# https://dev.to/fleepgeek/prevent-multiple-sessions-for-a-user-in-your-django-application-13oo
	# Model to store the list of logged in users
	#user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	username = models.CharField(null=True, blank=True, max_length=100)
	# Session keys are 32 characters long
	ip_adress = models.CharField(null=True, blank=True, max_length=20)
	browser = models.CharField(null=True, blank=True, max_length=200)
	login_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)


class Slot(models.Model):
	id_of_token = models.IntegerField(blank=True, null=True)
	id_of_mwe = models.IntegerField(blank=True, null=True)
	component_type = models.TextField(blank=True, null=True)
	core_element_type = models.TextField(blank=True, null=True)
	frame_id = models.IntegerField(blank=True, null=True)
	xml_id = models.IntegerField(blank=True, null=True)
	reference_c = models.BooleanField(default=False)
	reference_d = models.BooleanField(default=False)
	reference_r = models.BooleanField(default=False)
	role_label = models.TextField(blank=True, null=True)

	def __str__(self):
		if self.component_type == "token":
			token = Token.objects.get(id=self.id_of_token)
			return token.lemma + '-:-' + str(token.position) + '-:-' + self.core_element_type
		else:
			mwe = MWE.objects.get(id=self.id_of_mwe)
			mwe_lemma = ''
			mwe_positions = ''
			for token in mwe.components.all().order_by('position'):
				mwe_lemma += token.lemma+'_'
				mwe_positions += str(token.position)+'_'
			return mwe_lemma[:-1] + '-:-' + str(mwe_positions[:-1]) + '-:-' + self.core_element_type


class Token(models.Model):
	"""
		Token model to save all token of the input sentences. They are specified by the position, word_form. lemma,
		dependency relations and the belonging sentence.
	"""
	position = models.IntegerField()
	word_form = models.TextField()
	lemma = models.TextField()
	pos = models.TextField(blank=True, null=True)
	xpos = models.TextField(blank=True, null=True)
	dep_nr = models.IntegerField()
	dep_rel = models.TextField()
	sentence_id = models.TextField()
	#core_element_id = models.IntegerField(blank=True, null=True)
	#core_element = models.ForeignKey(CoreElement, on_delete=models.CASCADE, blank=True, null=True)
	#slot_type = models.TextField()
	# @todo: delete core element and slottype, are not used anymore
	#parent = models.ForeignKey('self', on_delete=models.CASCADE)
	def __str__(self):
		return self.word_form


class Sentence(models.Model):
	"""
		sentence model with stored token objects, which are assigned with manytomany relations
	"""
	sentence_id = models.IntegerField(primary_key=True)
	token = models.ManyToManyField(Token)
	def __str__(self):
		return self.sentence_id


class LexicalUnits(models.Model):
	"""
		LexicalUnit object which refer to the lexical unit elements of the FrameNet data
	"""
	verb = models.TextField()
	xml_id = models.IntegerField(blank=True, null=True)
	new_custom_value = models.BooleanField(default=False)
	def __str__(self):
		return self.verb+'_'+str(self.xml_id)


class MWE(models.Model):
	"""
		MWE object which will be added to a frame. Contains the components of a MWE (which are assigned to Token objects)
		and optional the type of the MWE.
	"""
	components = models.ManyToManyField(Token)
	type = models.TextField(blank=True, null=True)
	mwe_verb = models.BooleanField(default=False)
	# head = models.ForeignKey(Token, on_delete=models.CASCADE)

	def __str__(self):
		mwe_string = ""
		for token in self.components.all():
			mwe_string += token.lemma +'_'
		return mwe_string[:-1]


class Frame(models.Model):
	"""
		Frame object which contains all important information about the frame. It contains the unique identifiers with
		sentence id, verb lemma and position of the verb lemma. A new frame object of a combination sentence id,
		word and position will be created when the frame was changed (core element edited/added/deleted or frame type
		change). Current version marks which is the frame with the last changes.
		The core elements are save in a seperate table as coreelement objects.
		The time of each change will be saved in used_time, time_spent stands for the time spent on the frame
		detail page.
	"""
	# id = models.TextField(primary_key=True) # id = models.IntegerField(primary_key=True)
	id_of_sentence = models.IntegerField()
	sentence = models.ForeignKey(Sentence, on_delete=models.CASCADE)
	position = models.TextField()
	verb_lemma = models.TextField()
	verb_ids = models.TextField()
	f_type = models.TextField()
	user = models.TextField()
	annotated = models.BooleanField()
	comment = models.TextField(blank=True, null=True)
	used_clicks = models.IntegerField(default=0)
	used_time = models.IntegerField(default=0) # time spent on subtask
	time_spent = models.IntegerField(default=0) # time spent on read/frametype/mwe/slot/comment
	change_id = models.IntegerField(default=0)
	current_version = models.BooleanField(default=True)
	certainty = models.IntegerField(null=True, blank=True)
	mwe = models.ManyToManyField(MWE)
	annotation_state = models.IntegerField(default=0)
	#created_at = models.DateTimeField(auto_now_add=True)
	slot_element = models.ManyToManyField(Slot)
	verb_addition = models.TextField(default='')
	skipped = models.BooleanField(default=False)
	skip_reason = models.TextField(default='')
	timestamp = models.DateTimeField(auto_now_add=True, blank=True, null=True)
	description_of_change = models.TextField(blank=True, null=True)

	def __str__(self):
		frame_position = str(self.position).replace("-", "_")
		frame_string = '#'+str(self.id_of_sentence)+' '+frame_position+' '+self.verb_lemma+self.verb_addition+'.'+self.f_type+' '
		for core_string in self.slot_element.all():
			frame_string += str(core_string)+' '

		return frame_string.strip()  # remove additional space on the right


class CoreElementType(models.Model):
	"""
		Core element types based on the FrameNet data, contains definition, name and xml_id. If new_custom_value is true,
		a new type was inserted in the text field.
	"""
	name = models.TextField()
	definition = models.TextField(blank=True, null=True)
	xml_id = models.IntegerField(blank=True, null=True)
	new_custom_value = models.BooleanField(default=False)
	core_type = models.TextField(default="core")

	def __str__(self):
		return self.name+'_'+str(self.xml_id)


class FrameType(models.Model):
	"""
		Frame types based on the FrameNet data, contains definition, name and xml_id and reference to possible
		 lexical units. If new_custom_value is true, a new type was inserted in the text field.
	"""
	name = models.TextField()
	core_types = models.ManyToManyField(CoreElementType)
	definition = models.TextField(blank=True, null=True)
	lexUnits = models.ManyToManyField(LexicalUnits)
	xml_id = models.IntegerField(blank=True, null=True)
	new_custom_value = models.BooleanField(default=False)
	def __str__(self):
		return self.name+'_'+str(self.xml_id)


class SemanticRoles(models.Model):
	name = models.TextField()
	definition = models.TextField(blank=True, null=True)
	new_custom_value = models.BooleanField(default=False)
	def __str__(self):
		return self.name


class Comment(models.Model):
	"""
		comment object, which stores all user comments.
	"""
	user = models.TextField(blank=True, null=True)
	text = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)


class Synonyms(models.Model):
	"""
		synonym object for generating frame types to a given a lexical unit
	"""
	verb = models.TextField()
	synonym = models.TextField()
	xml_ids = models.TextField(null=True, blank=True)
	#id_of_lexUnit = models.IntegerField(null=True, blank=True)
	def __str__(self):
		return self.verb+'_'+self.synonym


class AnnotationSettings(models.Model):
	custom_element_type = models.BooleanField(default=False)
	custom_frame_type = models.BooleanField(default=False)


class FilterSettingsAnnotated(models.Model):
	username = models.TextField()

	count = models.TextField(default="25")
	start = models.IntegerField(default=0)
	end = models.IntegerField(default=25)
	search_verb = models.TextField()
	search_sent_id = models.IntegerField(blank=True, null=True)
	search_frame = models.TextField()
	search_certainty = models.IntegerField(blank=True, null=True)
	search_last_change = models.DateTimeField(blank=True, null=True)


class FilterSettingsUnannotated(models.Model):
	username = models.TextField()

	count = models.TextField(default="50")
	start = models.IntegerField(default=0)
	end = models.IntegerField(default=50)
	search_verb = models.TextField()
	search_sent_id = models.IntegerField(blank=True, null=True)
	search_frame = models.TextField()
	search_certainty = models.IntegerField(blank=True, null=True)
	search_last_change = models.DateTimeField(blank=True, null=True)


class FilterSettingsInprogress(models.Model):
	username = models.TextField()

	count = models.TextField(default="25")
	start = models.IntegerField(default=0)
	end = models.IntegerField(default=25)
	search_verb = models.TextField()
	search_sent_id = models.IntegerField(blank=True, null=True)
	search_frame = models.TextField()
	search_certainty = models.IntegerField(blank=True, null=True)
	search_last_change = models.DateTimeField(blank=True, null=True)


class FilterSettingsSkipped(models.Model):
	username = models.TextField()

	count = models.TextField(default="25")
	start = models.IntegerField(default=0)
	end = models.IntegerField(default=25)
	search_verb = models.TextField()
	search_sent_id = models.IntegerField(blank=True, null=True)
	search_frame = models.TextField()
	search_certainty = models.IntegerField(blank=True, null=True)
	search_last_change = models.DateTimeField(blank=True, null=True)
