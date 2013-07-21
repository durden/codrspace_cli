"""
Script to create/update posts on codrspace.com
"""

import os
import json
import requests
import sys

CREDENTIALS_FILE = os.path.expanduser('~/.codrspace_credentials')

# FIXME: Allow users to specify slug in file they pass
#   - Maybe use first 2 lines of file to look like this:
#       title: <title>
#       slug: <slug>
#   - if no slug line exists just autogenerate one
#   - title is required


def _get_creds_from_file(filename):
    """
    Read given filename for required credentials to interact with codrspace
    api

    File should be organized as key=value pairs and contain at least 2 valid
    keys: 'username' and 'api_key'
    """

    creds = {'username': None, 'api_key': None}

    with open(filename, 'r') as f:
        for line in f:
            try:
                key, value = line.split('=')
            except ValueError:
                raise ValueError('Invalid config line, should be key=value')

            key = key.strip()
            value = value.strip()

            if key in creds:
                creds[key] = value

    if None in creds.values():
        raise KeyError('Credentials file requires both username and password')

    return creds


def _get_post_data(filename):
    """
    Read data from filename that should be used in codrspace post

    First line of file is assumed to be the title of the post
    """

    data = {}
    with open(filename, 'r') as f:
        data['title'] = f.readline()
        data['content'] = ''.join(f.readlines())

    return data


def _create_or_update_post(filename, params):
    """Create or update post with contents of given filename"""

    data = _get_post_data(filename)

    url = 'http://codrspace.com/api/v1/post/'
    headers = {'content-type': 'application/json'}

    response = requests.post(url, data=json.dumps(data), headers=headers,
                             params=params)
    print response

    # Response 400 means slug already exists so we should update the post

    # FIXME: Maybe we should ask user if they want to update the post or not?

    # FIXME: Update line 150 on aps/codrspace/forms.py to include id in error
    # message

def main():
    """Main"""

    # Subtract 1 for sys.argv[0], command name
    num_args = len(sys.argv) - 1

    if num_args < 1:
        print 'Must specify filename to post/update from via command-line'
        sys.exit(1)

    filename = sys.argv[1]

    if os.path.exists(CREDENTIALS_FILE):
        params = _get_creds_from_file(CREDENTIALS_FILE)
    elif len(sys.argv) == 4:
        params = {}
        params['username'] = sys.argv[2]
        params['api_key'] = sys.argv[3]
    else:
        print 'Must have "%s" credentials file or specify username/password on command-line'
        sys.exit(1)

    _create_or_update_post(filename, params)


if __name__ == '__main__':
    main()
