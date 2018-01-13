from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.front_page_view, name='login'),
    url(r'^trylogin/$', views.try_login_view , name='trylogin'),
    url(r'^signup/$', views.signup_view, name='signup'),
    url(r'^trysignup/$', views.try_signup_view, name='trysignup'),

    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<gid>[0-9]+)/vote/$', views.general_vote_view, name='vote'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<gid>[0-9]+)/(?P<sid>[0-9]+)/vote/$', views.specific_vote_view, name='svote'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<gid>[0-9]+)/$', views.general_view, name='general'),
    url(r'^(?P<uid>[0-9]+)/projects/$', views.project_list_view, name='projectlist'),
    url(r'^(?P<uid>[0-9]+)/projectconstructor/$', views.project_constructor_view, name='projectconstructor'),
    url(r'^(?P<uid>[0-9]+)/projectcreate/$', views.create_project, name='projectcreate'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/generallist$', views.general_list_view, name='generallist'),
    url(r'^(?P<uid>[0-9]+)/(?P<did>[0-9]+)/discussion$', views.discussion_view, name='discussion'),
    url(r'^(?P<uid>[0-9]+)/(?P<did>[0-9]+)/submitcomment', views.submit_comment, name='submitcomment'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<bid>[0-9]+)/bundlevote/$', views.bundle_vote_view, name='bundlevote'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/generalbundlecreate$', views.create_general_bundle, name='generalbundlecreate'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/bundlelist$', views.general_bundle_list_view, name='generalbundlelist'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/generalbundleconstructor$', views.general_bundle_constructor_view, name='generalbundleconstructor'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/genconstructor/$', views.general_constructor_view, name='genconstructor'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/submitgeneral/$', views.create_general, name='gencreate'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<gid>[0-9]+)/specconstructor/$', views.specific_constructor_view, name='specconstructor'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<gid>[0-9]+)/facetconstructor/$', views.facet_constructor_view, name='facetconstructor'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<gid>[0-9]+)/submitspecific/$', views.create_specific, name='speccreate'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<gid>[0-9]+)/submitfacet/$', views.create_facet, name='facetcreate'),
    url(r'^(?P<uid>[0-9]+)/(?P<pid>[0-9]+)/(?P<gid>[0-9]+)/facets/$', views.facets_view, name='facetsview'),
]