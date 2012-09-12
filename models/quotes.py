import sqlite3

from core import app

db = sqlite3.connect(app.config['DB_PATH'])

class Episode(object):
    def __init__(self, eid=None, uid=None):
        c = db.cursor()

        if eid is None and uid is not None:
            c.execute('''SELECT episode_id
                         FROM utterance
                         WHERE id = ?
                         ''', (uid,))
            eid, = c.fetchone()

        if eid is None:
            raise ValueError('no eid given or found')

        self.eid = eid

        c.execute('''SELECT season_number, episode_number, title
                     FROM episode
                     WHERE id = ?
                     ''', (eid,))
        row = c.fetchone()
        self.season, self.number, self.title = row


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

        eid = None
        if speaker is None:
            c.execute('''SELECT speaker, episode_id
                         FROM utterance
                         WHERE id = ?
                         ''', (uid,))
            speaker, eid = c.fetchone()
        self.speaker = speaker

        if episode is None:
            episode = Episode(eid, self.uid)
        self.episode = episode


class Passage(object):
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

        self.quotes = [Quote(uid, speaker) for uid, speaker in rows]

    @classmethod
    def random(cls, subject=None):
        c = db.cursor()

        if subject is None:
            app.logger.debug('searching for random passage')
            c.execute('''SELECT id
                         FROM utterance
                         ORDER BY RANDOM()
                         LIMIT 1
                         ''')

        else:
            app.logger.debug('searching for random passage matching {}'.format(subject))
            c.execute('''SELECT utterance_id
                         FROM sentence
                         WHERE text LIKE ?
                         ORDER BY RANDOM()
                         LIMIT 1
                         ''', ('%{}%'.format(subject),))

        result = c.fetchone()
        app.logger.debug('search result: {}'.format(result))

        if result is None:
            return None

        uid, = result
        return Passage(uid=uid)

