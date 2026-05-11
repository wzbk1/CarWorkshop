import React, { useState } from 'react';

const ReviewModal = ({ booking, onClose, onSubmit }) => {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      location_id: booking.location_id,
      rating,
      comment
    });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={e => e.stopPropagation()}>
        <h2>Wystaw opinię</h2>
        <p className="text-muted" style={{ marginBottom: '20px' }}>{booking.service_name} w {booking.location_name}</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Ocena (1-5)</label>
            <div style={{ display: 'flex', gap: '15px', fontSize: '2rem', color: '#ffc107', marginBottom: '10px' }}>
              {[1, 2, 3, 4, 5].map(star => (
                <i 
                  key={star} 
                  className={`fa-star ${rating >= star ? 'fas' : 'far'}`} 
                  style={{ cursor: 'pointer' }}
                  onClick={() => setRating(star)}
                />
              ))}
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label">Twoja opinia</label>
            <textarea 
              className="form-control" 
              value={comment} 
              onChange={e => setComment(e.target.value)} 
              placeholder="Jak oceniasz usługę?"
              rows="4"
              required
            />
          </div>

          <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
            <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Wyślij opinię</button>
            <button type="button" className="btn btn-outline" style={{ flex: 1 }} onClick={onClose}>Anuluj</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ReviewModal;
