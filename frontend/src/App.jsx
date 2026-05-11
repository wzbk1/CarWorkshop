import { useEffect, useState } from "react";
import api from "./api";
import "./styles/index.css";
import Navbar from "./components/Navbar";
import Alert from "./components/Alert";
import WorkshopCard from "./components/WorkshopCard";
import BookingModal from "./components/BookingModal";
import MyBookings from "./components/MyBookings";
import CarsModal from "./components/CarsModal";
import Auth from "./components/Auth";
import ManageServicesModal from "./components/ManageServicesModal";
import ManageMechanicsModal from "./components/ManageMechanicsModal";
import ManageHoursModal from "./components/ManageHoursModal";
import AdminDashboard from "./components/AdminDashboard";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [me, setMe] = useState(null);
  const [view, setView] = useState("locations");
  const [alert, setAlert] = useState({ message: "", type: "success" });
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "dark");

  const [locations, setLocations] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [myCars, setMyCars] = useState([]);
  
  
  const [showCars, setShowCars] = useState(false);
  const [manageServicesLoc, setManageServicesLoc] = useState(null);
  const [manageMechanicsLoc, setManageMechanicsLoc] = useState(null);
  const [manageHoursLoc, setManageHoursLoc] = useState(null);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  useEffect(() => {
    if (token) {
      fetchMe();
      fetchLocations();
      fetchMyCars();
    }
  }, [token]);

  const fetchMe = async () => {
    try {
      const res = await api.get("/auth/me");
      setMe(res.data);
    } catch (err) {
      handleLogout();
    }
  };

  const fetchLocations = async () => {
    try {
      const res = await api.get("/locations/");
      setLocations(res.data);
    } catch (err) {
      setAlert({ message: "Błąd pobierania warsztatów", type: "error" });
    }
  };

  const fetchMyCars = async () => {
    try {
      const res = await api.get("/cars/me");
      setMyCars(res.data);
    } catch (err) {
      console.error("Błąd pobierania aut");
    }
  };

  const handleLogin = (newToken) => {
    localStorage.setItem("token", newToken);
    setToken(newToken);
    setView("locations");
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken("");
    setMe(null);
    setView("locations");
  };

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  if (!token) {
    return (
      <div className="auth-page">
        <Auth onLogin={handleLogin} />
        <button className="theme-toggle-fab" onClick={toggleTheme}>
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
      </div>
    );
  }

  return (
    <div className="app-layout">
      <Navbar 
        isLoggedIn={!!token} 
        isAdmin={me?.role === 'ADMIN'}
        me={me}
        setView={setView}
        onLogout={handleLogout}
        onShowCars={() => setShowCars(true)}
      />

      <Alert 
        message={alert.message} 
        type={alert.type} 
        onClose={() => setAlert({ message: "", type: "success" })} 
      />

      <main className="container">
        {view === 'locations' && (
          <div className="workshop-grid">
            {locations.map(loc => (
              <WorkshopCard 
                key={loc.id} 
                workshop={loc} 
                isAdmin={me?.role === 'ADMIN'}
                onBook={() => setSelectedLocation(loc)}
                onManageServices={() => setManageServicesLoc(loc)}
                onManageMechanics={() => setManageMechanicsLoc(loc)}
                onManageHours={() => setManageHoursLoc(loc)}
              />
            ))}
          </div>
        )}

        {view === 'my-bookings' && <MyBookings isAdmin={me?.role === 'ADMIN'} />}

        {view === 'admin-dashboard' && me?.role === 'ADMIN' && (
          <AdminDashboard 
            locations={locations}
            onManageServices={setManageServicesLoc}
            onManageMechanics={setManageMechanicsLoc}
            onManageHours={setManageHoursLoc}
            onAddLocation={async (data) => {
              try {
                const res = await api.post("/locations/", data);
                const newId = res.data.id;
                
                for (let i = 0; i < 7; i++) {
                  await api.post(`/business-hours/locations/${newId}/business-hours`, {
                    day_of_week: i,
                    open_time: "08:00",
                    close_time: "18:00",
                    is_closed: i === 6
                  });
                }
                fetchLocations();
              } catch (e) { alert(e.response?.data?.detail || "Błąd dodawania warsztatu"); }
            }}
            onUpdateLocation={async (id, data) => {
              try {
                await api.put(`/locations/${id}`, data);
                fetchLocations();
              } catch (e) { alert("Błąd edycji warsztatu"); }
            }}
            onDeleteLocation={async (id) => {
              if (confirm("Na pewno usunąć?")) {
                try {
                  await api.delete(`/locations/${id}`);
                  fetchLocations();
                } catch (e) { alert("Błąd usuwania warsztatu"); }
              }
            }}
          />
        )}
      </main>

      <button className="theme-toggle-fab" onClick={toggleTheme}>
        {theme === 'dark' ? '☀️' : '🌙'}
      </button>

      {}
      {selectedLocation && (
        <BookingModal 
          workshopId={selectedLocation.id}
          onClose={() => setSelectedLocation(null)}
          onAddCar={() => setShowCars(true)}
        />
      )}

      {showCars && (
        <CarsModal onClose={() => setShowCars(false)} />
      )}

      {manageServicesLoc && (
        <ManageServicesModal workshop={manageServicesLoc} onClose={() => setManageServicesLoc(null)} />
      )}

      {manageMechanicsLoc && (
        <ManageMechanicsModal workshop={manageMechanicsLoc} onClose={() => setManageMechanicsLoc(null)} />
      )}

      {manageHoursLoc && (
        <ManageHoursModal workshopId={manageHoursLoc.id} onClose={() => setManageHoursLoc(null)} />
      )}

      <footer className="footer glass">
        <p>© 2026 CarWorkshop Premium Service</p>
      </footer>
    </div>
  );
}