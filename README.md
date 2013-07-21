# Codrspace CLI

This repository contains code to interact with the
[codrspace](http://codrspace.com) API via the command-line.


## Usage

`python codrspace_cli.py <filename> [username] [api_key]`

You may omit the `username` and `api_key` in the command-line arguments if you
create a file that contains this information in `~/.codrspace_credentials`.
This file should be of the following format:

username=my_codrspace_username
api_key=my_codrspace_api_key

You can get the above information by logging into your codrspace blog and going
to the Settings->API Settings page, `http://codrspace.com/api-settings/`.
