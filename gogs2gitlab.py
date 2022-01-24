import os
import configparser
import requests
import json


class Repo(object):

    def __init__(self, name, full_name, description, import_url):
        self.name = name
        self.full_name = full_name
        self.description = description
        self.visibility = 'private'
        self.import_url = import_url


class Provider(object):
    def __init__(self, proto, host, user, password, token, endpoint):
        self.protocol = proto
        self.host = host
        self.user = user
        self.token = token
        self.password = password
        self.endpoint = endpoint

    def get_repos(self):
        resp = requests.get(
                "{protocol}{host}{endpoint}".format(
                    protocol=self.protocol,
                    host=self.host,
                    endpoint=self.endpoint),
                headers={"Authorization": "token {}".format(self.token)}
            )
        data = json.loads(resp.text)
        repos = []
        for item in data:
            import_url = '{protocol}{user}:{password}@{host}/{repo}'.format(
                    protocol=self.protocol,
                    user=self.user,
                    password=self.password,
                    host=self.host,
                    repo=item['full_name'])
            repo = Repo(name=item['name'], full_name=item['full_name'],
                        description=item['description'],
                        import_url=import_url)
            repos.append(repo)
        return repos

    def put_repo(self, repo):
        print('   Importing {repo}'.format(repo=repo.name))
        resp = requests.post(
                "{protocol}{host}{endpoint}".format(
                    protocol=self.protocol,
                    host=self.host,
                    endpoint=self.endpoint),
                headers={"Private-Token": "{}".format(self.token)},
                data=repo.__dict__
            )
        if resp:
            print('✅ OK')
        else:
            print('❌ KO -> {error}'.format(error=json.loads(resp.text)))


if __name__ == '__main__':
    # Read config file (need to fake .ini section in order to use configparser)
    try:
        home = os.path.expanduser('~')
        cfile = '{home}/.config/gogs2gitlab/gogs2gitlab.ini'.format(home=home)
        with open(cfile, 'r') as f:
            cfg_string = '[default]\n' + f.read()
        config = configparser.ConfigParser()
        config.read_string(cfg_string)
    except Exception as e:
        print(e)
    # Define providers
    gogs = Provider(
            proto=config['default']['gogs_proto'],
            host=config['default']['gogs_host'],
            user=config['default']['gogs_user'],
            token=config['default']['gogs_token'],
            password=config['default']['gogs_pass'],
            endpoint='/api/v1/user/repos')
    gitlab = Provider(
            proto=config['default']['gitlab_proto'],
            host=config['default']['gitlab_host'],
            user='',
            password='',
            token=config['default']['gitlab_token'],
            endpoint='/api/v4/projects')
    # Start the game
    repos = gogs.get_repos()
    for repo in repos:
        print('➡️  {repo}'.format(repo=repo.name))
        gitlab.put_repo(repo)
