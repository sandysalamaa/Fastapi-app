# tests/test_rbac.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from jose import jwt
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.user import User
from app.models.membership import Membership
from app.main import app
from app.db.dependency import get_db

client = TestClient(app)

def create_test_token(user_id: int) -> str:
    """Create a JWT token for testing."""
    return jwt.encode({"sub": str(user_id)}, SECRET_KEY, algorithm=ALGORITHM)

# Global mock database
mock_db = AsyncMock()

async def override_get_db():
    """Override database dependency."""
    return mock_db

app.dependency_overrides[get_db] = override_get_db

class TestRBAC:
    """Test RBAC enforcement on API endpoints."""
    @pytest.mark.asyncio
    async def test_admin_only_endpoints_member_forbidden(self):
        """Test admin endpoints reject regular members."""
        member_token = create_test_token(2)
        member_user = User(id=2, email="member@gmail.com", full_name="Member User")
        member_membership = Membership(user_id=2, org_id=1, role="member")
        
        # Reset mock and set up responses
        mock_db.reset_mock()
        
        # Mock user and membership lookup
        async def mock_execute_side_effect(query):
            mock_result = MagicMock()
            if "users" in str(query):
                mock_result.scalar_one_or_none.return_value = member_user
            else:  # membership lookup
                mock_result.scalar_one_or_none.return_value = member_membership
            return mock_result
        
        mock_db.execute = mock_execute_side_effect
        
        # Test add user to organization (should fail for member)
        response = client.post(
            "/organizations/1/user",
            json={"email": "newuser@gmail.com", "role": "member"},
            headers={"Authorization": f"Bearer {member_token}"}
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
        print("Member cannot access admin-only endpoint")
        
        # Test get organization users (should fail for member)
        response = client.get(
            "/organizations/1/users",
            headers={"Authorization": f"Bearer {member_token}"}
        )
        assert response.status_code == 403
        assert "Not authorized" in response.json()["detail"]
        print("Member cannot get organization users")
    
    @pytest.mark.asyncio
    async def test_membership_required_endpoints_member_success(self):
        """Test membership-required endpoints work for organization members."""
        member_token = create_test_token(2)
        member_user = User(id=2, email="member@gmail.com", full_name="Member User")
        member_membership = Membership(user_id=2, org_id=1, role="member")
        
        # Reset mock and set up responses
        mock_db.reset_mock()
        
        # Mock user and membership lookup
        async def mock_execute_side_effect(query):
            mock_result = MagicMock()
            if "users" in str(query):
                mock_result.scalar_one_or_none.return_value = member_user
            else:  # membership lookup
                mock_result.scalar_one_or_none.return_value = member_membership
            return mock_result
        
        mock_db.execute = mock_execute_side_effect
        
        # Test create item (requires membership)
        with patch('app.services.item_service.create_item') as mock_create_item:
            from app.models.item import Item
            mock_item = Item(id=1, org_id=1, created_by=2, details={"name": "Test Item"})
            mock_create_item.return_value = mock_item
            
            response = client.post(
                "/organizations/1/item",
                json={"item_details": {"name": "Test Item"}},
                headers={"Authorization": f"Bearer {member_token}"}
            )
            assert response.status_code == 200
            print("Member can create item")
        
        # Test get items (requires membership)
        with patch('app.services.item_service.get_items') as mock_get_items:
            mock_get_items.return_value = []
            
            response = client.get(
                "/organizations/1/item",
                headers={"Authorization": f"Bearer {member_token}"}
            )
            assert response.status_code == 200
            print("Member can get items")
    
    @pytest.mark.asyncio
    async def test_membership_required_endpoints_nonmember_forbidden(self):
        """Test membership-required endpoints reject non-members."""
        nonmember_token = create_test_token(3)
        nonmember_user = User(id=3, email="nonmember@gmail.com", full_name="Non-Member User")
        
        # Reset mock and set up responses
        mock_db.reset_mock()
        
        # Mock user lookup but no membership
        async def mock_execute_side_effect(query):
            mock_result = MagicMock()
            if "users" in str(query):
                mock_result.scalar_one_or_none.return_value = nonmember_user
            else:  # membership lookup - return None
                mock_result.scalar_one_or_none.return_value = None
            return mock_result
        
        mock_db.execute = mock_execute_side_effect
        
        # Test create item (should fail for non-member)
        response = client.post(
            "/organizations/1/item",
            json={"item_details": {"name": "Test Item"}},
            headers={"Authorization": f"Bearer {nonmember_token}"}
        )
        assert response.status_code == 403
        assert "Not part of organization" in response.json()["detail"]
        print("Non-member cannot create item")
        
        # Test get items (should fail for non-member)
        response = client.get(
            "/organizations/1/item",
            headers={"Authorization": f"Bearer {nonmember_token}"}
        )
        assert response.status_code == 403
        assert "Not part of organization" in response.json()["detail"]
        print("Non-member cannot get items")
    
    @pytest.mark.asyncio
    async def test_unauthenticated_access_forbidden(self):
        """Test that unauthenticated requests are rejected."""
        # Test without token
        response = client.post("/organizations/1/user", json={"email": "test@gmail.com", "role": "member"})
        assert response.status_code == 401  # HTTPBearer returns 401 for missing auth
        
        response = client.get("/organizations/1/users")
        assert response.status_code == 401
        
        response = client.post("/organizations/1/item", json={"item_details": {"name": "Test"}})
        assert response.status_code == 401
        
        response = client.get("/organizations/1/item")
        assert response.status_code == 401
        
        print("Unauthenticated access is blocked")
    
    @pytest.mark.asyncio
    async def test_invalid_token_forbidden(self):
        """Test that invalid tokens are rejected."""
        invalid_token = "invalid.jwt.token"
        
        response = client.post(
            "/organizations/1/user",
            json={"email": "test@gmail.com", "role": "member"},
            headers={"Authorization": f"Bearer {invalid_token}"}
        )
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
        
        print("Invalid tokens are rejected")