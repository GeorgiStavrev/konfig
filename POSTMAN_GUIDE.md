# Postman Collection Guide v2 - New Authentication Model

## What's New in v2

**Major Changes:**
- ✅ Separate Tenant and User models
- ✅ User-based authentication (JWT tokens)
- ✅ API Key authentication for services
- ✅ Role-based access control (owner, admin, member)
- ✅ User management endpoints
- ✅ API key management endpoints

## Files

1. **Konfig_v2.postman_collection.json** - Updated API collection
2. **Konfig_v2.local.postman_environment.json** - Local development environment
3. **Konfig_v2.production.postman_environment.json** - Production template

## Quick Start

### 1. Import Collection and Environment

1. Open Postman
2. Click "Import" button
3. Import these files:
   - `Konfig_v2.postman_collection.json`
   - `Konfig_v2.local.postman_environment.json`
4. Select "Konfig Local v2" environment from the dropdown (top right)

### 2. First-Time Setup Workflow

#### Step 1: Register (Creates Tenant + Owner User)

1. Open **Authentication → Register (Create Tenant + Owner User)**
2. The request body uses environment variables:
   ```json
   {
       "tenant_name": "{{tenant_name}}",     // "My Company"
       "email": "{{owner_email}}",           // "owner@example.com"
       "password": "{{owner_password}}",     // "SecurePassword123!"
       "full_name": "{{owner_full_name}}"    // "Owner User"
   }
   ```
3. Click **Send**
4. On success (201), the following are automatically saved:
   - `access_token` - Your JWT token
   - `refresh_token` - For refreshing the access token
   - `user_id` - Your user ID
   - `tenant_id` - Your organization ID
   - `tenant_name` - Your organization name

✅ You're now authenticated! All subsequent requests will use your access token automatically.

#### Step 2: Create a Namespace

1. Open **Namespaces → Create Namespace**
2. Click **Send**
3. On success, `namespace_id` is automatically saved

#### Step 3: Create a Configuration

1. Open **Configurations → Create Config**
2. Modify the request body as needed
3. Click **Send**
4. On success, `config_key` is automatically saved

### 3. User Management

#### Add a New User

1. Open **Users → Create User**
2. Modify the request body:
   ```json
   {
       "email": "admin@example.com",
       "password": "AdminPassword123!",
       "full_name": "Admin User",
       "role": "admin"  // owner, admin, or member
   }
   ```
3. Click **Send**
4. On success, `new_user_id` is saved

#### List All Users

1. Open **Users → List Users**
2. Click **Send**
3. See all users in your tenant

#### User Roles

- **owner**: Full access, can delete tenant, manage everything
- **admin**: Can manage users and all resources
- **member**: Can manage namespaces and configs only

### 4. API Key Authentication (For Services)

#### Create an API Key

1. Open **API Keys → Create API Key**
2. Modify the request body:
   ```json
   {
       "name": "Production Service",
       "scopes": "read,write"
   }
   ```
3. Click **Send**
4. ⚠️ **IMPORTANT**: Copy the `api_key` from the response immediately!
   - It's only shown once
   - It's automatically saved to environment as `{{api_key}}`
   - Format: `konfig_<random_string>`

#### Use API Key for Requests

There are two ways to use API keys:

**Method 1: Use Example Requests**
1. Open **Examples with API Key Auth → List Namespaces (API Key)**
2. Click **Send**
3. This request uses `X-API-Key` header instead of Bearer token

**Method 2: Manual Header**
1. Open any namespace or config request
2. Go to **Headers** tab
3. Remove `Authorization` header
4. Add header:
   - Key: `X-API-Key`
   - Value: `{{api_key}}`
5. Click **Send**

### 5. Dual Authentication Support

Namespace and Configuration endpoints support BOTH authentication methods:

- **JWT Token** (for users): `Authorization: Bearer {{access_token}}`
- **API Key** (for services): `X-API-Key: {{api_key}}`

Choose the appropriate method based on your use case:
- Web/mobile apps → Use JWT tokens
- Backend services → Use API keys

## Collection Structure

### 1. Health Check
- Simple endpoint to verify API is running
- No authentication required

### 2. Authentication
- **Register** - Create tenant + owner user
- **Login** - Get access token for existing user

### 3. Users
- **List Users** - See all users in your tenant
- **Create User** - Add admin/member users (requires admin+)
- **Get User** - View user details
- **Update User** - Modify user info or role
- **Delete User** - Remove user (requires owner)

### 4. API Keys
- **List API Keys** - See all API keys (requires admin+)
- **Create API Key** - Generate new API key (requires admin+)
- **Get API Key** - View API key details
- **Revoke API Key** - Delete API key (requires admin+)

### 5. Namespaces
- **List Namespaces** - All namespaces in your tenant
- **Create Namespace** - Create new namespace
- **Get Namespace** - View namespace details
- **Update Namespace** - Modify namespace
- **Delete Namespace** - Remove namespace

### 6. Configurations
- **List Configs** - All configs in a namespace
- **Create Config** - Add new configuration
- **Get Config** - Fetch configuration (decrypted)
- **Update Config** - Modify configuration (creates version)
- **Delete Config** - Remove configuration
- **Get Config History** - View version history

### 7. Examples with API Key Auth
- Pre-configured examples showing API key usage
- Use these as templates for service authentication

## Environment Variables

