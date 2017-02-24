#!/usr/bin/env python3
import github3
import sys
sys.path.append('./lib')
from getpass import getpass
from GHLogin import Login
import argparse
from reports import Report
import csv
from pathlib import Path

parser = argparse.ArgumentParser(description="Generates reports from the GitHub API")
parser.add_argument('-s', action="store", dest="search")
parser.add_argument('-r', action="store", dest="repo", required=True)
parser.add_argument('-o', action="store", dest="org")
parser.add_argument('-u', action="store", dest="user", required=True)
parser.add_argument('-t', action="store", dest="report_type", type=int, required=True)
parser.add_argument('-e', action="store_true", dest="ghe", default=False)
parser.add_argument('-p', action="store_true", dest="public")

args = parser.parse_args()

user = args.user
token = getpass("please enter your P.A.T. for authentication\n>")
reqs_max = 5000


def authenticate(ghe=args.ghe, user=user,token=token):
	if ghe:
		login = Login(user, token)
		return login.authenticate_ghe()

	else:
		login = Login(user, token)
		return login.authenticate()

gh = authenticate()

def get_org(pub=None):
	if pub == None:
		for orgs in gh.iter_orgs():
			# We only allow an org at a time for restrict rate-limiting or performance issues
			org = [orgs.refresh() for orgs in gh.iter_orgs() if orgs.login == args.org ]
		return org
	else:
		org = [ gh.organization(pub) ]
		return org

def get_repos(org_search=True, user_search=False, pub_search=args.public):
	if pub_search:
		for orgs in get_org(pub=args.org):
			repo = [r.refresh() for r in orgs.iter_repos() if r.name == args.repo]
		return repo
	elif org_search:
		for orgs in get_org():
			repos = [repos for repos in orgs.iter_repos() if repos.name == args.repo]
		return repos
	elif user_search:
		repo = [r.refresh() for r in gh.iter_user_repos(user) if r.name == args.repo]
		return repo
	elif org_search and user_search:
		return "Cannot return both user and org repos"
	else:
		exit()


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
		2 : "Ratio of Merged/Unmerged Pull Requests (Status=All)",
		3 : "Ratio of Merged/Unmerged Pull Requests (Status=Closed)",
		4 : "Contribution Count of last 100 Pull Requests",
		5 : "Repository Maintenance (Documentation submission vs Code Submission",
		6 : "Issues open by Assignee",
		7 : "Number of Comments on Closed Issues",
		8 : "Analyze sentiment of conversations in last 100 Pull Requests",
		9 : "Pull Requests in State=Closed with Number of Comments",
		10: "Overall sentiment rating for a repository in an org",
		11: "Basic report of releases by a repository",
		12: "JSON to CSV of last 100 Pull Requests"
	}
		return valid


def report(rtype):
	if not isinstance(rtype, int):
		return "Expected an integer value. Exiting"
	elif rtype == 1:
		repo = get_repos()
		report = Report(repo=repo).user_languages()
		return out2csv(report, '../reports/issue_contrib.csv')
	elif rtype == 2:
		pulls = get_prs()
		report = Report(pulls=pulls).pr_ratios()
		return out2csv(report, '../reports/open_closed_merged_prs.csv')
	elif rtype == 3:
		pulls = get_prs(state='closed')
		report = Report(pulls=pulls).pr_ratios()
		return out2csv(report, '../reports/closed_merged_prs.csv')
	elif rtype == 4:
		pulls = get_prs()
		report = Report(pulls=pulls).contribution_count()
		return out2csv(report, '../reports/positive_negative_pr_contributions.csv')
	elif rtype == 5:
		pulls = get_prs()
		report = Report(pulls=pulls).repo_maintenance()
		return out2csv(report, '../reports/repo_maintenance.csv')
	elif rtype == 6:
		repo = get_repos()
		report = Report(repo=repo).open_issues()
		return out2csv(report, '../reports/issue_assignees.csv')
	elif rtype == 7:
		repo = get_repos()
		report = Report(repo=repo).issue_comments()
		return out2csv(report, '../closed_issue_comments.csv')
	elif rtype == 8:
		#This is a heavy computation. Limiting to 10 PRs, as we're analyzing each sentence
		#in each comment in a single PR
		pulls = get_prs(limit=100)
		report = Report(pulls=pulls).pr_sentiment()
		return out2csv(report, '../reports/sentiment_analysis.csv')
	elif rtype == 9:
		pulls = get_prs(limit=500)
		report = Report(pulls=pulls).pr_report()
		return out2csv(report, '../reports/pr_report_closed.csv')
	elif rtype == 10:
		repo = get_repos()
		pulls = get_prs(limit=50)
		report = Report(pulls=pulls, repo=repo).sentiment_repo_report()
		fname = '../reports/pr_sentiment_report.csv'
		if fexists(Path(fname)):
			return out2csv(report, '../reports/pr_sentiment_report.csv', "a")
		else:
			return out2csv(report, '../reports/pr_sentiment_report.csv', "w+")
	elif rtype == 12:
		pulls = get_prs(state='all', limit=100)
		report = Report(pulls=pulls).parse()
		return out2csv(report, '../reports/100_json_pulls.csv')
	return True

def fexists(fname):
	if fname.is_file():
		return True
	else:
		return False

def out2csv(lt, fname="tmp.csv", mode="w+"):
	if not isinstance(lt, list):
		return "Expected a list"
	else:
		#This function is generally intaking lists that contain multiple dictionaries.
		#We only want the headers to consist of a single list comprised of the keys from these dicts
		headers = set()
		for d in lt:
			headers.update(d.keys())

		print(headers)
		with open(fname, mode) as f:
			dw = csv.DictWriter(f, delimiter='|', fieldnames=headers)
			if mode == "a":
				for d in lt:
					dw.writerow(d)
			else:
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