import React, { useState, useEffect } from 'react';
import api from '../api';

const AdminDashboard = ({ 
  locations, 
  onAddLocation, 
  onUpdateLocation, 
  onDeleteLocation,
  onManageMechanics,
  onManageServices,
  onManageHours
}) => {
  const [showModal, setShowModal] = useState(false);
  const [editingLoc, setEditingLoc] = useState(null);
  const [form, setForm] = useState({ name: "", address: "", city: "", description: "" });
  const [allBrands, setAllBrands] = useState([]);
  const [selectedBrandIds, setSelectedBrandIds] = useState([]);

  useEffect(() => {
    api.get("/car-brands/?active_only=true")
      .then(res => setAllBrands(res.data))
      .catch(err => console.error("Błąd pobierania marek:", err));
  }, []);

  const handleEdit = async (loc) => {
    setEditingLoc(loc);
    setForm({ name: loc.name, address: loc.address, city: loc.city || "", description: loc.description || "" });
    try {
      const res = await api.get(`/car-brands/locations/${loc.id}/brands`);
      setSelectedBrandIds(res.data.map(b => b.id));
    } catch (err) {
      setSelectedBrandIds([]);
    }
    setShowModal(true);
  };

  const handleAdd = () => {
    setEditingLoc(null);
    setForm({ name: "", address: "", city: "", description: "" });
    setSelectedBrandIds([]);
    setShowModal(true);
  };

  const toggleBrand = (brandId) => {
    setSelectedBrandIds(prev =>
      prev.includes(brandId)
        ? prev.filter(id => id !== brandId)
        : [...prev, brandId]
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const data = { ...form, serviced_brand_ids: selectedBrandIds };
    if (editingLoc) {
      onUpdateLocation(editingLoc.id, data);
    } else {
      onAddLocation(data);
    }
    setShowModal(false);
    setEditingLoc(null);
    setForm({ name: "", address: "", city: "", description: "" });
    setSelectedBrandIds([]);
  };

  return (
    <div className="container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' }}>
        <h1>Panel Administratora</h1>
        <button className="btn btn-primary" onClick={handleAdd}>
          <i className="fas fa-plus me-1"></i> Dodaj Warsztat
        </button>
      </div>

      <div className="card glass">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Nazwa</th>
              <th>Adres</th>
              <th>Zarządzanie</th>
              <th>Akcje</th>
            </tr>
          </thead>
          <tbody>
            {locations.map(loc => (
              <tr key={loc.id}>
                <td><strong>{loc.name}</strong></td>
                <td>{loc.address}</td>
                <td>
                  <div style={{ display: 'flex', gap: '5px' }}>
                    <button className="btn btn-outline" style={{ padding: '5px 10px', fontSize: '0.8rem' }} onClick={() => onManageMechanics(loc)}>Mechanicy</button>
                    <button className="btn btn-outline" style={{ padding: '5px 10px', fontSize: '0.8rem' }} onClick={() => onManageServices(loc)}>Usługi</button>
                    <button className="btn btn-outline" style={{ padding: '5px 10px', fontSize: '0.8rem' }} onClick={() => onManageHours(loc)}>Godziny</button>
                  </div>
                </td>
                <td>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button className="btn" style={{ color: 'var(--primary)' }} onClick={() => handleEdit(loc)}><i className="fas fa-edit"></i></button>
                    <button className="btn" style={{ color: 'var(--danger)' }} onClick={() => onDeleteLocation(loc.id)}><i className="fas fa-trash"></i></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content glass" onClick={e => e.stopPropagation()}>
            <h2>{editingLoc ? 'Edytuj Warsztat' : 'Dodaj Nowy Warsztat'}</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label className="form-label">Nazwa</label>
                <input className="form-control" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
              </div>
              <div className="form-group">
                <label className="form-label">Adres</label>
                <input className="form-control" value={form.address} onChange={e => setForm({...form, address: e.target.value})} required />
              </div>
              <div className="form-group">
                <label className="form-label">Miasto</label>
                <input className="form-control" value={form.city} onChange={e => setForm({...form, city: e.target.value})} required />
              </div>
              <div className="form-group">
                <label className="form-label">Opis</label>
                <textarea className="form-control" value={form.description} onChange={e => setForm({...form, description: e.target.value})} rows="3" />
              </div>

              <div className="form-group">
                <label className="form-label">Obsługiwane marki</label>
                <div style={{
                  display: 'flex',
                  flexWrap: 'wrap',
                  gap: '8px',
                  maxHeight: '200px',
                  overflowY: 'auto',
                  padding: '12px',
                  background: 'rgba(255,255,255,0.03)',
                  borderRadius: '12px',
                  border: '1px solid var(--border)'
                }}>
                  {allBrands.length === 0 && (
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Brak dostępnych marek</span>
                  )}
                  {allBrands.map(brand => {
                    const isSelected = selectedBrandIds.includes(brand.id);
                    return (
                      <button
                        key={brand.id}
                        type="button"
                        onClick={() => toggleBrand(brand.id)}
                        style={{
                          padding: '6px 14px',
                          borderRadius: '20px',
                          fontSize: '0.8rem',
                          fontWeight: 600,
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          border: isSelected ? '1px solid var(--primary)' : '1px solid var(--border)',
                          background: isSelected ? 'rgba(0, 122, 255, 0.2)' : 'rgba(255,255,255,0.05)',
                          color: isSelected ? '#00c6ff' : 'var(--text-secondary)',
                        }}
                      >
                        {isSelected ? '✓ ' : ''}{brand.name}
                      </button>
                    );
                  })}
                </div>
                {selectedBrandIds.length > 0 && (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '6px', display: 'block' }}>
                    Wybrano: {selectedBrandIds.length} {selectedBrandIds.length === 1 ? 'markę' : 'marek'}
                  </span>
                )}
              </div>

              <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Zapisz</button>
                <button type="button" className="btn btn-outline" style={{ flex: 1 }} onClick={() => setShowModal(false)}>Anuluj</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