### User-Defined Variables (Edit in Environment)

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `base_url` | http://localhost:8000 | API base URL |
| `tenant_name` | My Company | Your organization name |
| `owner_email` | owner@example.com | Owner user email |
| `owner_password` | SecurePassword123! | Owner user password |
| `owner_full_name` | Owner User | Owner user full name |
| `namespace_name` | production | Default namespace name |

### Auto-Generated Variables (Set by Scripts)

| Variable | Description |
|----------|-------------|
| `access_token` | JWT access token |
| `refresh_token` | JWT refresh token |
| `user_id` | Current user ID |
| `user_email` | Current user email |
| `tenant_id` | Current tenant ID |
| `namespace_id` | Last created namespace ID |
| `config_key` | Last created config key |
| `api_key` | Last created API key (full key) |
| `api_key_id` | Last created API key ID |
| `new_user_id` | Last created user ID |

## Common Workflows

### Workflow 1: Initial Setup (Web App)

```
1. Register → Creates tenant + owner user
2. Login → Get fresh token
3. Create Namespace → "production"
4. Create Config → Add configurations
5. Get Config → Fetch when needed
```

### Workflow 2: Team Collaboration

```
1. Owner registers tenant
2. Owner creates admin user
3. Admin logs in
4. Admin creates member users
5. Members log in and manage configs
```

### Workflow 3: Service Integration

```
1. Admin creates API key
2. Copy API key to service
3. Service uses X-API-Key header
4. Service fetches configs
5. When done, revoke API key
```

### Workflow 4: Role-Based Operations

**As Owner:**
- ✅ Create/delete users
- ✅ Change user roles
- ✅ Create/revoke API keys
- ✅ Manage all resources

**As Admin:**
- ✅ Create users (except owners)
- ✅ Create/revoke API keys
- ✅ Manage all resources
- ❌ Cannot change roles

**As Member:**
- ✅ Manage namespaces
- ✅ Manage configurations
- ❌ Cannot manage users
- ❌ Cannot manage API keys

## Testing Different Scenarios

### Test 1: User Registration and Login

```
1. Register → Should return 201 with tokens
2. Login → Should return 200 with same user
3. Register again with same email → Should return 400
```

### Test 2: Role-Based Access

```
1. Register as owner
2. Create admin user
3. Create member user
4. Login as member
5. Try to create user → Should fail (403)
6. Try to create namespace → Should succeed (201)
```

### Test 3: API Key Workflow

```
1. Login as admin/owner
2. Create API key → Save the key
3. Use API key to list namespaces → Should succeed
4. Revoke API key
5. Try to use revoked key → Should fail (401)
```

### Test 4: Multi-Tenant Isolation

```
1. Register tenant A with owner A
2. Register tenant B with owner B
3. Login as owner A
4. Create namespace in tenant A
5. Login as owner B
6. Try to access tenant A's namespace → Should fail (404)
```

## Production Usage

### For Production Environment:

1. Import `Konfig_v2.production.postman_environment.json`
2. Edit environment variables:
   - `base_url`: Your production API URL
   - `tenant_name`: Your company name
   - `owner_email`: Your real email
   - `owner_password`: **Use a strong password!**
3. Switch to "Konfig Production v2" environment
4. Run registration and setup

### Security Best Practices:

1. **Never commit production credentials**
2. **Use environment-specific API keys**
3. **Rotate API keys regularly**
4. **Use strong passwords** (min 8 chars, uppercase, lowercase, number, special char)
5. **Revoke unused API keys**
6. **Use member role** for users who don't need admin access
7. **Enable MFA** (when available)

## Troubleshooting

### Issue: "Invalid authentication credentials"

**Possible causes:**
1. Access token expired → Run **Login** again
2. Wrong environment selected → Check top-right dropdown
3. User deactivated → Contact admin

**Solution:** Re-login with **Authentication → Login**

### Issue: "Insufficient permissions"

**Cause:** Your user role doesn't have permission for this operation

**Solutions:**
- For user management: Need admin or owner role
- For API keys: Need admin or owner role
- For configs: Any role works

### Issue: "Tenant not found or inactive"

**Cause:** Tenant account is deactivated

**Solution:** Contact platform administrator

### Issue: "API key has expired"

**Cause:** API key passed its expiration date

**Solution:** Create a new API key

### Issue: "Cannot delete last owner"

**Cause:** Trying to delete the only owner

**Solution:** Promote another user to owner first

## Migration from v1

If you're using the old Postman collection (tenant-based auth):

### Changes:

1. **Registration endpoint** now requires:
   - `tenant_name` instead of `name`
   - `full_name` for the user
   - Creates both tenant AND user

2. **Login endpoint** now returns:
   - `user` object with user details
   - `tenant_id` and `tenant_name`
   - Tokens work the same way

3. **New endpoints** added:
   - `/api/v1/users` - User management
   - `/api/v1/api-keys` - API key management

4. **Namespace/Config endpoints** now support:
   - Both JWT and API key auth
   - No other changes to request/response format

### Migration Steps:

1. Export your old environment variables
2. Import new collection and environment
3. Update `tenant_name`, `owner_email`, etc.
4. Re-register or login to get new tokens
5. Test all your workflows

## Support

For issues or questions:
- Check the API docs at `{base_url}/docs`
- Review error messages (they're descriptive!)
- Check the TEST_UPDATE_GUIDE.md for test examples
- Review MIGRATION_GUIDE.md for database setup

## Next Steps

- Set up automated tests using Newman
- Create collection runners for common workflows
- Set up monitoring for your API
- Implement token refresh logic in your app
- Set up webhook notifications (when available)
