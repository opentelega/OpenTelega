from django.conf.urls import url

from fileserver import views, AdminViews

app_name = 'fileserver'
urlpatterns = [
    url(r'^upload_file/', views.upload_file, name='upload_file'),
    url(r'^get_file_list/', views.get_file_list, name='get_file_list'),
    url(r'^download_file_by_id/', views.download_file_by_id, name='download_file_by_id'),
    url(r'^change_user_password/', views.change_user_password, name='change_user_password'),
    url(r'^get_files_count/', views.get_files_count, name='get_files_count'),
    url(r'^user_get_version/', views.user_get_version, name='user_get_version'),
]

urlpatterns += [
    url(r'^initialize_server/', AdminViews.initialize_server, name='initialize_server'),
    url(r'^get_options_list/', AdminViews.get_options_list, name='get_options_list'),
    url(r'^change_option/', AdminViews.change_option, name='change_option'),
    url(r'^change_admin_password/', AdminViews.change_admin_password, name='change_admin_password'),
    url(r'^register_user/', AdminViews.register_user, name='register_user'),
    url(r'^reset_user_password/', AdminViews.reset_user_password, name='reset_user_password'),
    url(r'^delete_user/', AdminViews.delete_user, name='delete_user'),
    url(r'^list_all_users/', AdminViews.list_all_users, name='list_all_users'),
    url(r'^list_all_files/', AdminViews.list_all_files, name='list_all_files'),
    url(r'^admin_download_file/', AdminViews.admin_download_file, name='admin_download_file'),
    url(r'^delete_file/', AdminViews.delete_file, name='delete_file'),
    url(r'^clean_media_directory/', AdminViews.clean_media_directory, name='clean_media_directory'),
    url(r'^admin_get_version/', AdminViews.admin_get_version, name='admin_get_version'),
]