#  Copyright 2018, Michael DeHaan LLC
#  License: Apache License Version 2.0 + Commons Clause
#---------------------------------------------------------------------------
# test_webhook.py - CLI command used in development to simulate a webhook
# from GitHub to test the webhook functionality. Of limited use
# in a real deployment.
#---------------------------------------------------------------------------

import requests
import json
from django.core.management.base import BaseCommand
from vespene.models.project import Project
from vespene.common.logger import Logger

LOG = Logger()


WEBHOOK_URL = "webhooks"

GITHUB_WEBHOOK = """
{
  "ref": "refs/tags/simple-tag",
  "before": "a10867b14bb761a232cd80139fbd4c0d33264240",
  "after": "0000000000000000000000000000000000000000",
  "created": false,
  "deleted": true,
  "forced": false,
  "base_ref": null,
  "compare": "https://github.com/Codertocat/Hello-World/compare/a10867b14bb7...000000000000",
  "commits": [

  ],
  "head_commit": null,
  "repository": {
    "id": 135493233,
    "node_id": "MDEwOlJlcG9zaXRvcnkxMzU0OTMyMzM=",
    "name": "Hello-World",
    "full_name": "Codertocat/Hello-World",
    "owner": {
      "name": "Codertocat",
      "email": "21031067+Codertocat@users.noreply.github.com",
      "login": "Codertocat",
      "id": 21031067,
      "node_id": "MDQ6VXNlcjIxMDMxMDY3",
      "avatar_url": "https://avatars1.githubusercontent.com/u/21031067?v=4",
      "gravatar_id": "",
      "url": "https://api.github.com/users/Codertocat",
      "html_url": "https://github.com/Codertocat",
      "followers_url": "https://api.github.com/users/Codertocat/followers",
      "following_url": "https://api.github.com/users/Codertocat/following{/other_user}",
      "gists_url": "https://api.github.com/users/Codertocat/gists{/gist_id}",
      "starred_url": "https://api.github.com/users/Codertocat/starred{/owner}{/repo}",
      "subscriptions_url": "https://api.github.com/users/Codertocat/subscriptions",
      "organizations_url": "https://api.github.com/users/Codertocat/orgs",
      "repos_url": "https://api.github.com/users/Codertocat/repos",
      "events_url": "https://api.github.com/users/Codertocat/events{/privacy}",
      "received_events_url": "https://api.github.com/users/Codertocat/received_events",
      "type": "User",
      "site_admin": false
    },
    "private": false,
    "html_url": "https://github.com/Codertocat/Hello-World",
    "description": null,
    "fork": false,
    "url": "https://github.com/Codertocat/Hello-World",
    "forks_url": "https://api.github.com/repos/Codertocat/Hello-World/forks",
    "keys_url": "https://api.github.com/repos/Codertocat/Hello-World/keys{/key_id}",
    "collaborators_url": "https://api.github.com/repos/Codertocat/Hello-World/collaborators{/collaborator}",
    "teams_url": "https://api.github.com/repos/Codertocat/Hello-World/teams",
    "hooks_url": "https://api.github.com/repos/Codertocat/Hello-World/hooks",
    "issue_events_url": "https://api.github.com/repos/Codertocat/Hello-World/issues/events{/number}",
    "events_url": "https://api.github.com/repos/Codertocat/Hello-World/events",
    "assignees_url": "https://api.github.com/repos/Codertocat/Hello-World/assignees{/user}",
    "branches_url": "https://api.github.com/repos/Codertocat/Hello-World/branches{/branch}",
    "tags_url": "https://api.github.com/repos/Codertocat/Hello-World/tags",
    "blobs_url": "https://api.github.com/repos/Codertocat/Hello-World/git/blobs{/sha}",
    "git_tags_url": "https://api.github.com/repos/Codertocat/Hello-World/git/tags{/sha}",
    "git_refs_url": "https://api.github.com/repos/Codertocat/Hello-World/git/refs{/sha}",
    "trees_url": "https://api.github.com/repos/Codertocat/Hello-World/git/trees{/sha}",
    "statuses_url": "https://api.github.com/repos/Codertocat/Hello-World/statuses/{sha}",
    "languages_url": "https://api.github.com/repos/Codertocat/Hello-World/languages",
    "stargazers_url": "https://api.github.com/repos/Codertocat/Hello-World/stargazers",
    "contributors_url": "https://api.github.com/repos/Codertocat/Hello-World/contributors",
    "subscribers_url": "https://api.github.com/repos/Codertocat/Hello-World/subscribers",
    "subscription_url": "https://api.github.com/repos/Codertocat/Hello-World/subscription",
    "commits_url": "https://api.github.com/repos/Codertocat/Hello-World/commits{/sha}",
    "git_commits_url": "https://api.github.com/repos/Codertocat/Hello-World/git/commits{/sha}",
    "comments_url": "https://api.github.com/repos/Codertocat/Hello-World/comments{/number}",
    "issue_comment_url": "https://api.github.com/repos/Codertocat/Hello-World/issues/comments{/number}",
    "contents_url": "https://api.github.com/repos/Codertocat/Hello-World/contents/{+path}",
    "compare_url": "https://api.github.com/repos/Codertocat/Hello-World/compare/{base}...{head}",
    "merges_url": "https://api.github.com/repos/Codertocat/Hello-World/merges",
    "archive_url": "https://api.github.com/repos/Codertocat/Hello-World/{archive_format}{/ref}",
    "downloads_url": "https://api.github.com/repos/Codertocat/Hello-World/downloads",
    "issues_url": "https://api.github.com/repos/Codertocat/Hello-World/issues{/number}",
    "pulls_url": "https://api.github.com/repos/Codertocat/Hello-World/pulls{/number}",
    "milestones_url": "https://api.github.com/repos/Codertocat/Hello-World/milestones{/number}",
    "notifications_url": "https://api.github.com/repos/Codertocat/Hello-World/notifications{?since,all,participating}",
    "labels_url": "https://api.github.com/repos/Codertocat/Hello-World/labels{/name}",
    "releases_url": "https://api.github.com/repos/Codertocat/Hello-World/releases{/id}",
    "deployments_url": "https://api.github.com/repos/Codertocat/Hello-World/deployments",
    "created_at": 1527711484,
    "updated_at": "2018-05-30T20:18:35Z",
    "pushed_at": 1527711528,
    "git_url": "git://github.com/Codertocat/Hello-World.git",
    "ssh_url": "git@github.com:Codertocat/Hello-World.git",
    "clone_url": "https://github.com/Codertocat/Hello-World.git",
    "svn_url": "https://github.com/Codertocat/Hello-World",
    "homepage": null,
    "size": 0,
    "stargazers_count": 0,
    "watchers_count": 0,
    "language": null,
    "has_issues": true,
    "has_projects": true,
    "has_downloads": true,
    "has_wiki": true,
    "has_pages": true,
    "forks_count": 0,
    "mirror_url": null,
    "archived": false,
    "open_issues_count": 2,
    "license": null,
    "forks": 0,
    "open_issues": 2,
    "watchers": 0,
    "default_branch": "master",
    "stargazers": 0,
    "master_branch": "master"
  },
  "pusher": {
    "name": "Codertocat",
    "email": "21031067+Codertocat@users.noreply.github.com"
  },
  "sender": {
    "login": "Codertocat",
    "id": 21031067,
    "node_id": "MDQ6VXNlcjIxMDMxMDY3",
    "avatar_url": "https://avatars1.githubusercontent.com/u/21031067?v=4",
    "gravatar_id": "",
    "url": "https://api.github.com/users/Codertocat",
    "html_url": "https://github.com/Codertocat",
    "followers_url": "https://api.github.com/users/Codertocat/followers",
    "following_url": "https://api.github.com/users/Codertocat/following{/other_user}",
    "gists_url": "https://api.github.com/users/Codertocat/gists{/gist_id}",
    "starred_url": "https://api.github.com/users/Codertocat/starred{/owner}{/repo}",
    "subscriptions_url": "https://api.github.com/users/Codertocat/subscriptions",
    "organizations_url": "https://api.github.com/users/Codertocat/orgs",
    "repos_url": "https://api.github.com/users/Codertocat/repos",
    "events_url": "https://api.github.com/users/Codertocat/events{/privacy}",
    "received_events_url": "https://api.github.com/users/Codertocat/received_events",
    "type": "User",
    "site_admin": false
  }
}
"""

