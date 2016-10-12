#!/usr/bin/env python3

class Report(object):
	def __init__(self, repo=None, org=None):
		self.repo = repo
		self.org = org


	def user_languages(self):
		commit_list = []
		sha_list = []
		committer_and_file_type = []
		for r in self.repo:
			commits = r.iter_commits(number=11)
			print(commits)
			for c in commits:
				max_shas = 0
				while max_shas < 10:
					sha = c.sha
					sha_list.append(sha)
					max_shas = max_shas + 1


		for sha in sha_list:
			commit_list.append(r.commit(sha).to_json())

		for cj in commit_list:
			try:
				files = cj['files'][0]['filename']
				committer = cj['commit']['author']['name']
				sha = cj['sha'][0:6]
				continue
			except TypeError:
				continue
			except IndexError:
				continue

			finally:
				if "/" in files:
					files = files.split("/")[-1]
					extension = files.split(".")[-1]
					committer_and_file_type.append([sha, committer, extension])
				elif "." in files:
					files = files.split(".")[-1]
					committer_and_file_type.append([sha, committer, files])
				else:
					pass

		print(committer_and_file_type)
		return committer_and_file_type

	def pr_ratios(self, state='Closed'):
		pass

	def contribution_count(self):
		pass

	def repo_maintenance(self):
		pass

	def open_issues(self):
		pass

	def issue_comments(self, state='Closed'):
		pass

	def pr_sentiment(self):
		pass
