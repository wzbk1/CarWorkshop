import React, { useState, useEffect } from 'react';

const ReviewsListModal = ({ location, onClose, apiJson }) => {
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState({ avg_rating: 0, count: 0 });

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const data = await apiJson(`/reviews/locations/${location.id}`);
      setReviews(data.reviews || []);
      setStats({ avg_rating: data.avg_rating, count: data.count });
    } catch (err) { console.error(err); }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div>
            <h2 style={{ margin: 0 }}>Opinie: {location.name}</h2>
            <div style={{ color: '#ffc107', fontSize: '1.2rem', marginTop: '5px' }}>
              <i className="fas fa-star"></i> {stats.avg_rating?.toFixed(1)} ({stats.count} opinii)
            </div>
          </div>
          <button className="btn" onClick={onClose}><i className="fas fa-times"></i></button>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {reviews.length > 0 ? reviews.map(r => (
            <div key={r.id} className="card glass" style={{ padding: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                <div style={{ fontWeight: 700 }}>{r.user_name || r.user_email}</div>
                <div style={{ color: '#ffc107' }}>
                  {Array.from({ length: r.rating }).map((_, i) => <i key={i} className="fas fa-star"></i>)}
                </div>
              </div>
              <p style={{ fontStyle: 'italic' }}>"{r.comment || 'Brak komentarza'}"</p>
              <div className="text-muted" style={{ fontSize: '0.8rem', marginTop: '10px' }}>
                {new Date(r.created_at).toLocaleDateString()}
              </div>
            </div>
          )) : (
            <div className="text-center text-muted" style={{ padding: '30px' }}>
              Brak opinii dla tego warsztatu.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReviewsListModal;
