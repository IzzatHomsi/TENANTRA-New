import pytest

def test_user_has_required_relationships():
    # Importing inside test ensures mapper config runs with package side-effects
    from app.models import User
    rels = set(User.__mapper__.relationships.keys())
    # These relationships must exist for mapper back_populates consistency
    assert "refresh_tokens" in rels, "User.refresh_tokens relationship is missing"
    assert "notification_settings" in rels, "User.notification_settings relationship is missing"

def test_notification_setting_inverse_if_present():
    # If NotificationSetting exists in this deployment, verify inverse mapping
    from app.models import NotificationSetting, User
    if NotificationSetting is None:
        pytest.skip("NotificationSetting model not present in this build")
    rels = NotificationSetting.__mapper__.relationships
    assert "user" in rels, "NotificationSetting.user inverse relationship is missing"
    assert rels["user"].mapper.class_ is User, "NotificationSetting.user should map to User"
