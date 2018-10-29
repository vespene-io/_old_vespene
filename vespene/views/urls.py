#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#  -------------------------------------------------------------------------
#  urls.py - the standard web routes configuration file for Django
#  --------------------------------------------------------------------------

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from vespene.views import index, webhook_post
from vespene.views.fileserving import serve_file, serve_dir
from vespene.views.build import BuildView
from vespene.views.pipeline import PipelineView
from vespene.views.project import ProjectView
from vespene.views.service_login import ServiceLoginView
from vespene.views.snippet import SnippetView
from vespene.views.ssh_key import SshKeyView
from vespene.views.variable_set import VariableSetView
from vespene.views.worker_pool import WorkerPoolView
from vespene.views.organization import OrganizationView
from vespene.views.stage import StageView
from vespene.views.user import UserView
from vespene.views.group import GroupView

urlpatterns = [

    # Home page
    path('', index, name='index'),
    path('ui', index, name='index'),
    path('ui/', index, name='index'),

    # Login/Logout
    path('login/', LoginView.as_view(template_name='registration/login.html'), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),

    # Admin
    path('admin/', admin.site.urls),

    # Projects
    path('ui/projects', ProjectView.list, name='project_list'),
    path('ui/projects/new', ProjectView.new, name='project_new'),
    path('ui/projects/<pk>/edit', ProjectView.edit, name='project_edit'),
    path('ui/projects/<pk>/delete', ProjectView.delete, name='project_delete'),
    path('ui/projects/<pk>/detail', ProjectView.detail, name='project_detail'),
    path('ui/projects/<pk>/start', ProjectView.project_start, name='project_start'),
    path('ui/projects/<pk>/start_prompt', ProjectView.project_start_prompt, name='project_start_prompt'),

    # Builds
    path('ui/builds', BuildView.list, name='build_list'),
    path('ui/builds/<pk>/detail', BuildView.detail, name='build_detail'),
    path('ui/builds/<pk>/stop', BuildView.build_stop, name='build_stop'),

    # Snippets
    path('ui/snippets', SnippetView.list, name='snippet_list'),
    path('ui/snippets/new', SnippetView.new, name='snippet_new'),
    path('ui/snippets/<pk>/edit', SnippetView.edit, name='snippet_edit'),
    path('ui/snippets/<pk>/delete', SnippetView.delete, name='snippet_delete'),
    path('ui/snippets/<pk>/detail', SnippetView.detail, name='snippet_detail'),

    # Variable Sets
    path('ui/variable_sets', VariableSetView.list, name='variable_set_list'),
    path('ui/variable_sets/new', VariableSetView.new, name='variable_set_new'),
    path('ui/variable_sets/<pk>/edit', VariableSetView.edit, name='variable_set_edit'),
    path('ui/variable_sets/<pk>/delete', VariableSetView.delete, name='variable_set_delete'),
    path('ui/variable_sets/<pk>/detail', VariableSetView.detail, name='variable_set_detail'),

    # SSH Access
    path('ui/ssh_keys', SshKeyView.list, name='ssh_key_list'),
    path('ui/ssh_keys/new', SshKeyView.new, name='ssh_key_new'),
    path('ui/ssh_keys/<pk>/edit', SshKeyView.edit, name='ssh_key_edit'),
    path('ui/ssh_keys/<pk>/delete', SshKeyView.delete, name='ssh_key_delete'),
    path('ui/ssh_keys/<pk>/detail', SshKeyView.detail, name='ssh_key_detail'),

    # Service Logins
    path('ui/service_logins', ServiceLoginView.list, name='service_login_list'),
    path('ui/service_logins/new', ServiceLoginView.new, name='service_login_new'),
    path('ui/service_logins/<pk>/edit', ServiceLoginView.edit, name='service_login_edit'),
    path('ui/service_logins/<pk>/delete', ServiceLoginView.delete, name='service_login_delete'),
    path('ui/service_logins/<pk>/detail', ServiceLoginView.detail, name='service_login_detail'),

    # Worker Pools
    path('ui/worker_pools', WorkerPoolView.list, name='worker_pool_list'),
    path('ui/worker_pools/new', WorkerPoolView.new, name='worker_pool_new'),
    path('ui/worker_pools/<pk>/edit', WorkerPoolView.edit, name='worker_pool_edit'),
    path('ui/worker_pools/<pk>/delete', WorkerPoolView.delete, name='worker_pool_delete'),
    path('ui/worker_pools/<pk>/detail', WorkerPoolView.detail, name='worker_pool_detail'),

    # Stages
    path('ui/stages', StageView.list, name='stage_list'),
    path('ui/stages/new', StageView.new, name='stage_new'),
    path('ui/stages/<pk>/edit', StageView.edit, name='stage_edit'),
    path('ui/stages/<pk>/delete', StageView.delete, name='stage_delete'),
    path('ui/stages/<pk>/detail', StageView.detail, name='stage_detail'),

    # Users
    path('ui/users', UserView.list, name='user_list'),
    path('ui/users/new', UserView.new, name='user_new'),
    path('ui/users/<pk>/edit', UserView.edit, name='user_edit'),
    path('ui/users/<pk>/delete', UserView.delete, name='user_delete'),
    path('ui/users/<pk>/detail', UserView.detail, name='user_detail'),

    # Groups
    path('ui/groups', GroupView.list, name='group_list'),
    path('ui/groups/new', GroupView.new, name='group_new'),
    path('ui/groups/<pk>/edit', GroupView.edit, name='group_edit'),
    path('ui/groups/<pk>/delete', GroupView.delete, name='group_delete'),
    path('ui/groups/<pk>/detail', GroupView.detail, name='group_detail'),

    # Pipelines
    path('ui/pipelines', PipelineView.list, name='pipeline_list'),
    path('ui/pipelines/new', PipelineView.new, name='pipeline_new'),
    path('ui/pipelines/<pk>/edit', PipelineView.edit, name='pipeline_edit'),
    path('ui/pipelines/<pk>/delete', PipelineView.delete, name='pipeline_delete'),
    path('ui/pipelines/<pk>/detail', PipelineView.detail, name='pipeline_detail'),
    path('ui/pipelines/<pk>/map', PipelineView.map, name='pipeline_map'),

    # Organizations
    path('ui/organizations', OrganizationView.list, name='organization_list'),
    path('ui/organizations/new', OrganizationView.new, name='organization_new'),
    path('ui/organizations/<pk>/edit', OrganizationView.edit, name='organization_edit'),
    path('ui/organizations/<pk>/delete', OrganizationView.delete, name='organization_delete'),
    path('ui/organizations/<pk>/detail', OrganizationView.detail, name='organization_detail'),

    # Webhooks
    path('webhooks', webhook_post, name='webhook_post'),
    path('webhooks/', webhook_post, name='webhook_post'),

    # Fileserving
    path('srv/<pk>/f/<location>', serve_file, name="serve_file"),
    path('srv/<pk>/d', serve_dir, name="serve_dir")


]
