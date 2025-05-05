from .models import UserActivity

def track_activity(user, action, dataset=None, dashboard=None, **kwargs):
    """
    Record user activity
    
    Args:
        user: User performing the action
        action: String from UserActivity.ACTION_CHOICES
        dataset: Optional Dataset instance
        dashboard: Optional MetabaseDashboard instance
        **kwargs: Additional details to store in the JSON field
    """
    UserActivity.objects.create(
        user=user,
        action=action,
        dataset=dataset,
        dashboard=dashboard,
        details=kwargs
    )