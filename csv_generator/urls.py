from django.urls import path

from . import views

urlpatterns = [
    path('', views.schemas, name='schemas'),
    path('schema/new/', views.new_schema, name='new_schema'),
    path('schema/<int:pk>/edit', views.edit_schema, name='edit_schema'),
    path('schema/<int:pk>/delete', views.delete_schema, name='delete_schema'),
    path('schema/<int:pk>/datasets', views.new_schema, ),
    path('schema/<int:schema_pk>/column/<int:column_pk>', views.delete_schema_column, name='delete_schema_column'),
    path('schema/<int:schema_pk>/column/add', views.add_schema_column, name='add_schema_column'),
    path('schema/<int:schema_pk>/data_sets', views.data_sets, name='data_sets'),
    path('schema/<int:schema_pk>/data_sets/new', views.generate_data_set, name='new_data_set'),
    path('data_set/<int:data_set_pk>/download', views.url_data_set, name='url_data_set'),
]
