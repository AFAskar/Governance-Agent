# WorkOS Admin Portal Demo Setup Guide

This guide will help you set up and demonstrate the WorkOS Admin Portal with Keycloak SSO integration.

## Quick Start

1. **Start the demo environment:**

   ```bash
   docker compose -f docker-compose.demo.yml up
   ```

2. **Access points:**
   - **Frontend Application:** http://localhost:5001
   - **Keycloak Admin Console:** http://localhost:8080
     - Username: `admin`
     - Password: `admin`

## Setting Up Keycloak for WorkOS Demo

### Step 1: Configure Keycloak Realm

1. Navigate to http://localhost:8080 and login with `admin / admin`

2. Create a new realm (or use the master realm):
   - Click the realm dropdown (top-left)
   - Click "Create Realm"
   - Name: `governance-demo`
   - Click "Create"

### Step 2: Configure SAML/OIDC Client for WorkOS

#### For SAML:

1. Go to **Clients** → **Create client**
2. Set:
   - Client type: `SAML`
   - Client ID: `workos-governance-app`
3. Click **Next**, then **Save**
4. Configure the client:
   - Valid redirect URIs: `https://api.workos.com/sso/saml/acs/*`
   - Master SAML Processing URL: `https://api.workos.com/sso/saml/acs`
   - Name ID format: `email`
5. Save the configuration

#### For OpenID Connect (OIDC):

1. Go to **Clients** → **Create client**
2. Set:
   - Client type: `OpenID Connect`
   - Client ID: `workos-governance-app`
3. Click **Next**
4. Configure:
   - Client authentication: `ON`
   - Valid redirect URIs: `https://api.workos.com/sso/oauth/callback`
   - Web origins: `http://localhost:5001`
5. Save and note the **Client Secret** from the Credentials tab

### Step 3: Create Test Users

1. Navigate to **Users** → **Create new user**
2. Create demo users:
   - Username: `demo.user@company.com`
   - Email: `demo.user@company.com`
   - First name: `Demo`
   - Last name: `User`
   - Email verified: `ON`
3. Click **Create**
4. Set password:
   - Go to **Credentials** tab
   - Click **Set password**
   - Password: `demo123`
   - Temporary: `OFF`
5. Repeat for additional demo users (e.g., admin, manager, employee)

### Step 4: Configure WorkOS Admin Portal

1. **Get Keycloak metadata URL:**
   - For SAML: `http://localhost:8080/realms/governance-demo/protocol/saml/descriptor`
   - For OIDC: `http://localhost:8080/realms/governance-demo/.well-known/openid-configuration`

2. **In WorkOS Dashboard** (https://dashboard.workos.com):
   - Create an Organization
   - Navigate to **SSO** → **Connections** → **Create Connection**
   - Choose **SAML** or **OIDC**
   - Enter the Keycloak metadata URL or configure manually:
     - **SAML Endpoint:** `http://localhost:8080/realms/governance-demo/protocol/saml`
     - **OIDC Discovery:** `http://localhost:8080/realms/governance-demo/.well-known/openid-configuration`

3. **Configure Domain:**
   - Add a domain (e.g., `company.com`)
   - Link it to the Keycloak connection

### Step 5: Test the Admin Portal

1. **Access the WorkOS Admin Portal:**

   ```javascript
   // Generate Admin Portal link in your application
   const adminPortalUrl = `https://api.workos.com/portal/launch?
     client_id=${WORKOS_CLIENT_ID}&
     intent=sso&
     organization=${organizationId}&
     return_url=${encodeURIComponent("http://localhost:5001/dashboard")}`;
   ```

2. **Via API:**
   ```bash
   curl -X POST https://api.workos.com/user_management/portal/generate_link \
     -H "Authorization: Bearer ${WORKOS_API_KEY}" \
     -H "Content-Type: application/json" \
     -d '{
       "organization": "org_...",
       "intent": "sso"
     }'
   ```

## Demo Flow

### For Your Presentation:

1. **Show the Admin Portal UI:**
   - "This is the WorkOS Admin Portal - IT admins can configure SSO without developer involvement"

2. **Configure Keycloak SSO:**
   - Show how an admin would paste the Keycloak SAML/OIDC metadata
   - Demonstrate domain configuration
   - Show the connection testing feature

3. **Test SSO Login:**
   - Navigate to your app's login
   - Enter a user email with the configured domain
   - Show the automatic redirect to Keycloak
   - Complete authentication
   - Show successful login to your app

4. **Highlight Key Features:**
   - Self-service SSO configuration
   - No code deployments needed
   - Support for multiple identity providers
   - Domain-based routing
   - User provisioning (SCIM)

## Troubleshooting

### Keycloak not accessible

```bash
# Check if Keycloak is healthy
docker ps
docker logs keycloak_demo

# Wait for Keycloak to fully start (can take 60-90 seconds)
```

### WorkOS can't reach Keycloak

- Use ngrok or similar to expose Keycloak publicly for the demo:
  ```bash
  ngrok http 8080
  # Use the ngrok URL in WorkOS configuration
  ```

### Reset everything

```bash
docker compose -f docker-compose.demo.yml down -v
docker compose -f docker-compose.demo.yml up
```

## Environment Variables

Make sure your `.env` file contains:

```env
# WorkOS Configuration
WORKOS_CLIENT_ID=client_...
WORKOS_API_KEY=sk_test_...
WORKOS_REDIRECT_URI=http://localhost:5001/api/auth/callback
WORKOS_COOKIE_PASSWORD=your-secure-cookie-password-here

# Other required variables
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-db-password
POSTGRES_DB=app_db
```

## Useful Keycloak Endpoints

- **Admin Console:** http://localhost:8080/admin
- **Account Console:** http://localhost:8080/realms/governance-demo/account
- **SAML Metadata:** http://localhost:8080/realms/governance-demo/protocol/saml/descriptor
- **OIDC Discovery:** http://localhost:8080/realms/governance-demo/.well-known/openid-configuration

## Additional Resources

- [WorkOS Admin Portal Docs](https://workos.com/docs/user-management/admin-portal)
- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [WorkOS SSO QuickStart](https://workos.com/docs/sso/guide)
