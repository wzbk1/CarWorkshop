import React, { useState, useEffect } from 'react';
import api from '../api';

const CarsModal = ({ onClose, onAdded }) => {
  const [brands, setBrands] = useState([]);
  const [myCars, setMyCars] = useState([]);
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ brand_id: "", model: "", vin: "", year: new Date().getFullYear(), color: "" });

  useEffect(() => {
    fetchBrands();
    fetchMyCars();
  }, []);

  const fetchBrands = async () => {
    try {
      const res = await api.get("/car-brands");
      setBrands(res.data);
    } catch (err) { console.error(err); }
  };

  const fetchMyCars = async () => {
    try {
      const res = await api.get("/cars/me");
      setMyCars(res.data);
    } catch (err) { console.error(err); }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.brand_id) return alert("Wybierz markę!");
    try {
      await api.post("/cars/", {
        ...form,
        brand_id: parseInt(form.brand_id),
        vin: form.vin || null,
        year: parseInt(form.year)
      });
      setShowAdd(false);
      setForm({ brand_id: "", model: "", vin: "", year: new Date().getFullYear(), color: "" });
      fetchMyCars();
      if (onAdded) onAdded();
    } catch (err) { alert(err.response?.data?.detail || "Błąd"); }
  };

  const handleDelete = async (id) => {
    if (confirm("Usunąć ten samochód?")) {
      try {
        await api.delete(`/cars/${id}`);
        fetchMyCars();
        if (onAdded) onAdded();
      } catch (err) { alert(err.response?.data?.detail || "Błąd"); }
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content glass" onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '20px' }}>
          <h2>Moje Samochody</h2>
          <button className="btn" onClick={onClose}><i className="fas fa-times"></i></button>
        </div>

        <button className="btn btn-primary" style={{ marginBottom: '20px', width: '100%' }} onClick={() => setShowAdd(!showAdd)}>
          {showAdd ? 'Anuluj' : 'Dodaj Nowy Samochód'}
        </button>

        {showAdd && (
          <form onSubmit={handleSubmit} className="card glass" style={{ marginBottom: '20px', padding: '20px' }}>
            <div className="form-group">
              <label className="form-label">Marka</label>
              <select className="form-control" value={form.brand_id} onChange={e => setForm({...form, brand_id: e.target.value})} required>
                <option value="">Wybierz markę...</option>
                {brands.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Model</label>
              <input className="form-control" value={form.model} onChange={e => setForm({...form, model: e.target.value})} placeholder="np. Golf, A4" required />
            </div>
            <div className="form-group">
              <label className="form-label">VIN (opcjonalnie, 17 znaków)</label>
              <input className="form-control" value={form.vin} onChange={e => setForm({...form, vin: e.target.value})} placeholder="Wpisz 17 znaków" maxLength={17} />
            </div>
            <div style={{ display: 'flex', gap: '10px' }}>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Rok</label>
                <input className="form-control" type="number" value={form.year} onChange={e => setForm({...form, year: e.target.value})} />
              </div>
              <div className="form-group" style={{ flex: 1 }}>
                <label className="form-label">Kolor</label>
                <input className="form-control" value={form.color} onChange={e => setForm({...form, color: e.target.value})} />
              </div>
            </div>
            <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Zapisz Samochód</button>
          </form>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '15px' }}>
          {myCars.length > 0 ? myCars.map(car => (
            <div key={car.id} className="card glass" style={{ position: 'relative', overflow: 'hidden', padding: '0' }}>
              <div style={{ padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '10px' }}>
                  <div style={{ width: '45px', height: '45px', background: 'linear-gradient(135deg, var(--primary), #00c6ff)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '1.2rem', boxShadow: '0 4px 10px rgba(0,122,255,0.3)' }}>
                    <i className="fas fa-car-side"></i>
                  </div>
                  <div>
                    <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: '700' }}>{car.brand_name} {car.model}</h3>
                    <span className="badge badge-blue" style={{ fontSize: '0.7rem', marginTop: '4px', display: 'inline-block' }}>Rocznik {car.year}</span>
                  </div>
                </div>
                
                <div style={{ background: 'var(--border)', height: '1px', margin: '15px 0' }}></div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  <div>
                    <i className="fas fa-palette me-1"></i> Kolor: <span style={{ color: 'var(--text)', fontWeight: '500' }}>{car.color || 'Brak'}</span>
                  </div>
                  <div>
                    <i className="fas fa-barcode me-1"></i> VIN: <span style={{ color: 'var(--text)', fontWeight: '500' }}>{car.vin?.substring(0,8) || 'Brak'}...</span>
                  </div>
                </div>
              </div>
              
              <button 
                className="btn" 
                style={{ position: 'absolute', top: '15px', right: '15px', color: 'var(--text-secondary)', padding: '5px' }} 
                onClick={() => handleDelete(car.id)}
                title="Usuń samochód"
                onMouseEnter={(e) => e.currentTarget.style.color = 'var(--danger)'}
                onMouseLeave={(e) => e.currentTarget.style.color = 'var(--text-secondary)'}
              >
                <i className="fas fa-trash-alt"></i>
              </button>
            </div>
          )) : !showAdd && (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px 20px', background: 'rgba(255,255,255,0.02)', borderRadius: '15px', border: '1px dashed var(--border)' }}>
              <i className="fas fa-car" style={{ fontSize: '3rem', color: 'var(--text-secondary)', opacity: 0.5, marginBottom: '15px' }}></i>
              <h3 style={{ color: 'var(--text-secondary)' }}>Brak samochodów w garażu</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Dodaj swój pierwszy samochód, aby móc umawiać wizyty.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CarsModal;