def do_github(url, project_id, token):
    content = json.loads(GITHUB_WEBHOOK)
    project = Project.objects.get(pk=project_id)
    content['repository']['git_url'] = project.repo_url
    if token:
        url = url + "?token=%s" % token
    r = requests.post(url, json=content)
    print(r.status_code)
    print(r.text)

class Command(BaseCommand):
    help = 'Simulates a webhook push for testing'

    def add_arguments(self, parser):
        parser.add_argument('project', type=int, help='project id')
        
        parser.add_argument(
            '--server',
            dest="server",
            default="127.0.0.1"
        )

        parser.add_argument(
            '--port',
            type=int,
            dest="port",
            default=80
        )

        parser.add_argument(
          '--token',
          dest="token",
          default=""
        )

    def handle(self, *args, **options):

        
        project_id = options['project']
        port = options['port']
        server = options['server']
        token = options['token']
        
        url = "http://%s:%s/%s" % (server, port, WEBHOOK_URL)
        do_github(url, project_id, token)

        #start = options['start']
        #stop = options['stop']

        #project = Project.objects.get(id=project_id)
        
        #if not start and not stop:
        #    raise CommandError("either --start or --stop are required")
        #if stop and start:
        #    raise CommandError("--start and --stop are mutually exclusive")
        #elif start:   
        #    LOG.info("Starting project")
        #    jobkick.start_project(project)
        #else:
        #    LOG.info("Stopping project")
        #    jobkick.stop_project(project)
