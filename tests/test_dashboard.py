import sys
import os
import pytest
from fastapi.testclient import TestClient


sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')

from main import app

client = TestClient(app)

def test_dashboard():
    response = client.get("/auth/dashboard") # I know,I know - it is the easiest endpoint;)
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to your dashboard!"}
