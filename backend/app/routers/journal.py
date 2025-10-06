"""Journal router: entries, AI analysis, and summaries."""
from typing import Any, List, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from ..models.user import User
from app.routers.auth import get_current_user
from ..models.journal import JournalEntry, JournalAnalysis

router = APIRouter(prefix="/journal", tags=["journal"])


@router.post("/entries", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_entry(
    payload: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    content = (payload.get("content") or "").strip()
    if not content:
        raise HTTPException(status_code=422, detail="content required")
    tags = payload.get("tags") or []
    user_mood = payload.get("user_mood")
    is_private = bool(payload.get("is_private", True))

    entry = JournalEntry(
        user_id=current_user.id,
        content=content,
        tags=tags,
        user_mood=user_mood,
        is_private=is_private,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)

    # Best-effort AI analysis (non-blocking pattern but synchronous MVP)
    try:
        from app.services.ai_service import AIService
        from app.services.memory_service import MemoryService
        ai = AIService()
        if not ai.is_available:
            await ai.initialize()

        analysis_data = {
            "mood_score": None,
            "valence": None,
            "arousal": None,
            "emotions": None,
            "topics": None,
            "triggers": None,
            "suggestions": None,
            "keywords": None,
            "summary": None,
            "safety_flags": None,
        }

        if getattr(ai, "llm", None) is not None:
            prompt = (
                "Analyze the following journal entry and return a compact JSON with fields:"
                " mood_score(-5..5), valence(0..1), arousal(0..1), emotions([{'label','score'}]),"
                " topics([str]), triggers([str]), suggestions([str]), keywords([str]), summary(str), safety_flags([str]).\n"
                f"Text: {content}"
            )
            try:
                raw = ai.llm.invoke(prompt)
                import json
                parsed = json.loads(str(raw)) if raw else {}
                analysis_data.update({k: parsed.get(k) for k in analysis_data.keys()})
            except Exception:
                # fallback: simple sentiment-like defaults
                analysis_data.update({
                    "mood_score": 0,
                    "emotions": [{"label": "neutral", "score": 0.5}],
                    "summary": content[:160] + ("…" if len(content) > 160 else ""),
                })
        else:
            analysis_data.update({
                "mood_score": 0,
                "emotions": [{"label": "neutral", "score": 0.5}],
                "summary": content[:160] + ("…" if len(content) > 160 else ""),
            })

        ja = JournalAnalysis(journal_id=entry.id, **analysis_data)
        db.add(ja)
        db.commit()
        db.refresh(ja)

        # Index a compact memory for Assistant RAG
        try:
            ms = MemoryService()
            snippet = ja.summary or content[:200]
            ms.store_memory(user_id=current_user.id, content=snippet, memory_type="journal", metadata={"journal_id": entry.id, "tags": tags})
        except Exception:
            pass
    except Exception:
        pass

    return {"id": entry.id}


@router.get("/entries", response_model=List[dict])
async def list_entries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
) -> Any:
    qry = db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id).order_by(JournalEntry.created_at.desc())
    if q:
        like = f"%{q}%"
        qry = qry.filter(JournalEntry.content.ilike(like))
    items = qry.limit(limit).all()
    # include analysis snapshot if present
    out = []
    for e in items:
        d = {
            "id": e.id,
            "content": e.content,
            "tags": e.tags or [],
            "user_mood": e.user_mood,
            "created_at": e.created_at,
        }
        if e.analysis:
            d["analysis"] = {
                "mood_score": e.analysis.mood_score,
                "emotions": e.analysis.emotions,
                "summary": e.analysis.summary,
                "topics": e.analysis.topics,
                "triggers": e.analysis.triggers,
            }
        out.append(d)
    return out


@router.get("/entries/{entry_id}", response_model=dict)
async def get_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    e = db.query(JournalEntry).filter(JournalEntry.id == entry_id, JournalEntry.user_id == current_user.id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Not found")
    d = {
        "id": e.id,
        "content": e.content,
        "tags": e.tags or [],
        "user_mood": e.user_mood,
        "created_at": e.created_at,
    }
    if e.analysis:
        d["analysis"] = {
            "mood_score": e.analysis.mood_score,
            "valence": e.analysis.valence,
            "arousal": e.analysis.arousal,
            "emotions": e.analysis.emotions,
            "topics": e.analysis.topics,
            "triggers": e.analysis.triggers,
            "suggestions": e.analysis.suggestions,
            "summary": e.analysis.summary,
            "safety_flags": e.analysis.safety_flags,
        }
    return d


@router.delete("/entries/{entry_id}")
async def delete_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    e = db.query(JournalEntry).filter(JournalEntry.id == entry_id, JournalEntry.user_id == current_user.id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(e)
    db.commit()
    return {"deleted": 1}


@router.get("/summary", response_model=dict)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(7, ge=1, le=90)
) -> Any:
    """Quick aggregate: avg mood score, top emotions, frequent topics in recent range."""
    since = datetime.utcnow() - timedelta(days=days)
    entries = db.query(JournalEntry).filter(JournalEntry.user_id == current_user.id, JournalEntry.created_at >= since).all()
    analyses = [e.analysis for e in entries if e.analysis]
    mood_scores = [a.mood_score for a in analyses if a and a.mood_score is not None]
    avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else None
    # flatten emotions
    from collections import Counter
    emo = Counter()
    topics = Counter()
    for a in analyses:
        for it in (a.emotions or []):
            lab = it.get("label") if isinstance(it, dict) else None
            if lab:
                emo[lab] += 1
        for t in (a.topics or []):
            topics[str(t)] += 1
    return {
        "avg_mood": avg_mood,
        "top_emotions": emo.most_common(5),
        "top_topics": topics.most_common(5),
        "count": len(entries),
    }
