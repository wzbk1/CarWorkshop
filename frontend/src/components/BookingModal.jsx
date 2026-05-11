import { useState, useEffect } from "react";
import api from "../api";

const BookingModal = ({ workshopId, onClose, onAddCar }) => {
  const [services, setServices] = useState([]);
  const [cars, setCars] = useState([]);
  const [mechanics, setMechanics] = useState([]);
  const [selectedService, setSelectedService] = useState("");
  const [selectedCar, setSelectedCar] = useState("");
  const [selectedMechanic, setSelectedMechanic] = useState("");
  const [date, setDate] = useState("");
  const [slots, setSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    fetchInitialData();
  }, [workshopId]);

  const fetchInitialData = async () => {
    try {
      const [sRes, cRes] = await Promise.all([
        api.get(`/services/locations/${workshopId}/services`),
        api.get("/cars/me")
      ]);
      setServices(sRes.data);
      setCars(cRes.data);
    } catch (err) {
      console.error("Błąd pobierania danych:", err);
    }
  };

  useEffect(() => {
    if (selectedService) {
      api.get(`/employees/services/${selectedService}/employees`)
        .then(res => setMechanics(res.data));
    }
  }, [selectedService]);

  useEffect(() => {
    if (selectedService && date) {
      setErrorMsg("");
      api.get(`/bookings/available-slots/${selectedService}?appointment_date=${date}`)
        .then(res => {
          const allSlots = res.data.available_slots || [];
          if (selectedMechanic) {
            const filteredSlots = allSlots
              .filter(slot => slot.available_employees.some(emp => emp.employee_id.toString() === selectedMechanic.toString()))
              .map(slot => slot.time);
            setSlots(filteredSlots);
            if (filteredSlots.length === 0) setErrorMsg("Brak wolnych terminów u tego mechanika w wybranym dniu.");
          } else {
            setSlots([]);
          }
        })
        .catch(err => {
          console.error(err);
          setSlots([]);
          setErrorMsg(err.response?.data?.detail || "Błąd pobierania terminów");
        });
    } else {
      setSlots([]);
      setErrorMsg("");
    }
  }, [selectedService, selectedMechanic, date]);

  const handleBooking = async () => {
    setLoading(true);
    try {
      await api.post("/bookings/", {
        car_id: selectedCar ? parseInt(selectedCar) : null,
        service_id: parseInt(selectedService),
        employee_id: parseInt(selectedMechanic),
        appointment_date: date,
        appointment_time: selectedSlot
      });
      alert("Rezerwacja zakończona sukcesem!");
      onClose();
    } catch (err) {
      alert(err.response?.data?.detail || "Błąd rezerwacji");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content glass">
        <div className="modal-header">
          <h2>Umów wizytę</h2>
        </div>

        <div className="form-group">
          <label className="form-label">Wybierz usługę</label>
          <select 
            className="form-control" 
            value={selectedService} 
            onChange={(e) => setSelectedService(e.target.value)}
          >
            <option value="">-- Wybierz --</option>
            {services.map(s => <option key={s.id} value={s.id}>{s.name} - {s.price} PLN</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Twój samochód</label>
          <div style={{ display: 'flex', gap: '10px' }}>
            <select 
              className="form-control" 
              value={selectedCar} 
              onChange={(e) => setSelectedCar(e.target.value)}
              style={{ flex: 1 }}
            >
              <option value="">-- Wybierz --</option>
              {cars.map(c => <option key={c.id} value={c.id}>{c.brand_name} {c.model} ({c.vin?.substring(0,6)})</option>)}
            </select>
            <button className="btn btn-outline" onClick={onAddCar}>+ Dodaj</button>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Mechanik</label>
          <select 
            className="form-control" 
            value={selectedMechanic} 
            onChange={(e) => setSelectedMechanic(e.target.value)}
            disabled={!selectedService}
          >
            <option value="">-- Wybierz --</option>
            {mechanics.map(m => <option key={m.id} value={m.id}>{m.first_name} {m.last_name}</option>)}
          </select>
        </div>

        <div className="form-group">
          <label className="form-label">Data</label>
          <input 
            type="date" 
            className="form-control" 
            value={date} 
            min={new Date().toISOString().split("T")[0]}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>

        {errorMsg && (
          <div className="alert alert-error" style={{ marginBottom: '15px', color: 'var(--danger)', fontWeight: 'bold' }}>
            {errorMsg}
          </div>
        )}

        {slots.length > 0 && !errorMsg && (
          <div className="form-group">
            <label className="form-label">Dostępne godziny</label>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '10px' }}>
              {slots.map(s => (
                <button 
                  key={s} 
                  className={`btn ${selectedSlot === s ? 'btn-primary' : 'btn-outline'}`}
                  onClick={() => setSelectedSlot(s)}
                  style={{ padding: '8px' }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="modal-actions" style={{ display: 'flex', gap: '15px', justifyContent: 'flex-end', marginTop: '30px' }}>
          <button className="btn btn-outline" onClick={onClose}>Anuluj</button>
          <button 
            className="btn btn-primary" 
            onClick={handleBooking} 
            disabled={!selectedSlot || loading}
          >
            {loading ? 'Rezerwowanie...' : 'Zarezerwuj teraz'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default BookingModal;
