async def trigger_study_generation(user_input, intent, user_id, db, marks, model, source="chat"):
    from DB.db_models import StudySessions, Notes, FlashCards
    import uuid
    from datetime import datetime, timezone
    from api.routes.study_tools import flashcard, note  # your existing methods

    # Create a session title based on the user_input
    title = user_input[:50] + "..." if len(user_input) > 50 else user_input

    session = StudySessions(
        user_id=user_id,
        title=title,
        file_name="untitled",
        file_type=intent,
        created_at=datetime.now(timezone.utc),
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    if intent == "notes":
        notes_text = await note(user_input, marks)
        db.add(Notes(
            id=uuid.uuid4(),
            user_id=user_id,
            session_id=session.id,
            content=notes_text,
            source_type=source,
            created_at=datetime.now(timezone.utc)
        ))

    elif intent == "flashcards":
        response = await flashcard(user_input, marks)
        for qa_block in response.split("Q:")[1:]:
            if "A:" in qa_block:
                q, a = qa_block.split("A:", 1)
                db.add(FlashCards(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    session_id=session.id,
                    question=q.strip(),
                    answer=a.strip(),
                    source_type=source,
                    created_at=datetime.now(timezone.utc),
                ))

    db.commit()
