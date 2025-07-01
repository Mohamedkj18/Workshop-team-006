from sklearn.cluster import KMeans
import numpy as np
from db.database import SessionLocal
from db.models import EmailReplyPair, StyleCluster
from services.feature_extraction import extract_features_from_emails


def cluster_reply_styles(user_id: str, n_clusters: int = 3):
    db = SessionLocal()
    pairs = db.query(EmailReplyPair).filter_by(user_id=user_id).all()

    if len(pairs) < n_clusters:
        db.close()
        return None

    # Extract incoming email vectors and corresponding reply vectors
    incoming_vectors = [list(extract_features_from_emails([pair.incoming_email]).values()) for pair in pairs]
    reply_vectors = [list(extract_features_from_emails([pair.reply_email]).values()) for pair in pairs]

    kmeans = KMeans(n_clusters=n_clusters, random_state=42).fit(incoming_vectors)
    labels = kmeans.labels_

    # Remove old clusters
    db.query(StyleCluster).filter_by(user_id=user_id).delete()

    for cluster_id in range(n_clusters):
        # Get all reply vectors that belong to this cluster
        cluster_reply_vectors = [reply_vectors[i] for i in range(len(labels)) if labels[i] == cluster_id]

        if not cluster_reply_vectors:
            continue

        avg_reply_vector = np.mean(cluster_reply_vectors, axis=0).tolist()
        email_centroid = kmeans.cluster_centers_[cluster_id].tolist()

        db.add(StyleCluster(
            user_id=user_id,
            cluster_id=cluster_id,
            centroid_vector=email_centroid,
            reply_style_vector=avg_reply_vector
        ))

    db.commit()
    db.close()
    return True


def init_reply_clusters(user_id: str, pairs: list[list[str]]):
    if not pairs:
        return None
    db = SessionLocal()
    for pair in pairs:
        email, reply = pair
        if not email or not reply:
            continue
        db.add(EmailReplyPair(
            user_id=user_id,
            incoming_email=email,
            reply_email=reply
        ))
    db.commit()
    db.close()
    return cluster_reply_styles(user_id)
     


