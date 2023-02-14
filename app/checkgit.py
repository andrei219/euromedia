import json

import requests
import subprocess

user = 'andrei219'

''' Get the latest commit hash from github '''
def get_latest_commit_hash_and_message():
	url = f"https://api.github.com/users/{user}/events/public"

	try:
		response = requests.get(url)
	except requests.exceptions.RequestException as e:
		return None, None

	if response.status_code == 200:
		commit_hash = response.json()[0]['payload']['commits'][-1]['sha']
		message = response.json()[0]['payload']['commits'][-1]['message']

		return commit_hash, message


def get_current_commit_hash():
	""" Get the current commit hash from git """
	commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'])
	return commit_hash.decode('utf-8').strip()

def check_update_available():

	latest_commit_hash, message = get_latest_commit_hash_and_message()
	current_commit_hash = get_current_commit_hash()

	if latest_commit_hash != current_commit_hash:
		return message
	else:
		return None


if __name__ == '__main__':

    print(get_latest_commit_hash_and_message())
    print(get_current_commit_hash())





