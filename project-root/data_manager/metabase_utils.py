import jwt
import time

def generate_metabase_url(metabase_config, dashboard_id, params=None):
    """
    Generate a signed URL for embedding Metabase dashboards
    
    Args:
        metabase_config: MetabaseConfig instance
        dashboard_id: ID of the dashboard in Metabase
        params: Optional parameters for the dashboard
        
    Returns:
        URL string for embedding
    """
    payload = {
        "resource": {"dashboard": dashboard_id},
        "params": params or {},
        "exp": round(time.time()) + (60 * 60)  # 1 hour expiration
    }
    
    token = jwt.encode(
        payload,
        metabase_config.secret_key,
        algorithm="HS256"
    )
    
    return f"{metabase_config.site_url}/embed/dashboard/{token}#bordered=true&titled=true"