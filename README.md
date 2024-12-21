# CRM Integration Project

This project demonstrates the integration of multiple CRM platforms (HubSpot, Airtable, and Notion) into a web application. It showcases OAuth 2.0 authentication and API interaction to fetch, process, and display CRM data.

---

## Features

- **OAuth 2.0 Authentication**: Secure integration with HubSpot, Airtable, and Notion using industry-standard OAuth 2.0.
- **Multi-CRM Support**: Fetch data from HubSpot (e.g., contacts, deals), Airtable (e.g., records), and Notion (e.g., databases).
- **Dynamic Data Handling**: Convert fetched data into structured `IntegrationItem` objects.
- **Redis Storage**: Store temporary credentials (e.g., access tokens) for secure access.
- **Frontend Integration**: Display CRM data with a user-friendly React UI.

---

## Tech Stack

### Backend

- **FastAPI**: Lightweight and modern Python framework for the API.
- **Redis**: Used for temporary data storage (e.g., OAuth states and tokens).
- **HTTPX**: For making asynchronous API requests to CRM platforms.

### Frontend

- **React**: Interactive user interface for connecting and displaying CRM data.
- **Axios**: For communicating with the backend.

### Deployment

- **Docker**: Containerized application for consistent deployment.
- **Cloud Platforms**: Compatible with AWS, Azure, or Heroku for deployment.

---

## OAuth Flow

1. **Authorization Request**:

   - User initiates the connection by clicking the "Connect" button in the frontend.
   - Redirects the user to the CRM's OAuth authorization URL.

2. **Authorization Callback**:

   - CRM redirects back to the app with an authorization code and state.
   - Backend validates the state and exchanges the code for access/refresh tokens.

3. **Token Storage**:

   - Tokens are securely stored in Redis with an expiration time.

4. **Data Fetching**:

   - Backend uses stored tokens to query CRM APIs and return structured data to the frontend.

---

## Endpoints

### Backend

#### `/integrations/<crm>/authorize`

Initiates the OAuth process for the specified CRM.

#### `/integrations/<crm>/oauth2callback`

Handles the callback from the CRM, validates the state, and exchanges the authorization code for tokens.

#### `/integrations/<crm>/load`

Fetches data from the CRM and returns it as structured `IntegrationItem` objects.

### Frontend

- Connect buttons for each CRM.
- Displays fetched data (e.g., contacts, records).

---

## How to Run

### Prerequisites

- Python 3.9+
- Node.js 16+
- Redis
- Docker (optional, for deployment)

### Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/your-username/crm-integration.git
cd crm-integration
```

#### 2. Backend Setup

```bash
cd backend
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
npm start
```

#### 4. Redis Setup

Start a local Redis instance or use a cloud-hosted Redis service.

#### 5. Environment Variables

Create `.env` files in the `backend` and `frontend` directories with your credentials (client ID, secret, and redirect URIs).

#### 6. Access the App

Visit `http://localhost:3000` to use the application.

---

## Deployment

### Docker Deployment

1. Build and run the Docker containers:

```bash
docker-compose up --build
```

2. Access the application at `http://localhost:3000`.

### Cloud Deployment

- Use platforms like AWS, Azure, or Heroku for deployment.
- Ensure environment variables are securely stored.

---

## Example Data Flow

1. **Connect HubSpot**:

   - User authorizes access.
   - Backend fetches contacts and deals using the HubSpot API.

2. **Connect Airtable**:

   - Fetches records from specified bases.

3. **Connect Notion**:

   - Retrieves data from Notion databases.

---

## Screenshots

Add screenshots of the app interface, showing:

- OAuth process.
- ![UI - 1](https://github.com/user-attachments/assets/a1ac7c2c-8b60-418f-80fc-0e174dc4fb54)
- OAuth
- ![UI - 2](https://github.com/user-attachments/assets/3c85bd9d-1394-4a06-87fb-3ef8db4d62b6)
- Data displayed for each CRM.
![UI - 3](https://github.com/user-attachments/assets/6ead36c9-f9e7-4e8f-a27b-b6494f3aa762)
---

## Future Enhancements

- Add support for more CRMs.
- Improve UI/UX for better data visualization.
- Implement role-based access control (RBAC).

---

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
