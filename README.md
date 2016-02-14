# fetchartist plugin for beets

A plugin that fetches artist covers from last.fm.

## Installation

The plugin requires `pylast` and `requests` which can be installed using `pip`:

	sudo pip install pylast requests

Afterwards Beets has to be configured to use the plugin, for example:

	pluginpath:
		~/git/fetchartist/beetsplug

	plugins: fetchartist

## Configuration

The configuration is done in the fetchartist section:

	fetchartist:
		cover_name: ""

* cover_name: If set the value will be used as filename for the artist covers.
  If it is empty, the artist's name will be used instead. Default: `""`

## Usage

	Usage: beet fetchartist [options]

	Options:
	-h, --help   show this help message and exit
	-f, --force  force overwrite existing artist covers

Automatically fetching artist covers during import is not supported yet.
