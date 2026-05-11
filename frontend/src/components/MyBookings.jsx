import React, { useState, useEffect } from 'react';
import api from '../api';

const MyBookings = ({ isAdmin }) => {
  const [bookings, setBookings] = useState([]);
  const [myReviews, setMyReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  
  const [reviewingBooking, setReviewingBooking] = useState(null);
  const [editingReview, setEditingReview] = useState(null); 
  const [reviewRating, setReviewRating] = useState(5);
  const [reviewComment, setReviewComment] = useState("");
  const [reviewSubmitting, setReviewSubmitting] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [bRes, rRes] = await Promise.all([
        api.get(isAdmin ? "/bookings/all" : "/bookings/me"),
        isAdmin ? Promise.resolve({ data: [] }) : api.get("/reviews/me")
      ]);
      setBookings(bRes.data);
      setMyReviews(rRes.data);
    } catch (err) {
      console.error("Błąd pobierania danych:", err);
    } finally {
      setLoading(false);
    }
  };

  const getReviewForLocation = (locationId) => {
    return myReviews.find(r => r.location_id === locationId);
  };

  const handleCancel = async (id) => {
    if (confirm("Na pewno odwołać tę rezerwację?")) {
      try {
        await api.patch(`/bookings/${id}/cancel`);
        fetchData();
      } catch (err) {
        alert(err.response?.data?.detail || "Błąd odwoływania rezerwacji");
      }
    }
  };

  const handleComplete = async (id) => {
    if (confirm("Oznaczyć rezerwację jako zakończoną?")) {
      try {
        await api.patch(`/bookings/${id}/complete`);
        fetchData();
      } catch (err) {
        alert(err.response?.data?.detail || "Błąd zmiany statusu");
      }
    }
  };

  const openNewReview = (booking) => {
    setReviewingBooking(booking);
    setEditingReview(null);
    setReviewRating(5);
    setReviewComment("");
  };

  const openEditReview = (booking, review) => {
    setReviewingBooking(booking);
    setEditingReview(review);
    setReviewRating(review.rating);
    setReviewComment(review.comment || "");
  };

  const handleDeleteReview = async (reviewId) => {
    if (confirm("Na pewno usunąć opinię?")) {
      try {
        await api.delete(`/reviews/${reviewId}`);
        fetchData();
      } catch (err) {
        alert(err.response?.data?.detail || "Błąd usuwania opinii");
      }
    }
  };

  const handleReviewSubmit = async () => {
    if (!reviewingBooking) return;
    setReviewSubmitting(true);
    try {
      if (editingReview) {
        await api.put(`/reviews/${editingReview.id}`, {
          rating: reviewRating,
          comment: reviewComment || null
        });
      } else {
        await api.post("/reviews/", {
          location_id: reviewingBooking.location_id,
          rating: reviewRating,
          comment: reviewComment || null
        });
      }
      setReviewingBooking(null);
      setEditingReview(null);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Błąd zapisywania opinii");
    } finally {
      setReviewSubmitting(false);
    }
  };

  const getStatusLabel = (status) => {
    switch(status) {
      case 'CANCELLED': return 'Odwołana';
      case 'COMPLETED': return 'Zakończona';
      default: return 'Zarezerwowana';
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'CANCELLED': return 'var(--danger)';
      case 'COMPLETED': return 'var(--success)';
      default: return 'var(--primary)';
    }
  };

  const renderStars = (rating) => {
    return [1,2,3,4,5].map(s => (
      <span key={s} style={{ color: s <= rating ? '#ffc107' : 'var(--text-secondary)', fontSize: '0.85rem' }}>★</span>
    ));
  };

  if (loading) return <div style={{ padding: '50px', textAlign: 'center', color: 'var(--text-secondary)' }}>Ładowanie rezerwacji...</div>;

  return (
    <div className="container">
      <h1 style={{ marginBottom: '30px' }}>{isAdmin ? 'Wszystkie Rezerwacje' : 'Moje Rezerwacje'}</h1>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        {bookings.length > 0 ? bookings.map(b => {
          const existingReview = getReviewForLocation(b.location_id);

          return (
            <div key={b.id} className="card glass" style={{ borderLeft: `5px solid ${getStatusColor(b.status)}` }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '15px' }}>
                <div style={{ flex: 1, minWidth: '250px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                    <i className="fas fa-warehouse" style={{ color: 'var(--primary)', fontSize: '0.9rem' }}></i>
                    <span style={{ fontWeight: 700, fontSize: '1.15rem', color: 'var(--primary)' }}>{b.location_name || 'Warsztat'}</span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                    <h3 style={{ margin: 0 }}>{b.service_name}</h3>
                    <span className="badge" style={{ 
                      background: `${getStatusColor(b.status)}15`,
                      color: getStatusColor(b.status)
                    }}>
                      {getStatusLabel(b.status)}
                    </span>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginTop: '10px', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
                    <span><i className="fas fa-calendar-alt" style={{ marginRight: '6px' }}></i>{b.appointment_date}</span>
                    <span><i className="fas fa-clock" style={{ marginRight: '6px' }}></i>{b.appointment_time?.substring(0,5)}</span>
                    <span><i className="fas fa-user-cog" style={{ marginRight: '6px' }}></i>{b.employee_name}</span>
                    <span><i className="fas fa-hourglass-half" style={{ marginRight: '6px' }}></i>{b.service_duration_minutes} min</span>
                    {isAdmin && <span><i className="fas fa-envelope" style={{ marginRight: '6px' }}></i>{b.user_email}</span>}
                  </div>

                  {}
                  {b.status === 'COMPLETED' && existingReview && !isAdmin && (
                    <div style={{ marginTop: '12px', padding: '10px 14px', background: 'rgba(255,193,7,0.08)', borderRadius: '10px', border: '1px solid rgba(255,193,7,0.2)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>Twoja ocena:</span>
                        {renderStars(existingReview.rating)}
                      </div>
                      {existingReview.comment && (
                        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>„{existingReview.comment}"</p>
                      )}
                    </div>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
                  {b.status === 'BOOKED' && (
                    <>
                      {isAdmin && (
                        <button className="btn btn-primary" style={{ background: 'var(--success)', padding: '8px 16px', fontSize: '0.85rem' }} onClick={() => handleComplete(b.id)}>
                          <i className="fas fa-check"></i> Zakończ
                        </button>
                      )}
                      <button className="btn btn-outline" style={{ color: 'var(--danger)', borderColor: 'var(--danger)', padding: '8px 16px', fontSize: '0.85rem' }} onClick={() => handleCancel(b.id)}>
                        <i className="fas fa-times"></i> Odwołaj
                      </button>
                    </>
                  )}
                  {b.status === 'COMPLETED' && !isAdmin && (
                    existingReview ? (
                      <>
                        <button className="btn btn-outline" style={{ padding: '8px 14px', fontSize: '0.85rem' }} onClick={() => openEditReview(b, existingReview)}>
                          <i className="fas fa-edit"></i> Edytuj
                        </button>
                        <button className="btn btn-outline" style={{ color: 'var(--danger)', borderColor: 'var(--danger)', padding: '8px 14px', fontSize: '0.85rem' }} onClick={() => handleDeleteReview(existingReview.id)}>
                          <i className="fas fa-trash-alt"></i>
                        </button>
                      </>
                    ) : (
                      <button className="btn btn-primary" style={{ padding: '8px 16px', fontSize: '0.85rem' }} onClick={() => openNewReview(b)}>
                        <i className="fas fa-star"></i> Wystaw opinię
                      </button>
                    )
                  )}
                </div>
              </div>
            </div>
          );
        }) : (
          <div className="card glass" style={{ padding: '50px', textAlign: 'center' }}>
            <i className="fas fa-calendar-times" style={{ fontSize: '3rem', color: 'var(--text-secondary)', marginBottom: '20px', display: 'block' }}></i>
            <h3>Brak rezerwacji</h3>
            <p style={{ color: 'var(--text-secondary)' }}>Nie masz jeszcze żadnych zaplanowanych wizyt.</p>
          </div>
        )}
      </div>

      {}
      {reviewingBooking && (
        <div className="modal-overlay" onClick={() => setReviewingBooking(null)}>
          <div className="modal-content glass" onClick={e => e.stopPropagation()} style={{ maxWidth: '480px' }}>
            <div className="modal-header">
              <h2>{editingReview ? 'Edytuj opinię' : 'Wystaw opinię'}</h2>
            </div>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
              <strong>{reviewingBooking.service_name}</strong> w <strong>{reviewingBooking.location_name}</strong>
            </p>

            <div className="form-group">
              <label className="form-label">Ocena</label>
              <div style={{ display: 'flex', gap: '8px', fontSize: '2rem' }}>
                {[1,2,3,4,5].map(star => (
                  <span 
                    key={star} 
                    onClick={() => setReviewRating(star)}
                    style={{ cursor: 'pointer', color: star <= reviewRating ? '#ffc107' : 'var(--text-secondary)', transition: 'color 0.15s' }}
                  >
                    ★
                  </span>
                ))}
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Komentarz (opcjonalnie)</label>
              <textarea 
                className="form-control" 
                rows="4" 
                value={reviewComment}
                onChange={e => setReviewComment(e.target.value)}
                placeholder="Opisz swoje doświadczenie..."
              />
            </div>

            <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
              <button className="btn btn-primary" style={{ flex: 1 }} onClick={handleReviewSubmit} disabled={reviewSubmitting}>
                {reviewSubmitting ? 'Zapisywanie...' : (editingReview ? 'Zapisz zmiany' : 'Wyślij opinię')}
              </button>
              <button className="btn btn-outline" style={{ flex: 1 }} onClick={() => setReviewingBooking(null)}>
                Anuluj
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MyBookings;
