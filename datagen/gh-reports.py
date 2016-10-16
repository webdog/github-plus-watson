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
		org = [orgs for orgs in gh.iter_orgs() if orgs.login == args.org ]
	return org

def get_repos(org_search=True, user_search=False):
	if org_search:
		for orgs in get_org():
			repos = [repos for repos in orgs.iter_repos() if repos.name == args.repo]
		return repos
	elif user_search:
		repo = [r.refresh() for r in gh.iter_user_repos(user) if r.name == args.repo]
		return repo
	elif org_search and user_search:
		return "Cannot return both user and org repos"
	else:
		repo = [r.refresh() for r in gh.iter_user_repos('angular') if r.name == 'angular']
		return repo


def get_prs(limit=100, state='all'):
	pulls = []
	for repo in get_repos():
		pr = repo.iter_pulls(state=state, number=limit)
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
		report = Report(repo=repo).user_languages()
		return report
	elif rtype == 2:
		pulls = get_prs()
		report = Report(pulls=pulls).pr_ratios()
		return report
	elif rtype == 3:
		pulls = get_prs(state='closed')
		report = Report(pulls).pr_ratios()
		return report
	elif rtype == 4:
		pulls = get_prs()
		report = Report(pulls=pulls).contribution_count()
		return report
	elif rtype == 5:
		pulls = get_prs()
		report = Report(pulls=pulls).repo_maintenance()
		return report
	elif rtype == 6:
		repo = get_repos()
		report = Report(repo=repo).open_issues()
		return report
	elif rtype == 7:
		repo = get_repos()
		report = Report(repo=repo).issue_comments()
		return report
	elif rtype == 8:
		#This is a heavy computation. Limiting to 10 PRs, as we're analyzing each sentence
		#in each comment in a single PR
		pulls = get_prs(limit=10)
		report = Report(pulls=pulls).pr_sentiment()
		print(out2csv(report))
		return report
	else:
		return True

def out2csv(lt, fname="tmp.csv"):
	if not isinstance(lt, list):
		return "Expected a list"
	else:
		#This function is generally intaking lists that contain multiple dictionaries.
		#We only want the headers to consist of a single list comprised of the keys from these dicts
		headers = set()
		for d in lt:
			headers.update(d.keys())

		print(headers)
		with open(fname, "w+") as f:
			dw = csv.DictWriter(f, delimiter='|', fieldnames=headers)
			dw.writerow(dict((fn, fn) for fn in headers))
			for d in lt:
				dw.writerow(d)
		return True
def main():
	rt = args.report_type
	keys = [keys for keys, values in valid_reports().items()]
	if rt not in keys:
		print("Please choose a valid selection:\n")
	else:
		return report(rt)






if __name__ == "__main__":
	main()