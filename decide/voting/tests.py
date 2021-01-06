import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
User=get_user_model()
from django.test import TestCase
from django.db.utils import IntegrityError
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption
from django.db.utils import IntegrityError
from .admin import give_message
import sys



class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question', option_types=1,type=0)
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(id=1,name='test voting')
        
        v.save()
        v.question.add(q)
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    
    def create_question(self):
        q = Question(desc='test question')
        q.save()
        return q

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.sex = 'M'
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for q in v.question.all():
            for opt in q.options.all():
                clear[opt.number] = 0
                for i in range(random.randint(0, 5)):
                    a, b = self.encrypt_msg(opt.number, v)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user = self.get_or_create_user(voter.voter_id)
                    self.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
        return clear
   
    
    # def test_question_unique(self):
    #     v = self.create_question()
    #     with self.assertRaises(Exception) as raised:
    #         self.create_question()
    #     self.assertEqual(IntegrityError, type(raised.exception))

    # def test_duplicate_voting_name(self):
    #     v1 = self.create_voting()
    #     with self.assertRaises(Exception) as raised:
    #         v2 = self.create_voting()
    #     self.assertEqual(IntegrityError, type(raised.exception))
    
    def store_votes_unique_option(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        for i in range(1):
            main_voter = self.get_or_create_user(voter.voter_id)
            self.login(user=main_voter.username)
            votos = []
            qs = v.question.all()
            for q in qs:
                options = q.options.all()
                count_options = len(options)

                a,b = None, None
                for j in range(1):
                    chosen_option = options[0]
                    
                    x, y = self.encrypt_msg(chosen_option.number, v)

                    if a and b: 
                        a = a + ',' + str(x) + ''
                        b = b + ',' + str(y) + ''
                        
                    else:
                        a = str(x)
                        b = str(y)
                        
                    votos.append({'a': a, 'b': b })
                
            data = {
                'voting': v.id,
                'voter': voter.voter_id,
                'vote': votos,
                'question_id': q.id,
                'token': self.token
            }                

            mods.post('store', json=data)
            self.logout()
            voter = voters.pop()
    
    def test_tally_message_positive(self):
        voting = self.create_voting()
        self.create_voters(voting)
        voting.create_pubkey()
        
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        self.store_votes_unique_option(voting)
        
        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')
        
        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        tally=voting.tally_votes(self.token)
        
        mensajeEsperado="For voting test voting: for question test question for option option 1 it has 1 votes,  for option option 2 it has 0 votes,  for option option 3 it has 0 votes,  for option option 4 it has 0 votes,  for option option 5 it has 0 votes."
        mensajeObtenido=give_message(voting,tally)
        
        self.assertEqual(mensajeEsperado, mensajeObtenido)

    def test_tally_message_negative(self):
        voting = self.create_voting()
        self.create_voters(voting)
        voting.create_pubkey()
        
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        self.store_votes_unique_option(voting)
        
        data = {'action': 'stop'}
        self.login()
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')
        
        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')
        tally=voting.tally_votes(self.token)
        
        mensajeEsperado="For voting test bad voting : for question test question for option option 1 it has 0 votes,  for option option 2 it has 0 votes,  for option option 3 it has 1 votes,  for option option 4 it has 0 votes,  for option option 5 it has 0 votes."
        mensajeObtenido=give_message(voting,tally)
        
        self.assertNotEqual(mensajeEsperado, mensajeObtenido)

    
        

    # def test_update_voting(self):
    #     voting = self.create_voting()

    #     data = {'action': 'start'}
    #     #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
    #     #self.assertEqual(response.status_code, 401)

    #     # login with user no admin
    #     self.login(user='noadmin')
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 403)

    #     # login with user admin
    #     self.login()
    #     data = {'action': 'bad'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)

    #     # STATUS VOTING: not started
    #     for action in ['stop', 'tally']:
    #         data = {'action': action}
    #         response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #         self.assertEqual(response.status_code, 400)
    #         self.assertEqual(response.json(), 'Voting is not started')

    #     data = {'action': 'start'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), 'Voting started')

    #     # STATUS VOTING: started
    #     data = {'action': 'start'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already started')

    #     data = {'action': 'tally'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting is not stopped')

    #     data = {'action': 'stop'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), 'Voting stopped')

    #     # STATUS VOTING: stopped
    #     data = {'action': 'start'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already started')

    #     data = {'action': 'stop'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already stopped')

    #     data = {'action': 'tally'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), 'Voting tallied')

    #     # STATUS VOTING: tallied
    #     data = {'action': 'start'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already started')

    #     data = {'action': 'stop'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already stopped')

    #     data = {'action': 'tally'}
    #     response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
    #     self.assertEqual(response.status_code, 400)
    #     self.assertEqual(response.json(), 'Voting already tallied')

    #Pruebas unitarias para la funcionalidad de crear votaciones con múltiples question

    def create_voting_multi(self):
        q1 = Question(desc='test1 question', option_types=2)
        q2 = Question(desc='test2 question', option_types=2)

        q1.save()
        q2.save()

        for i in range(5):
            opt = QuestionOption(question=q1, option='option {}'.format(i+1))
            opt.save()

        for i in range(5):
            opt = QuestionOption(question=q2, option='option {}'.format(i+1))
            opt.save()

        v = Voting(name='test voting multi')
        v.save()
        v.question.add(q1)
        v.question.add(q2)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                           defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    #Caso positivo 1: se crea correctamente una votación con una única question

    def test_multi_voting_simple_pos(self):
        v1 = self.create_voting()  
        self.assertEqual(v1.name, 'test voting')

        
        q = []
        for quest in v1.question.all():
            q.append(quest.desc)

        desc = q[0]
        self.assertEqual(desc, 'test question')
        
        longitud = len(q)
        self.assertEqual(longitud, 1)

    #Caso positivo 2: se crea correctamente una votación con dos question

    def test_multi_voting_two_pos(self):
        v1 = self.create_voting_multi()  
        self.assertEqual(v1.name, 'test voting multi')

        
        q = []
        for quest in v1.question.all():
            q.append(quest.desc)

        desc1 = q[0]
        desc2 = q[1]
        self.assertEqual(desc1, 'test1 question')
        self.assertEqual(desc2, 'test2 question')
        
        longitud = len(q)
        self.assertEqual(longitud, 2)

    
    
