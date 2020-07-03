"""
Fetchartist plugin for beets.
"""
import os
import re
import pylast
import requests

from bs4 import BeautifulSoup

from beets import config
from beets import plugins
from beets import ui
from beets import util as beetsutil

from beetsplug import util

CONTENT_TYPES = ["image/png", "image/jpeg"]
FILE_TYPES = ['png', 'jpg']

CONTENT_TYPE_TO_EXTENSION_MAP = {
    "image/png": "png",
    "image/jpeg": "jpg"
}

COVER_NAME_KEY = "filename"

class ArtistInfo(object):
    """
    Contains information about an artist, like it's name, paths that point to
    its covers and the cover itself.
    """
    def __init__(self, name):
        self.name = name
        self.paths = set()
        self.cover = None
        self.extension = None
        self.remaining_paths = set()

    def add_path(self, path):
        """
        Adds a cover path to this artist.
        """
        self.paths.add(path)

    def get_write_paths(self, force):
        """
        If there are remaining paths set, only covers at those paths don't
        exist and need to be written. Otherwise all paths are returned. If
        force is set, all covers should be written again.
        """
        write_paths = self.paths

        if not force and self.remaining_paths:
            write_paths = self.remaining_paths

        return [path + "." + self.extension for path in write_paths]

    def __repr__(self):
        return "ArtistInfo<name=%s,paths=%r>" % (self.name, self.paths)


class FetchArtistPlugin(plugins.BeetsPlugin):
    """
    The fetchart plugin.
    """
    def __init__(self):
        super(FetchArtistPlugin, self).__init__()

        self._last_fm = pylast.LastFMNetwork(api_key=plugins.LASTFM_KEY)

        self.config.add({
            COVER_NAME_KEY: ""
        })

        self._process_config()
        self._create_path_templates()

    def _process_config(self):
        self._cover_name = self.config[COVER_NAME_KEY].get().strip()
        if not self._cover_name:
            self._cover_name = None

    def _create_path_templates(self):
        self._library_path = config["directory"].get()
        self._default_template = util.strip_template_path_suffix(
            config["paths"]["default"].get(), "$albumartist")
        self._singleton_template = util.strip_template_path_suffix(
            config["paths"]["singleton"].get(), "$artist")

    def commands(self):
        cmd = ui.Subcommand("fetchartist", help="download artist art")
        cmd.parser.add_option("-f", "--force", dest="force",
                              action="store_true", default=False,
                              help="force overwrite existing artist covers")

        def _func(lib, opts, args):
            self._fetch_artist(lib.items(ui.decargs(args)), opts.force)

        cmd.func = _func
        return [cmd]

    @staticmethod
    def _get_artist_from_item(item):
        """
        Returns an appropriate artist name for the given item. If the given item is
        part of an album, the albumartist, otherwise the artist is returned.
        """
        if item.singleton:
            return item.artist

        return item.albumartist

    def _get_cover_name(self, item):
        if self._cover_name:
            return self._cover_name

        return FetchArtistPlugin._get_artist_from_item(item)

    def _create_cover_path(self, item):
        if item.singleton:
            template = self._singleton_template
        else:
            template = self._default_template

        evaluated_template = item.evaluate_template(template)
        cover_name = self._get_cover_name(item)
        path = os.path.join(evaluated_template, cover_name)

        return os.path.join(self._library_path, beetsutil.sanitize_path(path))

    def _create_artist_infos(self, items):
        artist_infos = dict()

        for item in items:
            # compilations don't need artist covers
            if item.comp:
                continue

            artist = FetchArtistPlugin._get_artist_from_item(item)

            artist_info = artist_infos.get(artist)
            if artist_info is None:
                artist_info = ArtistInfo(artist)
                artist_infos[artist] = artist_info

            artist_info.add_path(self._create_cover_path(item))

        return sorted(artist_infos.values(), key=lambda a: a.name)

    @staticmethod
    def _check_for_existing_covers(artist_info):
        existing_paths, missing_paths = util.find_existing_and_missing_files(artist_info.paths, FILE_TYPES)
        artist_info.remaining_paths = missing_paths

        # return false if there are no covers at all
        if not existing_paths:
            return False

        # return true when there are all covers
        if not missing_paths:
            return True

        # TODO ask the user if only some covers exist
        return False

    def _request_cover(self, artist_name):
        artist = self._last_fm.get_artist(artist_name)
        url = artist.get_url()

        if not url:
            return None

        headers = {"Accept-Language": "en-US, en;q=0.5"}
        results = requests.get(url, headers=headers)

        # cover art endpoint was removed so this parses the html
        soup = BeautifulSoup(results.text, "html.parser")

        # artist image will show up in this element
        search = soup.find_all('div', class_='header-new-background-image')
        if not search:
            return None

        # image is set as the background url
        image = search[0]['style']

        # strip url from style
        cover = re.search('\(([^)]+)', image).group(1)

        # this is a custom value that improves the image quality
        cover = cover.replace('/ar0/', '/770x0/')
        cover = cover.replace('.jpg', '.png')
        response = requests.get(cover, stream=True)

        content_type = response.headers.get('Content-Type')
        if content_type is None or content_type not in CONTENT_TYPES:
            self._log.debug(u"not a supported image: {}", content_type or 'no content type')
            return None

        extension = CONTENT_TYPE_TO_EXTENSION_MAP[content_type]
        return (response, extension)

    def _fetch_cover(self, artist_info):
        result = self._request_cover(artist_info.name)
        if result is None:
            return False

        artist_info.cover, artist_info.extension = result
        return True

    def _write_covers(self, artist_info, force):
        for path in artist_info.get_write_paths(force):
            if not os.path.exists(os.path.dirname(path)):
                self._log.error('path: {}', path)
                return False

            self._log.debug(u"saving cover at '{}'".format(path))
            with open(path, "wb") as target:
                for chunk in artist_info.cover.iter_content(chunk_size=128):
                    target.write(chunk)

        return True

    def _update_cover(self, artist_info, force):
        all_exist = FetchArtistPlugin._check_for_existing_covers(artist_info)
        if force or not all_exist:
            if self._fetch_cover(artist_info):
                if self._write_covers(artist_info, force):
                    message = ui.colorize('text_success', 'artist cover found')
                else:
                    message = ui.colorize('text_error', 'path not found')
            else:
                message = ui.colorize('text_error', 'no artist cover found')
        else:
            message = ui.colorize('text_highlight_minor', 'has artist cover')

        self._log.info(u'{0}: {1}', artist_info.name, message)

    def _fetch_artist(self, items, force):
        artist_infos = self._create_artist_infos(items)
        for artist_info in artist_infos:
            self._update_cover(artist_info, force)
