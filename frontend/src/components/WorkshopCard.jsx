import React, { useState, useEffect } from 'react';
import api from '../api';

const WorkshopCard = ({ workshop, isAdmin, onBook, onManageServices, onManageMechanics, onManageHours }) => {
  const [brands, setBrands] = useState([]);
  const [reviewStats, setReviewStats] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [showReviews, setShowReviews] = useState(false);

  useEffect(() => {
    if (workshop?.id) {
      api.get(`/car-brands/locations/${workshop.id}/brands`)
        .then(res => setBrands(res.data))
        .catch(err => console.error(err));
      api.get(`/reviews/location/${workshop.id}/stats`)
        .then(res => setReviewStats(res.data))
        .catch(err => console.error(err));
    }
  }, [workshop?.id]);

  const handleToggleReviews = async () => {
    if (!showReviews && reviews.length === 0) {
      try {
        const res = await api.get(`/reviews/location/${workshop.id}`);
        setReviews(res.data);
      } catch (err) {
        console.error(err);
      }
    }
    setShowReviews(!showReviews);
  };

  if (!workshop) return null;

  const renderStars = (rating) => {
    return [1,2,3,4,5].map(s => (
      <span key={s} style={{ color: s <= rating ? '#ffc107' : 'rgba(255,255,255,0.15)', fontSize: '0.9rem' }}>★</span>
    ));
  };

  return (
    <div className="card glass">
      <div className="card-header">
        <div>
          <h3 className="workshop-name">{workshop.name}</h3>
          <p className="workshop-location">
            <i className="fas fa-map-marker-alt" style={{ color: 'var(--primary)' }}></i> 
            {workshop.address}, {workshop.city}
          </p>
        </div>
        <div 
          className="badge badge-blue" 
          style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
          onClick={handleToggleReviews}
          title="Kliknij, aby zobaczyć opinie"
        >
          <i className="fas fa-star"></i>
          {reviewStats && reviewStats.total_reviews > 0 
            ? `${reviewStats.average_rating.toFixed(1)} (${reviewStats.total_reviews})` 
            : 'Nowy'}
        </div>
      </div>
      
      <p className="workshop-description">
        {workshop.description || 'Profesjonalny autoryzowany serwis.'}
      </p>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '20px' }}>
        {brands?.map(brand => (
          <span key={brand.id} className="badge" style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid var(--border)' }}>
            {brand.name}
          </span>
        ))}
        {brands.length === 0 && <span className="text-muted" style={{ fontSize: '0.85rem' }}>Obsługa wszystkich marek</span>}
      </div>

      {}
      {showReviews && (
        <div style={{ 
          borderTop: '1px solid var(--border)', 
          paddingTop: '16px', 
          marginBottom: '16px',
          maxHeight: '300px',
          overflowY: 'auto'
        }}>
          <h4 style={{ fontSize: '1rem', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <i className="fas fa-comments" style={{ color: 'var(--primary)' }}></i>
            Opinie klientów
            {reviewStats && <span style={{ color: 'var(--text-secondary)', fontWeight: 400, fontSize: '0.85rem' }}>
              ({reviewStats.total_reviews})
            </span>}
          </h4>

          {reviews.length > 0 ? reviews.map(r => (
            <div key={r.id} style={{ 
              padding: '12px 14px', 
              marginBottom: '10px', 
              background: 'rgba(255,255,255,0.03)', 
              borderRadius: '10px',
              border: '1px solid var(--border)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ 
                    width: '32px', height: '32px', borderRadius: '50%', 
                    background: 'var(--primary)', color: 'white', 
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '0.75rem', fontWeight: 700, flexShrink: 0
                  }}>
                    {r.user_name?.[0]?.toUpperCase() || '?'}
                  </div>
                  <div>
                    <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{r.user_name}</span>
                    <div>{renderStars(r.rating)}</div>
                  </div>
                </div>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                  {r.created_at ? new Date(r.created_at).toLocaleDateString('pl-PL') : ''}
                </span>
              </div>
              {r.comment && (
                <p style={{ margin: '6px 0 0 42px', color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: '1.5' }}>
                  {r.comment}
                </p>
              )}
            </div>
          )) : (
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', textAlign: 'center', padding: '15px 0' }}>
              Brak opinii — bądź pierwszy!
            </p>
          )}
        </div>
      )}

      <div className="card-footer">
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button className="btn btn-primary" onClick={onBook}>
            Umów wizytę
          </button>
          <button 
            className="btn btn-outline" 
            onClick={handleToggleReviews}
            style={{ padding: '10px 16px' }}
          >
            <i className={`fas fa-${showReviews ? 'chevron-up' : 'comments'}`}></i>
            {showReviews ? ' Ukryj' : ' Opinie'}
          </button>
        </div>
        
        {isAdmin && (
          <div className="workshop-actions">
            <button className="btn btn-outline" onClick={onManageServices} title="Zarządzaj usługami">
              <i className="fas fa-tools"></i>
            </button>
            <button className="btn btn-outline" onClick={onManageMechanics} title="Mechanicy">
              <i className="fas fa-users-cog"></i>
            </button>
            <button className="btn btn-outline" onClick={onManageHours} title="Godziny pracy">
              <i className="fas fa-clock"></i>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default WorkshopCard;
