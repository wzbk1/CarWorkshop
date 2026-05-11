import { useState, useEffect } from "react";
import api from "../api";

const ManageHoursModal = ({ workshopId, onClose }) => {
  const [tab, setTab] = useState("standard"); 
  const [hours, setHours] = useState([]);
  const [exceptions, setExceptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  
  const [excDate, setExcDate] = useState("");
  const [excReason, setExcReason] = useState("");

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  useEffect(() => {
    fetchInitialData();
  }, [workshopId]);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [hRes, eRes] = await Promise.all([
        api.get(`/business-hours/locations/${workshopId}/business-hours`),
        api.get(`/location-exceptions/locations/${workshopId}/exceptions`)
      ]);
      let hoursData = hRes.data;
      
      
      if (hoursData.length === 0) {
        for (let i = 0; i < 7; i++) {
          await api.post(`/business-hours/locations/${workshopId}/business-hours`, {
            day_of_week: i,
            open_time: "08:00",
            close_time: "18:00",
            is_closed: i === 6
          });
        }
        const refreshed = await api.get(`/business-hours/locations/${workshopId}/business-hours`);
        hoursData = refreshed.data;
      }
      
      setHours(hoursData);
      setExceptions(eRes.data);
    } catch (err) {
      console.error("Błąd pobierania godzin:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleClosed = (dayIdx) => {
    setHours(prev => prev.map(h => 
      h.day_of_week === dayIdx ? { ...h, is_closed: !h.is_closed } : h
    ));
  };

  const handleChangeTime = (dayIdx, field, value) => {
    setHours(prev => prev.map(h => 
      h.day_of_week === dayIdx ? { ...h, [field]: value } : h
    ));
  };

  const handleSaveStandard = async () => {
    setSaving(true);
    try {
      for (const h of hours) {
        await api.put(`/business-hours/${h.id}`, {
          open_time: h.open_time,
          close_time: h.close_time,
          is_closed: h.is_closed
        });
      }
      alert("Standardowe godziny zapisane pomyślnie.");
    } catch (err) {
      alert("Błąd zapisu godzin");
    } finally {
      setSaving(false);
    }
  };

  const handleAddException = async (e) => {
    e.preventDefault();
    if (!excDate) return;
    try {
      await api.post(`/location-exceptions/locations/${workshopId}/exceptions`, {
        exception_date: excDate,
        is_closed: true,
        reason: excReason || "Dzień wolny"
      });
      setExcDate("");
      setExcReason("");
      const res = await api.get(`/location-exceptions/locations/${workshopId}/exceptions`);
      setExceptions(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || "Błąd dodawania dnia wolnego");
    }
  };

  const handleDeleteException = async (id) => {
    try {
      await api.delete(`/location-exceptions/${id}`);
      const res = await api.get(`/location-exceptions/locations/${workshopId}/exceptions`);
      setExceptions(res.data);
    } catch (err) {
      alert("Błąd usuwania wyjątku");
    }
  };

  if (loading) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content glass" style={{ maxWidth: '600px' }}>
        <div className="modal-header" style={{ marginBottom: '15px' }}>
          <h2>Zarządzaj godzinami pracy</h2>
        </div>

        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
          <button className={`btn ${tab === 'standard' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setTab('standard')} style={{ flex: 1 }}>
            Standardowy tydzień
          </button>
          <button className={`btn ${tab === 'exceptions' ? 'btn-primary' : 'btn-outline'}`} onClick={() => setTab('exceptions')} style={{ flex: 1 }}>
            Wyjątki / Dni wolne
          </button>
        </div>

        {tab === 'standard' && (
          <>
            <div className="hours-list" style={{ marginBottom: '25px' }}>
              {days.map((day, index) => {
                const h = hours.find(item => item.day_of_week === index) || { open_time: '08:00', close_time: '18:00', is_closed: false };
                const dayNamesPl = {
                  'Monday': 'Poniedziałek', 'Tuesday': 'Wtorek', 'Wednesday': 'Środa',
                  'Thursday': 'Czwartek', 'Friday': 'Piątek', 'Saturday': 'Sobota', 'Sunday': 'Niedziela'
                };
                
                return (
                  <div key={day} className="form-group" style={{ 
                    display: 'grid', 
                    gridTemplateColumns: '120px 1fr 1fr 100px', 
                    gap: '15px', 
                    alignItems: 'center',
                    padding: '12px',
                    borderBottom: '1px solid var(--border)'
                  }}>
                    <span style={{ fontWeight: 600 }}>{dayNamesPl[day]}</span>
                    <input 
                      type="time" 
                      className="form-control"
                      value={h.open_time?.substring(0, 5) || "08:00"}
                      onChange={(e) => handleChangeTime(index, 'open_time', e.target.value)}
                      disabled={h.is_closed}
                    />
                    <input 
                      type="time" 
                      className="form-control"
                      value={h.close_time?.substring(0, 5) || "18:00"}
                      onChange={(e) => handleChangeTime(index, 'close_time', e.target.value)}
                      disabled={h.is_closed}
                    />
                    <button 
                      className={`btn ${h.is_closed ? 'btn-primary' : 'btn-outline'}`}
                      onClick={() => handleToggleClosed(index)}
                      style={{ fontSize: '0.8rem', padding: '6px' }}
                    >
                      {h.is_closed ? 'Zamknięte' : 'Otwarte'}
                    </button>
                  </div>
                );
              })}
            </div>

            <div className="modal-actions" style={{ display: 'flex', gap: '15px', justifyContent: 'flex-end' }}>
              <button className="btn btn-outline" onClick={onClose} disabled={saving}>Zamknij</button>
              <button className="btn btn-primary" onClick={handleSaveStandard} disabled={saving}>
                {saving ? 'Zapisywanie...' : 'Zapisz zmiany tygodnia'}
              </button>
            </div>
          </>
        )}

        {tab === 'exceptions' && (
          <>
            <form className="card glass" onSubmit={handleAddException} style={{ padding: '15px', marginBottom: '20px' }}>
              <h4 style={{ margin: '0 0 10px 0' }}>Dodaj dzień wolny</h4>
              <div style={{ display: 'flex', gap: '10px' }}>
                <input 
                  type="date" 
                  className="form-control" 
                  value={excDate}
                  onChange={(e) => setExcDate(e.target.value)}
                  required
                />
                <input 
                  type="text" 
                  className="form-control" 
                  placeholder="Powód (np. Święto, Urlop)"
                  value={excReason}
                  onChange={(e) => setExcReason(e.target.value)}
                  style={{ flex: 1 }}
                />
                <button type="submit" className="btn btn-primary">Dodaj</button>
              </div>
            </form>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '300px', overflowY: 'auto' }}>
              {exceptions.map(exc => (
                <div key={exc.id} className="card glass" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 15px' }}>
                  <div>
                    <strong style={{ color: 'var(--danger)' }}>{exc.exception_date}</strong> (Zamknięte)
                    <div className="text-muted" style={{ fontSize: '0.9rem' }}>{exc.reason || 'Brak powodu'}</div>
                  </div>
                  <button className="btn" style={{ color: 'var(--text-secondary)' }} onClick={() => handleDeleteException(exc.id)}>
                    <i className="fas fa-trash-alt"></i>
                  </button>
                </div>
              ))}
              {exceptions.length === 0 && (
                <p className="text-center text-muted" style={{ padding: '20px' }}>Brak dodanych wyjątków (warsztat działa normalnie w każdy dzień).</p>
              )}
            </div>

            <div className="modal-actions" style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
              <button className="btn btn-outline" onClick={onClose}>Zamknij</button>
            </div>
          </>
        )}

      </div>
    </div>
  );
};

export default ManageHoursModal;
