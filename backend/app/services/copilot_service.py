from typing import Optional
import uuid
from typing import Dict, Any
from app.services.base import BaseService, track_metrics
from app.repositories.base import UnitOfWork
from app.core.events import EventDispatcher
from app.models.copilot import Conversation, ConversationMessage, RetrievedContext
from app.services.rag_service import RAGService
from app.ai.llm_gateway import llm_gateway

class CopilotService(BaseService):
    def __init__(self, uow: UnitOfWork, event_dispatcher: Optional[EventDispatcher] = None):
        super().__init__(uow, event_dispatcher)
        self.rag_service = RAGService(uow=self.uow, event_dispatcher=self.event_dispatcher)

    @track_metrics("ask_copilot")
    async def ask(self, conversation_id: uuid.UUID, user_query: str, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Orchestrates Copilot interaction:
        1. Logs user message
        2. Retrieves RAG context
        3. Calls LLM Gateway
        4. Logs AI response with citations
        """
        async def _operation():
            # In a full implementation we would use repos, but for brevity we use session directly
            session = self.uow.session
            
            # 1. Fetch or create conversation
            from sqlalchemy import select
            stmt = select(Conversation).where(Conversation.id == conversation_id)
            res = await session.execute(stmt)
            conv = res.scalar_one_or_none()
            if not conv:
                conv = Conversation(id=conversation_id, title=user_query[:50] + "...")
                session.add(conv)
                await session.flush()

            # 2. Add User Message
            user_msg = ConversationMessage(
                conversation_id=conv.id,
                sender="USER",
                content=user_query,
                created_by=user_id
            )
            session.add(user_msg)
            
            # 3. Retrieve Context via RAG
            rag_results = await self.rag_service.search(query=user_query, top_k=3)
            
            context_text = "\n\n".join([f"Source ({r['document_title']}): {r['chunk_text']}" for r in rag_results])
            
            # 4. Call LLM Gateway
            ai_response = await llm_gateway.generate_explanation(
                context=context_text,
                prompt=user_query
            )
            
            # Format as an enterprise markdown report
            content_str = (
                f"### Executive Intelligence Brief\n\n"
                f"**Prediction Analysis:**\n"
                f"{ai_response.get('Prediction', 'N/A')}\n\n"
                f"**Confidence Level:** `{ai_response.get('Confidence', 0)}%`\n\n"
                f"**Business Justification:**\n"
                f"{ai_response.get('Reason', 'No reason provided')}\n\n"
                f"**Data Evidence:**\n"
                f"- {ai_response.get('Evidence', 'Insufficient evidence')}\n\n"
                f"### Recommended Action\n"
                f"> **{ai_response.get('RecommendedAction', 'Monitor situation')}**\n"
            )

            # 5. Add AI Message
            ai_msg = ConversationMessage(
                conversation_id=conv.id,
                sender="ASSISTANT",
                content=content_str,
                created_by=user_id
            )
            session.add(ai_msg)
            await session.flush()
            
            # 6. Save Retrieved Contexts mapping
            for idx, rag_res in enumerate(rag_results):
                ret_ctx = RetrievedContext(
                    message_id=ai_msg.id,
                    context_text=rag_res['chunk_text'],
                    similarity_score=rag_res['score'],
                    created_by=user_id
                )
                session.add(ret_ctx)

            return {
                "message": content_str,
                "citations": rag_results
            }

        return await self.execute_in_transaction(_operation)
