import React, { useState } from 'react';
import api from '../api';

const Auth = ({ onLogin }) => {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ email: "", password: "", first_name: "", last_name: "" });
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccessMsg("");
    setLoading(true);
    
    try {
      if (mode === 'login') {
        const res = await api.post("/auth/login", {
          email: form.email,
          password: form.password
        });
        onLogin(res.data.access_token);
      } else {
        await api.post("/auth/register", {
          email: form.email,
          password: form.password,
          first_name: form.first_name,
          last_name: form.last_name
        });
        setMode('login');
        setSuccessMsg("Konto utworzone pomyślnie. Możesz się zalogować.");
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Wystąpił błąd podczas autoryzacji");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
      <div className="card glass" style={{ width: '100%', maxWidth: '400px', padding: '40px' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '30px' }}>{mode === 'login' ? 'Witaj ponownie!' : 'Utwórz konto'}</h2>
        
        {error && <div style={{ color: 'var(--error)', marginBottom: '15px', textAlign: 'center', fontWeight: '500' }}>{error}</div>}
        {successMsg && <div style={{ color: 'var(--success)', marginBottom: '15px', textAlign: 'center', fontWeight: '500' }}>{successMsg}</div>}

        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
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
          )}
          
          <div className="form-group">
            <label className="form-label">E-mail</label>
            <input className="form-control" type="email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
          </div>
          
          <div className="form-group">
            <label className="form-label">Hasło</label>
            <input className="form-control" type="password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} required />
          </div>

          <button className="btn btn-primary" style={{ width: '100%', padding: '12px', marginTop: '10px' }} disabled={loading}>
            {loading ? 'Ładowanie...' : (mode === 'login' ? 'Zaloguj się' : 'Zarejestruj się')}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.9rem' }}>
          {mode === 'login' ? 'Nie masz konta?' : 'Masz już konto?'} {' '}
          <a href="#" style={{ color: 'var(--primary)', fontWeight: 700 }} onClick={(e) => { e.preventDefault(); setMode(mode === 'login' ? 'register' : 'login'); setError(''); setSuccessMsg(''); }}>
            {mode === 'login' ? 'Zarejestruj się' : 'Zaloguj się'}
          </a>
        </p>
      </div>
    </div>
  );
};

export default Auth;
