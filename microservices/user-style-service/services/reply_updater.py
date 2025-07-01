from db.database import SessionLocal
from db.models import StyleCluster, ClusterStatus
from services.feature_extraction import extract_features_from_emails
from services.reply_cluster import cluster_reply_styles
from utils.similarity import cosine_similarity
import numpy as np

CLUSTER_TRIGGER_THRESHOLD = 10

def update_reply_style_vector(user_id: str, incoming_email: str, reply_email: str):
    db = SessionLocal()

    # Extract feature vector of the incoming email
    incoming_vec = list(extract_features_from_emails([incoming_email]).values())

    # Find all clusters for this user
    clusters = db.query(StyleCluster).filter_by(user_id=user_id).all()
    if not clusters:
        db.close()
        return False  # No clusters exist yet

    # Find closest cluster
    similarities = [cosine_similarity(incoming_vec, cluster.centroid_vector) for cluster in clusters]
    best_idx = int(np.argmax(similarities))
    best_cluster = clusters[best_idx]

    # Extract new reply vector
    reply_vec = list(extract_features_from_emails([reply_email]).values())

    # Update reply_style_vector using moving average
    old_vec = np.array(best_cluster.reply_style_vector or np.zeros(len(reply_vec)))
    count = best_cluster.sample_count or 0
    new_vec = ((old_vec * count) + np.array(reply_vec)) / (count + 1)

    best_cluster.reply_style_vector = new_vec.tolist()
    best_cluster.sample_count = count + 1

    # Update counter in ClusterStatus
    status = db.query(ClusterStatus).filter_by(user_id=user_id).first()
    if not status:
        status = ClusterStatus(user_id=user_id, pair_count_since_last_cluster=1)
        db.add(status)
    else:
        status.pair_count_since_last_cluster += 1

    # Retrigger full clustering if threshold exceeded
    if status.pair_count_since_last_cluster >= CLUSTER_TRIGGER_THRESHOLD:
        cluster_reply_styles(user_id)
        status.pair_count_since_last_cluster = 0

    db.commit()
    db.close()
    return True
