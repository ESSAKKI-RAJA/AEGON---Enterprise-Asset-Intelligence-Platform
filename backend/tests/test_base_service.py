import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.base import BaseService
from app.repositories.base import UnitOfWork, RepositoryException
from app.exceptions.service import EnterpriseServiceException

@pytest.mark.asyncio
async def test_base_service_execute_in_transaction_success():
    mock_uow = AsyncMock(spec=UnitOfWork)
    mock_dispatcher = AsyncMock()
    
    service = BaseService(mock_uow, mock_dispatcher)
    
    async def dummy_operation():
        return "success"
        
    result = await service.execute_in_transaction(dummy_operation)
    
    assert result == "success"
    # UnitOfWork __aenter__ and __aexit__ should be called
    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

@pytest.mark.asyncio
async def test_base_service_execute_in_transaction_failure():
    mock_uow = AsyncMock(spec=UnitOfWork)
    mock_dispatcher = AsyncMock()
    
    service = BaseService(mock_uow, mock_dispatcher)
    
    async def dummy_operation():
        raise RepositoryException("DB error")
        
    with pytest.raises(EnterpriseServiceException):
        await service.execute_in_transaction(dummy_operation)
        
    mock_uow.__aenter__.assert_awaited_once()
    mock_uow.__aexit__.assert_awaited_once()

@pytest.mark.asyncio
async def test_base_service_publish_event():
    mock_uow = AsyncMock()
    mock_dispatcher = AsyncMock()
    
    service = BaseService(mock_uow, mock_dispatcher)
    
    event = MagicMock()
    await service.publish_event(event)
    
    mock_dispatcher.publish.assert_awaited_once_with(event)
