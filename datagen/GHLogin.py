#!/usr/bin/env python3
import github3


class Login:
	def __init__(self, username, token):
		self.username = username
		self.token = token

	def authenticate(self):
		return github3.login(username=self.username, token=self.token)
	
	def authenticate_ghe(self):
		site = input("Please enter your GHE instance URL\n>")
		return github3.login(username=self.username, token=self.token, url=site)

