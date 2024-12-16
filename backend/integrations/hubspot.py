# slack.py
import json
import secrets
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import hashlib

import requests
from integrations.integration_item import IntegrationItem
from datetime import datetime
from typing import Optional, List,Dict
from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

CLIENT_ID = '9f0be225-0cfe-42b2-8a20-cf685121144d'
CLIENT_SECRET = '6b31bfdf-bef1-4c75-b9f1-92da5623ffbd'
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
AUTHORIZATION_URL = 'https://app.hubspot.com/oauth/authorize'
TOKEN_URL = 'https://api.hubapi.com/oauth/v1/token'
SCOPES = 'crm.objects.contacts.read crm.objects.deals.read'

from fastapi import Request
import secrets
from fastapi.responses import RedirectResponse


async def authorize_hubspot(user_id, org_id):
    sec_tok = secrets.token_urlsafe(32)
    state = f"{org_id}:{user_id}:{sec_tok}"
    # Save state in Redis for validation later
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', sec_tok, expire=600)

    auth_url = (
        f"{AUTHORIZATION_URL}"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}"
        f"&state={state}"
    )
    return RedirectResponse(auth_url)


async def oauth2callback_hubspot(request: Request):
    error = request.query_params.get('error')
    if error:
        raise HTTPException(status_code=400, detail=f"Authorization failed: {error}")

    code = request.query_params.get('code')
    state = request.query_params.get('state')
    try:
        org_id, user_id, random_state = state.split(":")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state format.")

    # Validate state
    user_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not user_state or user_state.decode('utf-8') != random_state:
        raise HTTPException(status_code=400, detail="State mismatch or expired.")

    # Exchange code for an access token
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={
                'grant_type': 'authorization_code',
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI,
                'code': code,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Token exchange failed.")

    token_data = response.json()
    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(token_data), expire=3600)

    return HTMLResponse("<html><script>window.close();</script></html>")
    pass

async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail="No credentials found.")
    return json.loads(credentials)


async def create_integration_item_metadata_object(response_json) -> List[IntegrationItem]:
    """
    Creates IntegrationItem metadata from the response JSON of HubSpot API.
    """
    integration_items = []

    # Iterate through the response JSON results
    for item in response_json.get("results", []):
        try:
            # Create the integration item
            integration_item = IntegrationItem(
                id=item.get("id"),
                name=item.get("properties", {}).get("dealname", "Unnamed Deal"),  # Use dealname for deal title
                amount=item.get("properties", {}).get("amount", None),
                deal_stage= item.get("properties", {}).get("dealstage", None)
            )
            integration_items.append(integration_item)
        except Exception as e:
            # Log error and skip problematic items
            print(f"Error processing item {item}: {e}")
            # Optionally, add traceback for more detailed error information
            import traceback
            traceback.print_exc()

    return integration_items

async def get_items_hubspot(credentials):
    """
    Fetches HubSpot CRM objects (e.g., Deals, Companies) and converts them to IntegrationItem metadata.
    """
    # Assuming credentials contain the access_token
    print(credentials)
    # Parse credentials if necessary
    credentials_dict = json.loads(credentials)
    access_token = credentials_dict.get('access_token')

    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    # URL for HubSpot CRM objects (e.g., Deals)
    url = "https://api.hubapi.com/crm/v3/objects/deals"  # You can change this to companies, tickets, etc.

    # API request to get CRM objects
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params={'limit': 100},  # Adjusted parameter for pagination if needed
            headers={'Authorization': f'Bearer {access_token}'}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to retrieve items from HubSpot.")

    response_json = response.json()
    print(response_json)
    print('after response')

    # Await the async function call to create metadata
    integration_items = await create_integration_item_metadata_object(response_json)


    serialized_items = jsonable_encoder(integration_items)

    # Return the serialized data as a JSON response
    return JSONResponse(content=serialized_items)
