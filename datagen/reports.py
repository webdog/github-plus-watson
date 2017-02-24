#!/usr/bin/env python3
from textblob import TextBlob
from textblob.sentiments import NaiveBayesAnalyzer

class Report(object):
	def __init__(self, repo=None, org=None, pulls=None):
		self.repo = repo
		self.org = org
		self.pulls = pulls

	def parse(self):
		plist = []
		for pr in self.pulls:
			pdict = {}
			pr = pr.refresh()
			try:
				pdict['number'] = pr.number
				pdict['state'] = pr.state
				pdict['title'] = pr.title
				pdict['assignee'] = pr.assignee
				pdict['number_of_comments'] = pr.comments
				pdict['number_of_commits'] = pr.commits
				pdict['merge_status'] = pr.mergeable
				pdict['created_at'] = pr.created_at
				pdict['merged_at'] = pr.merged_at
				pdict['merged_by'] = pr.merged_by
				pdict['additions'] = pr.additions
				pdict['deletions'] = pr.deletions


				plist.append(pdict)
			except TypeError:
				continue
		print(plist)

		return plist



	def user_languages(self):
		clist = []
		for r in self.repo:
			commits = r.iter_commits(number=500)
			for c in commits:
				cdict = {}
				try:
					cfiles = str(r.commit(c.sha).files[0]['filename'])
				except IndexError:
					print("Empty commit, continue")
					pass
				committer = str(r.commit(c.sha).author)
				if "/" in cfiles:
					files = cfiles.split("/")[-1].split(".")[-1]
					cdict['sha'] = c.sha
					cdict['filetype'] = files
					cdict['author'] = committer
				else:
					files = cfiles.split(".")[-1]
					cdict['sha'] = c.sha
					cdict['filetype'] = files
					cdict['author'] = committer
				clist.append(cdict)

		return clist

	def pr_ratios(self):
		plist = []
		plmrg = "pull_merged"
		plnmrg = "pull_not_merged"
		pltot = "pull_total"
		pdict = {
				plmrg: 0,
				plnmrg: 0,
				pltot: 0
			}
		for pr in self.pulls:
			pr = pr.refresh()
			if pr.is_merged():
				pdict[plmrg] += 1
			else:
				pdict[plnmrg] += 1

		pdict[pltot] = pdict[plmrg] + pdict[plnmrg]
		plist.append(pdict)

		return plist

	def pr_report(self):
		plist = []
		for pr in self.pulls:
			pr = pr.refresh()
			pdict = {}
			pdict['pr_id'] = pr.number
			pdict['pr_status'] = pr.state

			if pr.is_merged() == True:
				pdict['is_merged'] = "merged"
			else:
				pdict['is_merged'] = "not_merged"

			if pr.comments is None:
				pdict['num_comments'] = 0
			else:
				pdict['num_comments'] = pr.comments

			plist.append(pdict)
		return plist


	def contribution_count(self):
		plist = []
		pos = "net_positive"
		neg = "net_negative"
		neq = "net_equal"
		number = "number"
		adds = "additions"
		dels = "deletions"
		for pr in self.pulls:
			pr = pr.refresh()

			pdict = {
				pos : 0,
				neg : 0,
				neq : 0,
				adds : 0,
				dels : 0,
				number: ""

			}

			if pr.additions is None:
				pr.additions = 0

			if pr.deletions is None:
				pr.deletions = 0

			pdict[number] = pr.number
			pdict[adds] = pr.additions
			pdict[dels] = pr.deletions
			total = pr.additions - pr.deletions
			if total < 0:
				pdict[neg] = total
			elif total > 0:
				pdict[pos] = total
			else:
				pdict[neq] = total
			plist.append(pdict)

		return plist

	def repo_maintenance(self):
		rcontrib = "repo_contrib"
		rmaintain = "repo_maintain"
		number = "number"
		plist = []

		for pr in self.pulls:
			pr = pr.refresh()
			pdict = {
			rcontrib : 0,
			rmaintain : 0,
			number : "number"
			}

			pr = pr.refresh()
			files = pr.iter_files()
			for PullFile in files:
				fname = PullFile.filename.split(".")[1]
				pdict[number] = pr.number
				if fname == "md":
					pdict[rcontrib] += 1
				elif fname == "txt":
					pdict[rmaintain]+= 1
				else:
					pdict[rcontrib] += 1
				plist.append(pdict)

		return plist

	def open_issues(self):
		alist = []
		assigned = "assigned"
		nassigned = "not_assigned"
		iname = "assigned_name"
		number = "number"
		acount = {
			assigned : 0,
			nassigned : 0
		}
		for r in self.repo:

			issues = r.iter_issues(number=100, state='open')
			for i in issues:
				i = i.refresh()
				adict = {}

				assignee = str(i.assignee)

				adict[number] = i.number
				if assignee != "None":
					adict[iname] = assignee
					acount[assigned] += 1
				elif assignee == "None":
					acount[nassigned] += 1
				else:
					acount[assigned] += 1
				alist.append(adict)

		#Return a tuple of the count of assigned vs unassigned, and the specific issue information
		#rtup = (alist, acount)
		return alist


	def issue_comments(self, state='closed'):
		clist = []
		for r in self.repo:
			issues = r.iter_issues(number=100, state=state)
			rname = "repo_name"
			number = "issue_number"
			ncomments = "number_of_comments"

			for i in issues:
				cdict = {}
				i = i.refresh()
				cdict[rname] = r.name
				cdict[number] = i.number
				cdict[ncomments] = i.comments
				clist.append(cdict)

		return clist


	def pr_sentiment(self):
		#sentiment list
		slist = []
		comlist = []
		for pr in self.pulls:
			pr = pr.refresh()
			number = "number"
			body = "body"
			author = "comment_author"
			comment = pr.iter_comments()
			comments = comment.refresh()
			for c in comments:
				comdict = {}
				comdict[number] = pr.number
				comdict[body] = c.body
				user = c.user.refresh()
				comdict[author] = user.name
				comlist.append(comdict)

		for i in comlist:
			sdict = {}
			comment = i['body']
			number = i['number']
			author = i['comment_author']
			classifier = "classified_as"
			overall = "overall_positivity"
			blob = TextBlob(comment, analyzer=NaiveBayesAnalyzer())
			for sentences in blob.sentences:
				sent = sentences.sentiment
				sdict['comment'] = comment
				sdict['number'] = number
				sdict['author'] = author
				sdict[classifier] = sent[0]
				sdict[overall] = sent[1]
			slist.append(sdict)


		return slist

	def sentiment_repo_report(self):
		comlist = []
		slist = []
		rdict = {}
		rlist = []

			#This is a hack to to get the number of objects
			#Python doesn't normally have a len() attribute
			#for generator statements.
			#print("hey these are the releases", release)
			#for rls in r.iter_releases():
			#	print("here's in the loop")
			#	print(rls)
			#	print("after the loop")
			#print(release)
			#releases += len(release)

		for pr in self.pulls:
			pr = pr.refresh()
			repo = pr.repository[1]
			rdict['repository'] = repo


		for pr in self.pulls:
			pr = pr.refresh()
			number = "number"
			body = "body"
			author = "comment_author"
			comment = pr.iter_comments()
			comments = comment.refresh()

			for c in comments:
				comdict = {}
				comdict[number] = pr.number
				comdict[body] = c.body
				user = c.user.refresh()
				comdict[author] = user.name
				comlist.append(comdict)

		for i in comlist:
			sdict = {}
			comment = i['body']
			number = i['number']
			author = i['comment_author']
			classifier = "classified_as"
			overall = "overall_positivity"
			blob = TextBlob(comment, analyzer=NaiveBayesAnalyzer())
			for sentences in blob.sentences:
				sent = sentences.sentiment
				sdict['comment'] = comment
				sdict['number'] = number
				sdict['author'] = author
				sdict[classifier] = sent[0]
				sdict[overall] = sent[1]
			slist.append(sdict)

		overall = 0
		num_sentiments = len(slist)
		for s in slist:
			rating = s['overall_positivity']
			print(rating)
			overall += rating

		repo_rating = overall / num_sentiments

		rdict['overall_rating'] = repo_rating
		rlist.append(rdict)
		return rlist

