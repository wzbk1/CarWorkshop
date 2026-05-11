import React from 'react';

const Navbar = ({ isLoggedIn, isAdmin, onLogout, setView, onShowCars, me, theme, onToggleTheme }) => {
  return (
    <nav className="navbar glass">
      <div className="container navbar-content">
        <a href="#" className="navbar-brand" onClick={() => setView('locations')}>
          <div className="logo-icon">
            <i className="fas fa-car-side"></i>
          </div>
          <span className="logo-text">Car<span className="text-primary">Workshop</span></span>
        </a>
        
        <div className="nav-links">
          <button className="btn btn-outline" onClick={() => setView('locations')}>
            <i className="fas fa-search me-1"></i> Warsztaty
          </button>
          
          {isLoggedIn ? (
            <>
              <button className="btn btn-outline" onClick={() => setView('my-bookings')}>
                <i className="fas fa-calendar-check me-1"></i> Rezerwacje
              </button>
              <button className="btn btn-outline" onClick={onShowCars}>
                <i className="fas fa-car me-1"></i> Moje Auta
              </button>
              {isAdmin && (
                <button className="btn btn-primary" onClick={() => setView('admin-dashboard')}>
                  <i className="fas fa-user-shield me-1"></i> Admin
                </button>
              )}
              <div className="user-info">
                <div className="user-avatar">{me?.first_name?.[0]}{me?.last_name?.[0]}</div>
                <button className="btn btn-outline btn-logout" onClick={onLogout}>
                  <i className="fas fa-sign-out-alt"></i>
                </button>
              </div>
            </>
          ) : (
            <button className="btn btn-primary" onClick={() => setView('auth')}>
              Zaloguj się
            </button>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
