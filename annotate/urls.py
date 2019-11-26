from django.urls import path, re_path
from . import views
from django.contrib.staticfiles import views as static_views
from django.conf.urls.static import static
from semantic_frame_annotation import settings

"""
	connection between views and templates. Each view gets a name here, which will be shown in the address bar and is
	related to a function in views.py
"""

urlpatterns = [
	re_path(r'^frame_list$', views.frames_list, name='frames_list'),
	re_path(r'^frame_(\d{1,3}(-)?)+_\d{8}$', views.frame_detail, name='frames_detail'),
	re_path(r'^frame_', views.frame_not_found, name='frame_not_found'),
	re_path(r'^frame', views.frame_detail, name='frames_detail'),
	#path(r'^fill_database', views.fill_database,  name='fill_database'),
	path('admin_fuctions', views.admin_fuctions, name='admin_functions'),
	path('export_database', views.export_database, name='export_database'),
	path('insert_frames', views.insert_frames, name='insert_frames'),
	path('insert_framenet_files', views.insert_framenet_files, name='insert_framenet_files'),
	path('assign_users', views.assign_users_frames, name='assign_users'),
	re_path(r'^definition_frame_', views.frame_definition, name='frame_definition'),
	path('timespent', views.store_time_spent, name='timespent'),
	path('export_history', views.export_history, name='export_history'),
	re_path(r'^signup/$', views.signup, name='signup'),
	re_path(r'^test/$', views.test, name='test'),

	re_path(r'^home', views.home, name='home'),
	re_path(r'^$', views.home, name='home'),
	re_path(r'comment$', views.save_comments, name='comment'),
	path('skip_sentence', views.skip_sentence, name='skip_sentence'),
	path('semantic_role_labels', views.info_semantic_role, name='semantic_role'),
	path('convert_core_elements', views.convert_core_elements, name='convert_core_elements'),
	re_path(r'video$', views.display_video),
	path('add_roles', views.add_role_labels, name="add_roles"),
	path('change_roles', views.add_semantic_role_table, name="change_roles"),
	path('add_synonyms', views.add_synonyms, name="add_synonyms"),
	path('add_non_core', views.add_non_corelements_to_db, name="add_non_core"),
	path('delete_types', views.delete_wrong_types, name="delete_types"),
	path('set_settings', views.set_annotation_settings, name="set_settings"),
	path('save_sorting_order', views.set_sorting_order, name="save_sorting_order"),
	path('delete_old_framenet_types', views.delete_old_framenet_types, name="delete_old_framenet_types"),
	path('delete_non_lexicalized_frames', views.delete_non_lexicalized_frames, name="delete_non_lexicalized_frames"),
	path('insert_missing_framenet_files', views.insert_missing_frames, name="insert_missing_framenet_files")

] #+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
