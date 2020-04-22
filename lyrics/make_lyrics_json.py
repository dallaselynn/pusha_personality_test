import copy
import glob
import json
import re
import sys


class ExtractKV:
    '''extract for quiz'''
    @staticmethod
    def get_songs_from_file(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            song_list = data['songs'] if 'songs' in data else [data]

            return [ExtractKV.extract_song_data(s) for s in song_list]

    @staticmethod
    def extract_song_data(song_data):
        '''extract fields from a song dict'''
        song_title = song_data.get('full_title') or song_data.get('song_title')

        album_title = None
        if song_data.get('album'):
            album_title = song_data['album'].get('full_title')
        if not album_title:
            album_title = song_data.get('album_title')

        song_desc = None
        if 'description' in song_data:
            song_desc = song_data['description'].get('plain')
        if not song_desc:
            song_desc = song_data.get('song_description')



        return {
            'song_title': song_title,
            'lyrics': song_data['lyrics'],
            'song_art_image_url': song_data['song_art_image_url'],
            'album_title': album_title,
            'song_description': song_desc
        }

    @staticmethod
    def extract_pusha_verses(lyrics):
        '''from the lyrics string parse out the push verses'''

        verses = []

        VERSE_START_RE = re.compile(r'\[.+?:.+?\]', re.MULTILINE|re.DOTALL)
        matches = list(re.finditer(VERSE_START_RE, lyrics))

        for idx,m in enumerate(matches):
            if ('Pusha' in m.group()) or (':' not in m.group()):
                # print(f'found match {m.group()}')
                if idx == len(matches) - 1:
                    verse_text = lyrics[m.end():]
                else:
                    next_match = matches[idx + 1]
                    verse_text = lyrics[m.end():next_match.start()]

                verses.append((m.group(), verse_text))
            else:
                continue
                # print(f'skipping non-push match {m.group()}')

        return verses

    @staticmethod
    def extract_verse_objects(filename):
        verse_objects = []

        songs = ExtractKV.get_songs_from_file(filename)
        song_data = [ExtractKV.extract_song_data(s) for s in songs]

        for song in song_data:
            verses = ExtractKV.extract_pusha_verses(song['lyrics'])
            for v in verses:
                s = copy.deepcopy(song)
                del s['lyrics']
                s['verse_heading'] = v[0]
                s['verse'] = v[1]

                verse_objects.append(s)

        return verse_objects

    @staticmethod
    def make_verse_list(filenames):
        verse_list = []

        for filename in filenames:
            verse_list.extend(ExtractKV.extract_verse_objects(filename))

        return verse_list

if __name__ == '__main__':
    json_files = glob.glob(f'{sys.argv[1]}/*.json')
    verse_list = ExtractKV.make_verse_list(json_files)
    with open('pusha_verses.json', 'w') as f:
        json.dump(verse_list, f)
