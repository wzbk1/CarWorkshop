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
          <button className="nav-item" onClick={() => setView('locations')}>
            <i className="fas fa-search"></i> <span>Warsztaty</span>
          </button>
          
          {isLoggedIn ? (
            <>
              <button className="nav-item" onClick={() => setView('my-bookings')}>
                <i className="fas fa-calendar-check"></i> <span>Rezerwacje</span>
              </button>
              <button className="nav-item" onClick={onShowCars}>
                <i className="fas fa-car"></i> <span>Auta</span>
              </button>
              {isAdmin && (
                <button className="nav-item" onClick={() => setView('admin-dashboard')}>
                  <i className="fas fa-user-shield"></i> <span>Admin</span>
                </button>
              )}
              <button className="nav-item btn-logout" onClick={onLogout}>
                <i className="fas fa-sign-out-alt"></i> <span>Wyloguj</span>
              </button>
            </>
          ) : (
            <button className="nav-item btn-primary-nav" onClick={() => setView('auth')}>
              <i className="fas fa-sign-in-alt"></i> <span>Logowanie</span>
            </button>
          )}
        </div>

      </div>
    </nav>
  );
};

export default Navbar;
