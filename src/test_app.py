from app import app, g, CURR_USER_KEY
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, Greeting, Person, Relationship

# use a test db
os.environ['DATABASE_URL'] = "postgresql:///auguri-test"


# create the tables, once for all tests. for each test, we will delete all data and add new.
db.create_all()


app.config['WTF_CSRF_ENABLED'] = False


class AppViewTestCase(TestCase):
    """ Test if application loads proper html """

    def setUp(self):
        db.drop_all()
        db.create_all()

        p1 = Person.signup(email_address="test1@gmail.com", first_name="Test1_first",
                           last_name="Test1_last", img_url="", birthday="2001-01-01", username="test1", password="password1")
        pid1 = 1001
        p1.id = pid1

        p2 = Person.signup(email_address="test2@gmail.com", first_name="Test2_first",
                           last_name="Test2_last", img_url="", birthday="2002-02-02", username="test2", password="password2")
        pid2 = 1002
        p2.id = pid2

        db.session.commit()

        p1 = Person.query.get(pid1)
        p2 = Person.query.get(pid2)

        self.p1 = p1
        self.pid1 = pid1

        self.p2 = p2
        self.pid2 = pid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_1_homepage(self):
        p = Person.authenticate(self.p1.username, "password1")
        with self.client as c:

            # while not logged in, it should redirect to the welcome page
            resp = c.get("/birthdays")
            self.assertEqual(resp.status_code, 302)

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.p1.id

            # once logged in, it should keep you on the bday main page.
            resp = c.get("/birthdays")
            self.assertEqual(resp.status_code, 200)

    def test_2_view_friend(self):
        p3 = Person.signup(email_address="test3@gmail.com", first_name="Test3_first",
                           last_name="Test3_last", img_url="", birthday="2003-03-03", username="test3", password="password1")
        pid3 = 1003
        p3.id = pid3
        db.session.commit()

        new_rel = Relationship(user_id=1001, friend_id=1003)
        db.session.add(new_rel)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.p1.id
                g.person = Person.query.get(self.p1.id)

                resp = c.get("/friend/1003")
                print('***********************************************')
                print(resp.data)
                print('***********************************************')
                self.assertEqual(resp.status_code, 200)

    # def test_3_(self):
    # def test_4_(self):
    # def test_5_(self):
