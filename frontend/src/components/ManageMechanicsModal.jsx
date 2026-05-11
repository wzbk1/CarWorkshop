import React, { useState, useEffect } from 'react';
import api from '../api';

const ManageMechanicsModal = ({ workshop, onClose }) => {
  const [mechanics, setMechanics] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", specialization: "" });

  const [allServices, setAllServices] = useState([]);
  const [selectedServiceId, setSelectedServiceId] = useState("");

  useEffect(() => {
    fetchMechanics();
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const res = await api.get(`/services/locations/${workshop.id}/services`);
      setAllServices(res.data);
    } catch (err) { console.error(err); }
  };

  const fetchMechanics = async () => {
    try {
      const res = await api.get(`/employees/locations/${workshop.id}/employees`);
      setMechanics(res.data);
    } catch (err) { console.error(err); }
  };

  const handleAssignService = async (empId) => {
    if (!selectedServiceId) return;
    try {
      await api.post(`/employees/${empId}/services`, { service_id: parseInt(selectedServiceId) });
      alert("Usługa przypisana!");
      fetchMechanics();
    } catch (err) { alert(err.response?.data?.detail || "Błąd"); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post(`/employees/locations/${workshop.id}/employees`, form);
      setShowAdd(false);
      setForm({ first_name: "", last_name: "", specialization: "" });
      fetchMechanics();
    } catch (err) { alert(err.response?.data?.detail || "Błąd"); }
  };

  const handleDelete = async (id) => {
    if (confirm("Usunąć mechanika?")) {
      try {
        await api.delete(`/employees/${id}`);
        fetchMechanics();
      } catch (err) { alert(err.response?.data?.detail || "Błąd"); }
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2>Mechanicy: {workshop.name}</h2>
          <button className="btn" onClick={onClose}><i className="fas fa-times"></i></button>
        </div>

        <button className="btn btn-primary" style={{ marginBottom: '20px' }} onClick={() => setShowAdd(!showAdd)}>
          {showAdd ? 'Anuluj' : 'Dodaj Mechanika'}
        </button>

        {showAdd && (
          <form onSubmit={handleSubmit} className="card glass" style={{ marginBottom: '20px', padding: '15px' }}>
            <div style={{ display: 'flex', gap: '10px' }}>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Imię</label>
                <input className="form-control" value={form.first_name} onChange={e => setForm({...form, first_name: e.target.value})} required />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Nazwisko</label>
                <input className="form-control" value={form.last_name} onChange={e => setForm({...form, last_name: e.target.value})} required />
              </div>
            </div>
            <div className="form-group">
              <label className="form-label">Specjalizacja</label>
              <input className="form-control" value={form.specialization} onChange={e => setForm({...form, specialization: e.target.value})} placeholder="np. Silniki, Skrzynie" />
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Zapisz</button>
          </form>
        )}

        <div style={{ marginBottom: '20px' }}>
          <label className="form-label">Wybierz usługę do przypisania:</label>
          <select className="form-control" value={selectedServiceId} onChange={e => setSelectedServiceId(e.target.value)}>
            <option value="">-- Wybierz usługę --</option>
            {allServices.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {mechanics.map(m => (
            <div key={m.id} className="card glass" style={{ display: 'flex', flexDirection: 'column', gap: '15px', padding: '20px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                  <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                    {m.first_name[0]}{m.last_name[0]}
                  </div>
                  <div>
                    <strong>{m.first_name} {m.last_name}</strong>
                    <div className="text-muted">{m.specialization || 'Mechanik'}</div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '10px' }}>
                  <button className="btn btn-outline" title="Przypisz usługę" onClick={() => handleAssignService(m.id)} disabled={!selectedServiceId}>
                    <i className="fas fa-link"></i>
                  </button>
                  <button className="btn" style={{ color: 'var(--danger)' }} onClick={() => handleDelete(m.id)}>
                    <i className="fas fa-trash"></i>
                  </button>
                </div>
              </div>
              
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '5px' }}>
                <span className="text-muted" style={{ fontSize: '0.8rem', width: '100%' }}>Przypisane usługi:</span>
                {m.services?.map(s => (
                  <span key={s.id} className="badge badge-info" style={{ fontSize: '0.7rem' }}>{s.name}</span>
                ))}
                {(!m.services || m.services.length === 0) && <span className="text-muted" style={{ fontSize: '0.7rem' }}>Brak</span>}
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};

export default ManageMechanicsModal;
