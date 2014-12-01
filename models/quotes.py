# Copyright 2014 John Reese
# Licensed under the MIT license

import random
import re
import sqlite3

from core import app, Cacheable
from models import amazon_links

wordre = re.compile(r'[\w\']+')
db = sqlite3.connect(app.config['DB_PATH'])

class Episode(object):
    __metaclass__ = Cacheable

    def __init__(self, eid):
        self.eid = eid

        c = db.cursor()
        c.execute('''SELECT season_number, episode_number, title
                     FROM episode
                     WHERE id = ?
                     ''', (eid,))
        row = c.fetchone()
        self.season, self.number, self.title = row
        self.amazon_title, self.amazon_url, self.amazon_img = amazon_links[self.season]

        self.cache()


class Quote(object):
    def __init__(self, uid, speaker=None, episode=None):
        self.uid = uid

        c = db.cursor()
        c.execute('''SELECT text
                     FROM sentence
                     WHERE utterance_id = ?
                     ORDER BY sentence_number
                     ''', (uid,))
        rows = c.fetchall()

        if len(rows) < 1:
            raise KeyError('No quote found with ID {}'.format(uid))

        self.text = ' '.join([text for text, in rows])

        if speaker is None or episode is None:
            c.execute('''SELECT speaker, episode_id
                         FROM utterance
                         WHERE id = ?
                         ''', (uid,))
            speaker, eid = c.fetchone()
        self.speaker = speaker

        if episode is None:
            episode = Episode(eid)
        self.episode = episode


class Passage(object):
    __metaclass__ = Cacheable

    highest_uid = 52206 # SELECT id FROM utterance ORDER BY id DESC LIMIT 1

    def __init__(self, uid):
        self.uid = uid

        c = db.cursor()

        c.execute('''SELECT episode_id, utterance_number
                     FROM utterance
                     WHERE id = ?
                     ''', (uid,))
        row = c.fetchone()

        if row is None:
            raise KeyError('utterance id {} not found'.format(uid))

        self.episode_id, utterance_number = row
        self.episode = Episode(self.episode_id)

        if utterance_number > 2:
            utterance_start = utterance_number - 2
        else:
            utterance_start = 1
        utterance_end = utterance_start + 4

        c.execute('''SELECT id, speaker
                     FROM utterance
                     WHERE episode_id = ?
                        AND utterance_number >= ?
                        AND utterance_number <= ?
                     ORDER BY id
                     ''', (self.episode_id, utterance_start, utterance_end))
        rows = c.fetchall()

        self.quotes = []
        for uid, speaker in rows:
            if uid == self.uid:
                self.speaker = speaker
            self.quotes.append(Quote(uid, speaker, self.episode))

        self.cache()

    @classmethod
    def random(cls, subject=None, speaker=None):
        c = db.cursor()

        if not subject and not speaker:
            uid = random.randint(1, cls.highest_uid)

        else:
            conditions = []
            params = []

            if subject:
                words = wordre.findall(subject)
                for word in words:
                    conditions.append('text LIKE ?')
                    params.append('%{}%'.format(word))

            if speaker:
                conditions.append('''utterance_id IN (
                                        SELECT id
                                        FROM utterance
                                        WHERE speaker LIKE ?
                                     )''')
                params.append(speaker)

            where = ' AND '.join(conditions)

            app.logger.debug('search clause: "{}", params: {}'.format(where, params))
            c.execute('''SELECT utterance_id
                         FROM sentence
                         WHERE {}
                         ORDER BY RANDOM()
                         LIMIT 1
                         '''.format(where), params)
            result = c.fetchone()

            if result is None:
                return None

            uid, = result

        return Passage(uid)

def warmup():
    c = db.cursor()
    c.execute('''SELECT id
                 FROM utterance
                 ORDER BY id DESC
                 LIMIT 1
                 ''')
    highest_uid, = c.fetchone()

    marker = 0
    for uid in range(1, highest_uid):
        Passage(uid)

        if uid >= marker + 100:
            print uid
            marker = uid

    print uid
