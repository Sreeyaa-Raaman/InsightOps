import json
import uuid
from typing import List, Dict, Any, Optional
from google.genai import types
from app.database.connection import get_db
from app.models.schemas import StructuredAnalysisResponse, ToolExecutionTraceItem

class ConversationMemory:
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            return cursor.fetchone()

    @staticmethod
    def create_session(dataset_id: Optional[str] = None, title: str = "New Analysis") -> str:
        session_id = str(uuid.uuid4())
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (id, title, dataset_id) VALUES (?, ?, ?)",
                (session_id, title, dataset_id)
            )
        return session_id

    @staticmethod
    def update_session_title(session_id: str, title: str):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sessions SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (title, session_id)
            )

    @staticmethod
    def update_session_dataset(session_id: str, dataset_id: str):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sessions SET dataset_id = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (dataset_id, session_id)
            )

    @staticmethod
    def save_message(
        session_id: str,
        role: str,
        content: str,
        structured_data: Optional[Dict[str, Any]] = None
    ) -> str:
        msg_id = str(uuid.uuid4())
        struct_json = json.dumps(structured_data) if structured_data else None
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (id, session_id, role, content, structured_data) VALUES (?, ?, ?, ?, ?)",
                (msg_id, session_id, role, content, struct_json)
            )
            cursor.execute("UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (session_id,))
        return msg_id

    @staticmethod
    def log_tool_execution(
        session_id: str,
        message_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        result: Dict[str, Any],
        execution_time_ms: float
    ):
        tool_id = str(uuid.uuid4())
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO tool_executions (id, session_id, message_id, tool_name, arguments_json, result_json, execution_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (tool_id, session_id, message_id, tool_name, json.dumps(arguments), json.dumps(result), execution_time_ms)
            )

    @staticmethod
    def get_conversation_history(session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC LIMIT ?",
                (session_id, limit)
            )
            rows = cursor.fetchall()
            messages = []
            for r in rows:
                struct = None
                if r.get("structured_data"):
                    try:
                        struct = json.loads(r["structured_data"])
                    except Exception:
                        struct = None
                messages.append({
                    "id": r["id"],
                    "session_id": r["session_id"],
                    "role": r["role"],
                    "content": r["content"],
                    "structured_data": struct,
                    "created_at": str(r["created_at"])
                })
            return messages

    @staticmethod
    def get_history_contents_for_gemini(session_id: str, max_turns: int = 6) -> List[types.Content]:
        """Convert recent message history into Gemini Content objects for context, strictly alternating user and model."""
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
                (session_id, max_turns * 2)
            )
            rows = cursor.fetchall()
            
        rows.reverse()
        contents = []
        last_role = None
        
        for r in rows:
            role = "user" if r["role"] == "user" else "model"
            # Avoid consecutive identical roles in prompt context
            if role == last_role:
                continue
                
            txt = r["content"]
            if len(txt) > 800:
                txt = txt[:800] + "... [context truncated]"
                
            contents.append(types.Content(
                role=role,
                parts=[types.Part.from_text(text=txt)]
            ))
            last_role = role
            
        # Ensure context ends with 'model' so the next added turn is 'user'
        if contents and contents[-1].role == "user":
            contents.pop()
            
        return contents
