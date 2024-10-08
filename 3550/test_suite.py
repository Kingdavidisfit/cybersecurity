from datetime import UTC, datetime
import pytest
from app import app
import jwt
from flask import Flask

@pytest.fixture
def client():
    with app.test_client() as test:
        yield test

# Should give a valid JWT
def test_Valid_JWT_authentication(client):
    test = client.post('/auth')
    assert test.status_code == 200

# Makes sure that /auth returns an expired JWT
def test_Expired_JWT_authentication(client):
    test = client.post('/auth')
    data = jwt.decode(test.get_json().get('token'), '9addb20691b1493de85c90a9a2369b1e', algorithms=['HS256'])
    assert data['exp'] is not None

# Makes sure that Valid JWT's kid is found in JWKS
def test_Valid_JWK_Found_In_JWKS(client):
    test = client.post('/auth')
    header = jwt.get_unverified_header(test.get_json().get('token'))

    assert header.get('kid') in [key['kid'] for key in client.get('/.well-known/jwks.json').get_json()['keys']]

# Test: Expired JWT's kid is not found in JWKS
def test_Expired_JWK_Not_Found_In_JWKS(client):
    test = client.post('/auth?expired=true')
    header = jwt.get_unverified_header(test.get_json().get('token'))

    assert header.get('kid') not in [key['kid'] for key in client.get('/.well-known/jwks.json').get_json()['keys']]

# Checks: JWT exp claim is in the past
def test_Expired_JWK_is_expired(client):
    test = client.post('/auth')
    data = jwt.decode(test.get_json().get('token'), '9addb20691b1493de85c90a9a2369b1e', algorithms=['HS256'])
    assert data['exp'] > data['iat']