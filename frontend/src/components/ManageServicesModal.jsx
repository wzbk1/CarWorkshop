import React, { useState, useEffect } from 'react';
import api from '../api';

const ManageServicesModal = ({ workshop, onClose }) => {
  const [services, setServices] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ name: "", duration_minutes: 60, price: 100, description: "" });

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const res = await api.get(`/services/locations/${workshop.id}/services`);
      setServices(res.data);
    } catch (err) { console.error(err); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/services/locations/${workshop.id}/services`, form);
      setShowAdd(false);
      setForm({ name: "", duration_minutes: 60, price: 100, description: "" });
      fetchServices();
    } catch (err) { alert(err.response?.data?.detail || "Błąd dodawania usługi"); }
  };

  const handleDelete = async (id) => {
    if (confirm("Usunąć usługę?")) {
      try {
        await api.delete(`/services/${id}`);
        fetchServices();
      } catch (err) { alert(err.response?.data?.detail || "Błąd usuwania usługi"); }
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2>Usługi: {workshop.name}</h2>
          <button className="btn" onClick={onClose}><i className="fas fa-times"></i></button>
        </div>

        <button className="btn btn-primary" style={{ marginBottom: '20px' }} onClick={() => setShowAdd(!showAdd)}>
          {showAdd ? 'Anuluj' : 'Dodaj Usługę'}
        </button>

        {showAdd && (
          <form onSubmit={handleSubmit} className="card glass" style={{ marginBottom: '20px', padding: '15px' }}>
            <div className="form-group">
              <label className="form-label">Nazwa</label>
              <input className="form-control" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Czas (min)</label>
                <input className="form-control" type="number" value={form.duration_minutes} onChange={e => setForm({...form, duration_minutes: parseInt(e.target.value)})} required />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Cena (zł)</label>
                <input className="form-control" type="number" value={form.price} onChange={e => setForm({...form, price: parseFloat(e.target.value)})} required />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Zapisz</button>
          </form>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {services.map(s => (
            <div key={s.id} className="card glass" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px' }}>
              <div>
                <strong>{s.name}</strong>
                <div className="text-muted">{s.duration_minutes} min | {s.price} zł</div>
              </div>
              <button className="btn" style={{ color: 'var(--danger)' }} onClick={() => handleDelete(s.id)}>
                <i className="fas fa-trash"></i>
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ManageServicesModal;
