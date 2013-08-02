"""
Script to create/update posts on codrspace.com
"""

import os
import json
import re
import requests
import sys

CREDENTIALS_FILE = os.path.expanduser('~/.codrspace_credentials')
BASE_URL = 'http://codrspace.com/api/v1/'

# FIXME: Allow users to specify slug in file they pass
#   - Maybe use first 2 lines of file to look like this:
#       title: <title>
#       slug: <slug>
#   - if no slug line exists just autogenerate one
#   - title is required


def _parse_args():
    """Parse arguments and return dict of parameters to pass to HTTP API"""

    # Subtract 1 for sys.argv[0], command name
    num_args = len(sys.argv) - 1

    if num_args < 1:
        print 'Must specify filename to post/update from via command-line'
        sys.exit(1)

    args = {}
    args['filename'] = sys.argv[1]

    if len(sys.argv) == 4:
        args['username'] = sys.argv[2]
        args['api_key'] = sys.argv[3]
    elif os.path.exists(CREDENTIALS_FILE):
        args.update(_get_creds_from_file(CREDENTIALS_FILE))
    else:
        print 'Must have "%s" credentials file or specify username/password on command-line'
        sys.exit(1)

    return args


def _append_message_and_raise_exception(error, message):
    """Append given string message to existing error and raise"""

    raise type(error), type(error)(error.message + '\n%s' % message), sys.exc_info()[2]


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


def update_post(filename, params):
    """
    Update a post from contents of filename and with given params dict

    params must contain 'title', 'content', and 'id' keys
    """

    data = _get_post_data(filename)
    headers = {'content-type': 'application/json'}
    _id = params.pop('id')

    url = '%spost/%d/' % (BASE_URL, _id)

    response = requests.put(url, data=json.dumps(data), headers=headers,
                            params=params)

    response.raise_for_status()

    print 'Post id %d updated, see changes at: %s' % (response.json['id'],
                                                      response.json['url'])


def create_post(filename, params):
    """
    Create post with contents of given filename and params query string dict

    params must contain 'title' and 'content'
    """

    data = _get_post_data(filename)
    headers = {'content-type': 'application/json'}
    url = '%spost/' % (BASE_URL)

    response = requests.post(url, data=json.dumps(data), headers=headers,
                             params=params)
    response.raise_for_status()

    print 'New post id %d created at: %s' % (response.json['id'],
                                             response.json['url'])


def _post_id_from_error(error):
    """Parse error message and status code for exisint post id"""

    # 400 code means post exists so
    status_code = error.response.status_code
    if status_code != 400:
        raise NotImplementedError('Unhandled API response code: %d' % (
                                                                status_code))

    err_msg = error.response.content
    m_obj = re.search('(id: \d+)', err_msg)

    if not m_obj:
        raise ValueError('Unable to parse error message for existing ID')

    tokens = m_obj.group().split(':')

    try:
        existing_id = int(tokens[1])
    except IndexError:
        raise IndexError('Message missing tokens (API error: "%s")' % (
                                                        err_msg))
    except ValueError:
        raise ValueError('Message missing integer id (API error: "%s")' % (
                                                        err_msg))

    return existing_id


def main():
    """Main"""

    params = _parse_args()
    filename = params.pop('filename')

    try:
        create_post(filename, params)
    except requests.exceptions.HTTPError as err:
        # FIXME: Add this as a command line param, update post or force user to
        # change title to generate new slug

        params['id'] = _post_id_from_error(err)

        try:
            update_post(filename, params)
        except requests.exceptions.HTTPError as err:
            msg = 'Failed creating new post and updating existing post'
            _append_message_and_raise_exception(err, msg)


if __name__ == '__main__':
    main()
