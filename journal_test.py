import unittest
import datetime

from playhouse.test_utils import test_database
from peewee import *

import journal
from models import User, BlogEntry


TEST_DB = SqliteDatabase(':memory:')
TEST_DB.connect()
TEST_DB.create_tables([User, BlogEntry], safe=True)

USER_DATA = {
    'username': 'user_test',
    'password': 'password'
}

REGISTER_DATA = {
    'username': 'user_test',
    'password': 'password',
    'password2': 'password'
}

class UserModelTestCase(unittest.TestCase):
    @staticmethod
    def create_users(count=2):
        for i in range(count):
            User.create_user(
                username='user_test{}'.format(i),
                password='password'
            )

    def test_create_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            self.assertEqual(User.select().count(), 2)
            self.assertNotEqual(
            User.select().get().password, 'password')

    def test_duplicate_user(self):
        with test_database(TEST_DB, (User,)):
            self.create_users()
            with self.assertRaises(ValueError):
                User.create_user(
                    username='user_test1',
                    password='password',
                )



class ViewTestCase(unittest.TestCase):
    def setup(self):
        journal.app.config['TESTING'] = True
        journal.app.config['WTF_CSRF_ENABLED'] = False
        self.app = journal.app.test_client()

class UserViewTestCase(ViewTestCase):
    def test_registration(self):
        with test_database(TEST_DB, (User,)):
            rv = journal.app.test_client().post('/register', data=REGISTER_DATA)
            #self.assertEqual(rv.status_code, 302)
            #self.assertEqual(rv.slocation, 'http://localhost/')

    def test_good_login(self):
        with test_database(TEST_DB, (User,)):
            UserModelTestCase.create_users()
            rv = journal.app.test_client().post('/login', data=USER_DATA, )
            self.assertEqual(rv.status_code, 302)
            #self.assertEqual(rv.location, 'http://localhost/')

    def test_bad_login(self):
        with test_database(TEST_DB, (User,)):
            rv = journal.app.test_client().post('/login', data=USER_DATA)
            #self.assertEqual(rv.status_code, 200)

#    def test_logout(self):
#       with test_database(TEST_DB, (User,)):
#            UserModelTestCase.create_users()
#            journal.app.test_client().post('/login', data=USER_DATA)

#            rv = journal.app.test_client().get('/logout')
#           self.assertEqual(rv.status_code, 302)
#           self.assertEqual(rv.location, 'http://localhost/')



class BlogEntryTestCase(unittest.TestCase):
    def test_blog_creation(self):
        with test_database(TEST_DB, (User, BlogEntry)):
            UserModelTestCase.create_users()
            user = User.select().get()
            BlogEntry.create_entry(
                title="This is a blog",
                date = "05/19/2017",
                time_spent="1 hr",
                learned="I learned that this works",
                resources="the internet",
                tags="#blog",
                user=user,
                )

            entry = BlogEntry.select().get()

            self.assertEqual(
                entry.select().count(),
                1
            )
            self.assertEqual(entry.user, user)








if __name__ == "__main__":
    unittest.main()
