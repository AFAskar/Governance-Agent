# RBAC Configuration with WorkOS

This project uses Role-Based Access Control (RBAC) with WorkOS to manage permissions for submissions.

## Permissions

The following permissions are configured for submissions:

- `submissions:read` - View submissions and their details (access to Admin Dashboard)
- `submissions:write` - Create new submissions (access to Submit page)
- `submissions:delete` - Delete existing submissions

## Roles

You should configure the following roles in your WorkOS dashboard:

### Admin
- Can view, create, and delete submissions
- Permissions: `submissions:read`, `submissions:write`, `submissions:delete`

### Manager
- Can view and create submissions
- Permissions: `submissions:read`, `submissions:write`

### Member (Default)
- Can only create submissions (cannot view existing ones)
- Permissions: `submissions:write`

**Note**: The Member role has write permissions but not read permissions. This means members can submit new evaluations but cannot view the admin dashboard or existing submissions.

## Setup Instructions

### 1. Create Permissions in WorkOS Dashboard

1. Go to [WorkOS Dashboard](https://dashboard.workos.com/) > **Roles & Permissions**
2. Click **"Create Permission"** and add each permission:
   - `submissions:read`
   - `submissions:write`
   - `submissions:delete`

### 2. Create Roles in WorkOS Dashboard

1. In the same **Roles & Permissions** page, click **"Create Role"**
2. Create the following roles with their respective permissions:

   **Admin Role:**
   - Name: `admin`
   - Permissions: `submissions:read`, `submissions:write`, `submissions:delete`

   **Manager Role:**
   - Name: `manager`
   - Permissions: `submissions:read`, `submissions:write`

   **Member Role:**
   - Name: `member`
   - Permissions: `submissions:write`
   - Set as default role (click ellipsis → "Set as default")

### 3. Assign Roles to Users

#### Manual Assignment
1. Go to **WorkOS Dashboard** > **Users**
2. Create or select a user
3. Go to **Organizations** > Select your organization > **Users** tab
4. Add users to the organization
5. For each user, click ellipsis → **"Edit role"** → Select appropriate role

#### Automatic Assignment via SSO
If you're using SSO with Directory Sync, you can map identity provider groups to roles:
- See [Group to Role Mapping](https://workos.com/blog/group-to-role-mapping)
- Configure in **WorkOS Dashboard** > **Directory Sync** > Your directory > **Role Mapping**

## Implementation

### How Permissions Work

1. **Authentication**: Users authenticate via WorkOS AuthKit
2. **Access Token**: WorkOS includes role permissions in the JWT access token
3. **Backend Check**: The tRPC middleware extracts permissions from the session
4. **Frontend Check**: Routes check permissions in `beforeLoad` hooks
5. **Authorization**: Each endpoint/page checks for required permissions before access

### Code Structure

#### Backend
- **Permissions Definition**: `packages/api/src/lib/workos.ts`
- **Permission Middleware**: `packages/api/src/trpc.ts` - `createPermissionProcedure()`
- **Submission Routes**: `packages/api/src/router/submission.ts`

#### Frontend
- **Permission Utilities**: `apps/tanstack-start/src/lib/permissions.ts`
- **Protected Routes**: 
  - `apps/tanstack-start/src/routes/admin/index.tsx`
  - `apps/tanstack-start/src/routes/admin/ndi.tsx`
  - `apps/tanstack-start/src/routes/admin/company.$companyId.tsx`
  - `apps/tanstack-start/src/routes/submit.tsx`
- **Conditional UI**: `apps/tanstack-start/src/component/layout/Header.tsx`

### Example Usage

#### Backend Permission Check
```typescript
// Create a procedure that requires submissions:write permission
const createSubmission = createPermissionProcedure([SUBMISSION_PERMISSIONS.WRITE])
  .mutation(async ({ ctx, input }) => {
    // Only users with submissions:write can access this
  });
```

#### Frontend Route Protection
```typescript
export const Route = createFileRoute("/admin/")({
  beforeLoad: async () => {
    const auth = await getAuth();
    
    if (!auth.user) {
      throw redirect({ to: "/" });
    }
    
    if (!hasPermission(auth.permissions, SUBMISSION_PERMISSIONS.READ)) {
      throw redirect({ 
        to: "/",
        search: { error: "insufficient_permissions" }
      });
    }
  },
  component: RouteComponent,
});
```

## Testing Permissions

1. **Create test users** with different roles in WorkOS
2. **Sign in** as each user
3. **Test operations**:
   - **Member** should only be able to submit new evaluations (access to `/submit` page)
     - ❌ No access to Admin Dashboard
     - ❌ No "Admin Dashboard" link in header
     - ✅ Can access Submit page
   - **Manager** should be able to view and create submissions
     - ✅ Access to Admin Dashboard (`/admin`)
     - ✅ Can submit new evaluations
     - ✅ Can view all submissions
   - **Admin** should be able to view, create, and delete submissions
     - ✅ Full access to all features
     - ✅ Can delete submissions (API endpoint available)

## Environment Variables

Ensure the following environment variables are set:

```env
WORKOS_API_KEY=sk_...
WORKOS_CLIENT_ID=client_...
WORKOS_REDIRECT_URI=http://localhost:3000/api/auth/callback
WORKOS_COOKIE_PASSWORD=... # At least 32 characters
```

## API Endpoints & Required Permissions

| Endpoint | Method | Permission | Description |
|----------|--------|------------|-------------|
| `submission.getAll` | Query | `submissions:read` | List all submissions |
| `submission.getById` | Query | `submissions:read` | Get submission details |
| `submission.create` | Mutation | `submissions:write` | Create new submission |
| `submission.delete` | Mutation | `submissions:delete` | Delete submission |

## Frontend Routes & Required Permissions

| Route | Permission | Description |
|-------|------------|-------------|
| `/` | None | Home page (shows error if redirected) |
| `/submit` | `submissions:write` | Submit new evaluation |
| `/admin` | `submissions:read` | Admin dashboard index |
| `/admin/ndi` | `submissions:read` | View NDI submissions |
| `/admin/company/:id` | `submissions:read` | View company details |

## Error Handling

### Backend Errors
When a user lacks required permissions:
- **Status**: 403 FORBIDDEN
- **Error Message**: "Missing required permissions: submissions:write"

When a user is not authenticated:
- **Status**: 401 UNAUTHORIZED

### Frontend Behavior
When a user lacks required permissions:
- **Redirected to**: Home page (`/`)
- **Error displayed**: "Insufficient Permissions" banner
- **UI changes**: Admin Dashboard link hidden from header

## Resources

- [WorkOS RBAC Documentation](https://workos.com/docs/rbac)
- [WorkOS Roles & Permissions](https://workos.com/docs/user-management/roles-and-permissions)
- [RBAC with WorkOS and Node Tutorial](https://workos.com/blog/rbac-with-workos-and-node)
- [Identity Provider Role Assignment](https://workos.com/docs/rbac/idp-role-assignment)
