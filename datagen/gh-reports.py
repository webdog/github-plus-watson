#!/usr/bin/env python3
import github3
import sys
sys.path.append('./lib')
from getpass import getpass
from GHLogin import Login
import argparse
from reports import Report
import csv

parser = argparse.ArgumentParser(description="Generates reports from the GitHub API")
parser.add_argument('-s', action="store", dest="search")
parser.add_argument('-r', action="store", dest="repo", required=True)
parser.add_argument('-o', action="store", dest="org")
parser.add_argument('-u', action="store", dest="user", required=True)
parser.add_argument('-t', action="store", dest="report_type", type=int, required=True)
parser.add_argument('-e', action="store_true", dest="ghe", default=False)
parser.add_argument('-p', action="store", dest="public")

args = parser.parse_args()

user = args.user
token = getpass("please enter your P.A.T. for authentication\n>")
reqs_max = 5000
pub_search = True


def authenticate(ghe=args.ghe, user=user,token=token):
	if ghe:
		login = Login(user, token)
		return login.authenticate_ghe()

	else:
		print("this is running")
		login = Login(user, token)
		return login.authenticate()

gh = authenticate()

def get_org():
	for orgs in gh.iter_orgs():
		# We only allow an org at a time for restrict rate-limiting or performance issues
		org = [orgs.id for orgs in gh.iter_orgs() if orgs.name == args.org ]
	return org

def get_repos(org_search=False, user_search=True):
	if org_search:
		for orgs in get_org():
			repos = [repos for repos in orgs.iter_repos() if repos.name == args.repo]
		return repos
	elif user_search:
		repo = [r.refresh() for r in gh.iter_user_repos(user) if r.name == args.repo]
		return repo
	else:
		repo = [r.refresh() for r in gh.iter_user_repos('angular') if r.name == 'angular']
		return repo


def get_prs(limit=100):
	pulls = []
	for repo in get_repos():
		pr = repo.iter_pulls(state='all', number=limit)
		pr.refresh()
		for prs in pr:
			pulls.append(prs)
	return pulls

def valid_reports():
		valid = {
		1 : "Languages committed per User",
		2 : "Ratio of Merged/Unmerged Pull Requests (Status=Open and Closed)",
		3 : "Ratio of Merged/Unmerged Pull Requests (Status=Closed)",
		4 : "Contribution Count of last 100 Pull Requests",
		5 : "Repository Maintenance (Documentation submission vs Code Submission",
		6 : "Issues open by Assignee",
		7 : "Number of Comments on Closed Issues",
		8 : "Analyze sentiment of conversations in last 100 Pull Requests"
	}
		return valid


def report(rtype):
	if not isinstance(rtype, int):
		return "Expected an integer value. Exiting"
	elif rtype == 1:
		repo = get_repos()
		report = Report(repo).user_languages()
		return report
	elif rtype == 2:
		report = Report.bla()
		return report


	else:
		return True

def main():
	rt = args.report_type
	keys = [keys for keys, values in valid_reports().items()]
	if rt not in keys:
		return "You did not select a valid report"
	else:
		return report(rt)






if __name__ == "__main__":
	print("running main")
	main()