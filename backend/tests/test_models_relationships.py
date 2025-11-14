def test_user_has_required_relationships():
    # Importing inside test ensures mapper config runs with package side-effects
    from app.models import User
    rels = set(User.__mapper__.relationships.keys())
    # These relationships must exist for mapper back_populates consistency
    assert "refresh_tokens" in rels, "User.refresh_tokens relationship is missing"
