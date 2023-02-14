import json
import os

import requests
import subprocess

url = 'https://api.github.com/repos/{owner}/{repo}/commits'
owner = 'andrei219'
repo = 'euromedia'

''' Get the latest commit hash from github '''
def get_latest_commit_hash_and_message():
	_url = url.format(owner=owner, repo=repo)

	headers = {'Authorization': 'Token ' + os.environ['GITHUB_AUTH']}
	try:

		response = requests.get(_url, headers=headers)

	except requests.exceptions.RequestException as e:
		return None, None

	if response.status_code == 200:
		commit = response.json()[0]['sha']
		message = response.json()[0]['commit']['message']
		return commit, message

	return None, None

def get_current_commit_hash():
	""" Get the current commit hash from git """
	commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
	return commit_hash.decode('utf-8').strip()

def check_update_available():

	latest_commit_hash, message = get_latest_commit_hash_and_message()
	current_commit_hash = get_current_commit_hash()

	if latest_commit_hash != current_commit_hash:
		return message

if __name__ == '__main__':

    print(get_latest_commit_hash_and_message())
    print(get_current_commit_hash())


