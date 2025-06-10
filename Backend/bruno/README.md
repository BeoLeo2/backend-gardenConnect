# GardenConnect API - Bruno Collection

This Bruno collection contains API requests for testing the GardenConnect microservices architecture.

## Setup

1. Install [Bruno](https://www.usebruno.com/) desktop app or VS Code extension
2. Open this collection in Bruno
3. Select the appropriate environment (Local or Docker)

## Environments

- **Local**: For development with services running directly (uvicorn)
- **Docker**: For services running in Docker containers

## Services

### Auth Service (Port 8001)
- User registration and authentication
- JWT token management
- User profile management
- Admin user operations

### Data Service (Port 8002)  
- Space management (garden areas)
- Node management (Arduino devices)
- Sensor management
- Sensor data collection

### Alert Service (Port 8003)
- Alert creation and management
- Notification system

## Usage

1. Start with authentication:
   - Register a new user or login
   - The access_token will be automatically set in environment variables

2. Use the token for protected endpoints:
   - All requests use the {{access_token}} variable
   - Token refresh is handled automatically

3. Test the workflow:
   - Create spaces → Create nodes → Create sensors → Add data → Monitor alerts

## Authentication Flow

1. **Register** - Create new user account
2. **Login** - Get access and refresh tokens  
3. **Use protected endpoints** - Tokens are automatically included
4. **Refresh token** - When access token expires
5. **Logout** - Invalidate tokens

## Variables

Environment variables are automatically managed:
- `access_token` - Set after successful login
- `refresh_token` - Set after successful login  
- Service URLs are pre-configured per environment