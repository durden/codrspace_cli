import io
import time
import json as json_mod
import re
import os

import click
import requests

import create

DOMAIN = 'http://codrspace.com/'

VERBOSITY = 0


def get_posts_from_json_file(filename, max_count):
    # max_count == 0 means 'all'

    with open(filename, 'r') as file_obj:
        data = file_obj.read()

    for ii, post in enumerate(json_mod.loads(data)['objects']):
        yield post

        if max_count > 0 and ii > max_count:
            raise StopIteration


def get_posts(creds, max_count, cache=False):
    # max_count == 0 means 'all'

    def send(url):
        if VERBOSITY > 1:
            print 'sending', url

        response = requests.get(url, params=creds)
        response.raise_for_status()
        return response.json()

    headers = {'content-type': 'application/json'}
    url = '%s/post/' % (create.BASE_URL)

    json = None

    ii = 1
    while True:
        if json is None:
            json = send(url)
        else:
            json = send('%s%s' % (DOMAIN, json['meta']['next']))

        if cache:
            with open('request_%d.json' % (ii), 'w+') as file_obj:
                file_obj.write(json_mod.dump(json, ensure_ascii=False))

        ii += 1

        for cnt, post in enumerate(json['objects'], 1):
            if max_count > 0 and cnt > max_count:
                raise StopIteration

            yield post

        if json['meta']['next'] is None:
            raise StopIteration


def _gist_replacement(str_, username):
    pattern = re.compile('\[gist (\d+) *\]', flags=re.IGNORECASE)
    gist_url = '[https://gist.github.com/{username}/{id}](https://gist.github.com/{username}/{id})'

    return pattern.sub(
                lambda m: gist_url.format(username=username, id=m.group(1)),
                str_)


def _code_replacement(str_):
    gh_pattern = re.compile("```(?P<lang>[^\\n\\s`]+)+?(?P<code>[^```]+)+?```",
                            re.I | re.S | re.M)
    code_pattern = re.compile('\\[code(\\s+lang=\"(?P<lang>[\\w]+)\")*\\](?P<code>.*?)\\[/code\\]',
                              re.I | re.S | re.M)

    str_ = gh_pattern.sub(lambda m: '<pre>%s</pre>' % (m.group('code')), str_)
    return code_pattern.sub(lambda m: '<pre>%s</pre>' % (m.group('code')), str_)



def _codrspace_tags_to_html(str_, title, username):
    str_ = _gist_replacement(str_, username)
    str_ = _code_replacement(str_)

    local_pattern = re.compile('\[local (\S+) *\]', flags=re.IGNORECASE)
    if local_pattern.search(str_) is not None:
        print 'Article "%s" contains [local] which must be manually resolved' % (title)

    return str_


def _update_timestamp(filename, post_date):
    """
    We set the utime AND put publish date in the file b/c pushing to heroku
    will actually change the timestamps so we have to use it from inside the
    file.
    """

    publish_dt = time.strptime(post_date, '%Y-%m-%dT%H:%M:%S')
    file_time = time.mktime(publish_dt)
    os.utime(filename, (file_time, file_time))

    # Return string representation
    return time.strftime('%m-%d-%Y %H:%M:%S', publish_dt)


def _write_file(filename, post, tag, username, require_published=True):
    if require_published and post['status'] != 'published':
        if VERBOSITY > 1:
            print 'Skipping %s, not published yet' % (post['slug'])

        return

    # Some reason codrspace exports with windows line endings
    newline_cleanup = lambda txt: txt.replace('\r\n', '\n')

    try:
        with io.open(filename, 'w', encoding='utf-8') as file_obj:
            # Update file timestamp and get string formatted timestamp

            # FIXME: need to do this at the end after writing ot file.
            publish_dt = _update_timestamp(filename, post['publish_dt'])

            # First line will always be publish date
            file_obj.write(unicode(publish_dt + '\n'))

            file_obj.write(unicode(post['title'] + '\n'))
            file_obj.write(unicode(tag + '\n\n'))
            file_obj.write(unicode('# %s\n' % (post['title'])))

            content = _codrspace_tags_to_html(post['content'],
                                              post['title'],
                                              username)
            file_obj.write(unicode(newline_cleanup(content)))
    except UnicodeEncodeError, err:
        print 'Failed writing %s (%s)' % (filename, err)
        os.unlink(filename)
    else:
        if VERBOSITY:
            print 'Wrote', filename

# Use -h in addition to --help
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    pass


@cli.command()
@click.argument('output_dir')
@click.argument('tag')
@click.option('-v', '--verbose', count=True)
@click.option('--count', default=0, type=int, show_default=False,
              help='Max number of posts to retrive')
def from_http(output_dir, tag, count, verbose):
    global VERBOSITY
    VERBOSITY = verbose

    creds = create._get_creds_from_file(create.CREDENTIALS_FILE)
    for post in get_posts(creds, int(count)):
        filename = '%s.md' % (os.path.join(output_dir, post['slug']))
        _write_file(filename, post, tag, creds['username'])


@cli.command()
@click.argument('json_file')
@click.argument('output_dir')
@click.argument('tag')
@click.argument('username')
@click.option('-v', '--verbose', count=True)
@click.option('--count', default=0, type=int, show_default=False,
              help='Max number of posts to retrive')
def from_file(json_file, output_dir, tag, username, count, verbose):
    global VERBOSITY
    VERBOSITY = verbose

    for post in get_posts_from_json_file(json_file, int(count)):
        filename = '%s.md' % (os.path.join(output_dir, post['slug']))
        _write_file(filename, post, tag, username)


if __name__ == '__main__':
    cli()
