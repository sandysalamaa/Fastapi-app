import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.organization_service import create_organization, add_user_to_org, get_org_users
from app.models.organization import Organization
from app.models.membership import Membership
from app.models.user import User
from fastapi import HTTPException

class TestOrganizationService:
    """Test organization service functions."""
    
    @pytest.mark.asyncio
    async def test_create_organization_success(self):
        """test successful organization creation."""
        mock_db = AsyncMock()
        mock_user = User(id=1, email="testuser@gmail.com")
        mock_org = Organization(id=1, name="Test Org", created_by=1)
        
        with patch('app.services.organization_service.Organization', return_value=mock_org):
            result = await create_organization(mock_db, mock_user, "Test Org")
            
            assert result.name == "Test Org"
            assert result.created_by == 1
            mock_db.add.assert_called()
            mock_db.commit.assert_called()
            print(f"Organization created: {result.name}")
    
    @pytest.mark.asyncio
    async def test_add_user_to_org_success(self):
        """test successfully adding user to organization."""
        mock_db = AsyncMock()
        mock_user = User(id=2, email="newuser@gmail.com")
        mock_current_user = User(id=1, email="admin@gmail.com")
        
        # Mock the database execute calls properly
        call_count = 0
        async def mock_execute_side_effect(query):
            nonlocal call_count
            call_count += 1
            mock_result = MagicMock()
            if call_count == 1:  # First call - user lookup
                mock_result.scalar_one_or_none.return_value = mock_user
            else:  # Second call - membership check
                mock_result.scalar_one_or_none.return_value = None  # User not already member
            return mock_result
        
        mock_db.execute = mock_execute_side_effect
        
        result = await add_user_to_org(mock_db, 1, "newuser@gmail.com", "member", mock_current_user)
        
        assert result["message"] == "User added successfully"
        print(f"User added to organization: {result}")
    
    @pytest.mark.asyncio
    async def test_add_user_to_org_user_not_found(self):
        """test adding non-existent user to organization."""
        mock_db = AsyncMock()
        mock_current_user = User(id=1, email="admin@gmail.com")
        
        # Mock the database execute to return None for user lookup
        async def mock_execute_side_effect(query):
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            return mock_result
        
        mock_db.execute = mock_execute_side_effect
        
        with pytest.raises(HTTPException, match="User not found"):
            await add_user_to_org(mock_db, 1, "nonexistent@gmail.com", "member", mock_current_user)
        print(f"Non-existent user correctly rejected")
    
    @pytest.mark.asyncio
    async def test_add_user_to_org_already_member(self):
        """test adding user who is already member."""
        mock_db = AsyncMock()
        mock_user = User(id=2, email="existing@gmail.com")
        mock_current_user = User(id=1, email="admin@gmail.com")
        mock_existing_membership = Membership()
        
        # Mock the database execute calls
        call_count = 0
        async def mock_execute_side_effect(query):
            nonlocal call_count
            call_count += 1
            mock_result = MagicMock()
            if call_count == 1:  # First call - user lookup
                mock_result.scalar_one_or_none.return_value = mock_user
            else:  # Second call - membership check
                mock_result.scalar_one_or_none.return_value = mock_existing_membership
            return mock_result
        
        mock_db.execute = mock_execute_side_effect
        
        with pytest.raises(HTTPException, match="User already added to this organization"):
            await add_user_to_org(mock_db, 1, "existing@gmail.com", "member", mock_current_user)
        print(f"Duplicate membership correctly rejected")
    
    @pytest.mark.asyncio
    async def test_get_org_users_success(self):
        """test getting organization users."""
        mock_db = AsyncMock()
        mock_users = [User(id=1, email="user1@gmail.com"), User(id=2, email="user2@gmail.com")]
        
        # Mock the database execute to return users
        async def mock_execute_side_effect(query):
            mock_result = MagicMock()
            mock_scalars = MagicMock()
            mock_scalars.all.return_value = mock_users
            mock_result.scalars.return_value = mock_scalars
            return mock_result
        
        mock_db.execute = mock_execute_side_effect
        
        result = await get_org_users(mock_db, 1, 10, 0)
        
        assert len(result) == 2
        assert result[0].email == "user1@gmail.com"
        print(f"Retrieved {len(result)} users from organization")