"""Offline tests of the actual Google libraries; no live credential or API call."""
import json
import unittest
from importlib.util import find_spec
from urllib.parse import parse_qs,urlsplit
from orchestrator.drive_evidence import SCOPE


@unittest.skipUnless(find_spec('google_auth_oauthlib'), 'Run separately in the pinned optional Drive client environment')
class GoogleClientTests(unittest.TestCase):
    def test_picker_offline_pkce_configuration(self):
        from google_auth_oauthlib.flow import InstalledAppFlow
        config={'installed':{'client_id':'synthetic.apps.googleusercontent.com','client_secret':'synthetic',
                'auth_uri':'https://accounts.google.com/o/oauth2/auth',
                'token_uri':'https://oauth2.googleapis.com/token','redirect_uris':['http://localhost']}}
        flow=InstalledAppFlow.from_client_config(config,[SCOPE],autogenerate_code_verifier=True)
        flow.redirect_uri='http://localhost:8765/'
        url,state=flow.authorization_url(access_type='offline',prompt='consent',trigger_onepick='true',allow_multiple='true',include_granted_scopes='false')
        values=parse_qs(urlsplit(url).query)
        for key,value in {'scope':SCOPE,'state':state,'access_type':'offline','trigger_onepick':'true','code_challenge_method':'S256','include_granted_scopes':'false'}.items():
            self.assertEqual(values[key],[value])

    def test_refresh_and_restart_with_fake_provider(self):
        from google.oauth2.credentials import Credentials
        info={'client_id':'synthetic','client_secret':'synthetic','refresh_token':'synthetic-refresh',
              'token_uri':'https://oauth2.googleapis.com/token','scopes':[SCOPE]}
        calls=[]
        class Response:
            status=200
            data=json.dumps({'access_token':'synthetic-access','expires_in':3600,'token_type':'Bearer','scope':SCOPE}).encode()
        def provider(url,method='GET',body=None,headers=None,**kwargs):
            calls.append(url)
            self.assertEqual(url,'https://oauth2.googleapis.com/token')
            return Response()
        for _ in range(2):
            creds=Credentials.from_authorized_user_info(info,scopes=[SCOPE])
            self.assertTrue(creds.expired)
            creds.refresh(provider)
            self.assertTrue(creds.valid)
            self.assertEqual(creds.refresh_token,'synthetic-refresh')
        self.assertEqual(len(calls),2)


if __name__=='__main__':unittest.main()
