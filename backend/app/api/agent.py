from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    SessionItem,
    MessageHistoryItem,
    StructuredAnalysisResponse
)
from app.services.dataset_service import DatasetService
from app.agents.agent_executor import AgentExecutor
from app.agents.memory import ConversationMemory
from app.database.connection import get_db

router = APIRouter(prefix="/agent", tags=["Agent"])

class CreateSessionRequest(BaseModel):
    dataset_id: Optional[str] = None
    title: Optional[str] = "New Analysis"

@router.post("/sessions", response_model=SessionItem)
def create_session(req: CreateSessionRequest):
    """Create a new analysis session."""
    session_id = ConversationMemory.create_session(
        dataset_id=req.dataset_id,
        title=req.title or "New Analysis"
    )
    dataset_name = None
    if req.dataset_id:
        meta = DatasetService.get_dataset_metadata(req.dataset_id)
        if meta:
            dataset_name = meta["original_name"]
            
    now_str = datetime.now().isoformat()
    return SessionItem(
        id=session_id,
        title=req.title or "New Analysis",
        dataset_id=req.dataset_id,
        dataset_name=dataset_name,
        created_at=now_str,
        updated_at=now_str,
        message_count=0
    )

@router.get("/sessions", response_model=List[SessionItem])
def list_sessions():
    """Retrieve all analysis sessions with dataset names and message counts."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT s.id, s.title, s.dataset_id, s.created_at, s.updated_at,
                   d.original_name as dataset_name,
                   (SELECT COUNT(*) FROM messages m WHERE m.session_id = s.id) as message_count
            FROM sessions s
            LEFT JOIN datasets d ON s.dataset_id = d.id
            ORDER BY s.updated_at DESC
            """
        )
        rows = cursor.fetchall()
        return [
            SessionItem(
                id=r["id"],
                title=r["title"],
                dataset_id=r["dataset_id"],
                dataset_name=r["dataset_name"],
                created_at=str(r["created_at"]),
                updated_at=str(r["updated_at"]),
                message_count=r["message_count"]
            )
            for r in rows
        ]

@router.post("/chat", response_model=ChatResponse)
def chat_with_agent(req: ChatRequest):
    """
    Send natural-language question to InsightOps agent.
    Gemini selects tools, backend executes Python operations on the dataset,
    and returns verified answers, numerical results, execution traces, and charts.
    """
    # 1. Resolve or create session
    session_id = req.session_id
    if not session_id:
        session_id = ConversationMemory.create_session(
            dataset_id=req.dataset_id,
            title=req.message[:35] + ("..." if len(req.message) > 35 else "")
        )
    else:
        # Update session dataset if changed
        ConversationMemory.update_session_dataset(session_id, req.dataset_id)
        
    # 2. Retrieve dataset
    try:
        df = DatasetService.get_dataset_df(req.dataset_id)
        dataset_meta = DatasetService.get_dataset_metadata(req.dataset_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Selected dataset not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to access dataset: {str(e)}")

    if not dataset_meta:
        raise HTTPException(status_code=404, detail="Dataset metadata missing.")

    # 3. Run Agent
    executor = AgentExecutor()
    try:
        structured_resp = executor.run_analysis(
            session_id=session_id,
            user_message=req.message,
            df=df,
            dataset_meta=dataset_meta
        )
    except ValueError as ve:
        # e.g. API key missing
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent analysis failed: {str(e)}")

    # 4. Save both user message and assistant response to memory
    ConversationMemory.save_message(
        session_id=session_id,
        role="user",
        content=req.message
    )
    assistant_msg_id = ConversationMemory.save_message(
        session_id=session_id,
        role="assistant",
        content=structured_resp.answer,
        structured_data=structured_resp.model_dump()
    )

    # Auto-update session title if it was first message
    history = ConversationMemory.get_conversation_history(session_id, limit=5)
    if len(history) <= 2:
        clean_title = req.message.replace("?", "").replace("!", "").strip()
        if len(clean_title) > 40:
            clean_title = clean_title[:40] + "..."
        ConversationMemory.update_session_title(session_id, clean_title.capitalize())

    return ChatResponse(
        session_id=session_id,
        message_id=assistant_msg_id,
        role="assistant",
        response=structured_resp,
        created_at=datetime.now().isoformat()
    )

@router.get("/history/{session_id}", response_model=List[MessageHistoryItem])
def get_session_history(session_id: str):
    """Retrieve full chronological conversation history and traces for a session."""
    messages = ConversationMemory.get_conversation_history(session_id, limit=50)
    history_items = []
    for m in messages:
        struct_obj = None
        if m.get("structured_data"):
            try:
                struct_obj = StructuredAnalysisResponse(**m["structured_data"])
            except Exception:
                struct_obj = None
        history_items.append(MessageHistoryItem(
            id=m["id"],
            session_id=m["session_id"],
            role=m["role"],
            content=m["content"],
            structured_data=struct_obj,
            created_at=m["created_at"]
        ))
    return history_items

@router.delete("/history/{session_id}", status_code=204)
def delete_session(session_id: str):
    """Delete a conversation session and all its associated messages and tool traces."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return None
