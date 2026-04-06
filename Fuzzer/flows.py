# Fuzzer/flows.py
REGISTER_FLOW = [
    {
        "name": "register",
        "request": {
            "method": "POST",
            "endpoint": "/api/register",
            "json": {"username": "user1", "password": "pass"}
        }
    },
    {
        "name": "verify",
        "request": {
            "method": "POST",
            "endpoint": "/api/verify",
            "json": {"code": "123456"}
        }
    },
    {
        "name": "update_profile",
        "request": {
            "method": "POST",
            "endpoint": "/api/update-profile",
            "json": {"bio": "test"}
        }
    }
]