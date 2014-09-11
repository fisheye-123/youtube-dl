# coding: utf-8
from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..utils import (
    ExtractorError,
    compat_urllib_request,
    urlencode_postdata,
    xpath_with_ns,
)

_x = lambda p: xpath_with_ns(p, {'xspf': 'http://xspf.org/ns/0/'})
_find = lambda el, p: el.find(_x(p)).text.strip()


class NosVideoIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.)?nosvideo\.com/' + \
                 '(?:embed/|\?v=)(?P<id>[A-Za-z0-9]{12})/?'
    _PLAYLIST_URL = 'http://nosvideo.com/xml/{xml_id:s}.xml'
    _FILE_DELETED_REGEX = r'<b>File Not Found</b>'
    _TEST = {
        'url': 'http://nosvideo.com/?v=mu8fle7g7rpq',
        'md5': '6124ed47130d8be3eacae635b071e6b6',
        'info_dict': {
            'id': 'mu8fle7g7rpq',
            'ext': 'mp4',
            'title': 'big_buck_bunny_480p_surround-fix.avi.mp4',
            'thumbnail': 're:^https?://.*\.jpg$',
        }
    }

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        fields = {
            'id': video_id,
            'op': 'download1',
            'method_free': 'Continue to Video',
        }
        req = compat_urllib_request.Request(url, urlencode_postdata(fields))
        req.add_header('Content-type', 'application/x-www-form-urlencoded')
        webpage = self._download_webpage(req, video_id,
                                         'Downloading download page')
        if re.search(self._FILE_DELETED_REGEX, webpage) is not None:
            raise ExtractorError('Video %s does not exist' % video_id,
                                 expected=True)

        xml_id = self._search_regex(r'php\|([^\|]+)\|', webpage, 'XML ID')
        playlist_url = self._PLAYLIST_URL.format(xml_id=xml_id)
        playlist = self._download_xml(playlist_url, video_id)

        track = playlist.find(_x('.//xspf:track'))
        title = _find(track, './xspf:title')
        url = _find(track, './xspf:file')
        thumbnail = _find(track, './xspf:image')

        formats = [{
            'format_id': 'sd',
            'url': url,
        }]

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats,
        }
