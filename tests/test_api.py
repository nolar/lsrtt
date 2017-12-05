import json


CUSTOMER_ID = '123456789012345678901234567890ab'
CUSTOMER_CLV = 112.03


def test_api_index(app):
    response = app.get('/')
    assert response.status_code == 200
    assert b'<plaintext>' in response.data


def test_api_404(app):
    response = app.get('/api/non-existent')
    assert response.status_code == 404


def test_api_customers(app):
    response = app.get('/api/customers')
    assert response.status_code == 200

    data = json.loads(response.data)

    assert isinstance(data, list)
    assert len(data) == 10


def test_api_customer_predictions(app):
    response = app.get('/api/customers/{}/predictions'.format(CUSTOMER_ID))
    assert response.status_code == 200

    data = json.loads(response.data)

    assert isinstance(data, dict)
    assert len(data.keys()) == 2
    assert 'customer_id' in data
    assert 'predicted_clv' in data
    assert data['customer_id'] == CUSTOMER_ID
    assert data['predicted_clv'] == CUSTOMER_CLV
