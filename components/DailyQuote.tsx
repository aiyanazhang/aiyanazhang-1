import React, { useState, useEffect, useRef, useCallback } from 'react';

interface Quote {
  text: string;
  author: string;
}

const quotes: Quote[] = [
  { text: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
  { text: "In the middle of difficulty lies opportunity.", author: "Albert Einstein" },
  { text: "What you seek is seeking you.", author: "Rumi" },
  { text: "The best time to plant a tree was 20 years ago. The second best time is now.", author: "Chinese Proverb" },
  { text: "Be yourself; everyone else is already taken.", author: "Oscar Wilde" },
  { text: "The only impossible journey is the one you never begin.", author: "Tony Robbins" },
  { text: "What lies behind us and what lies before us are tiny matters compared to what lies within us.", author: "Ralph Waldo Emerson" },
  { text: "The future belongs to those who believe in the beauty of their dreams.", author: "Eleanor Roosevelt" },
  { text: "It is during our darkest moments that we must focus to see the light.", author: "Aristotle" },
  { text: "The mind is everything. What you think you become.", author: "Buddha" },
  { text: "Simplicity is the ultimate sophistication.", author: "Leonardo da Vinci" },
  { text: "The journey of a thousand miles begins with one step.", author: "Lao Tzu" },
  { text: "Not all those who wander are lost.", author: "J.R.R. Tolkien" },
  { text: "Everything you can imagine is real.", author: "Pablo Picasso" },
  { text: "Turn your wounds into wisdom.", author: "Oprah Winfrey" },
  { text: "The secret of getting ahead is getting started.", author: "Mark Twain" },
  { text: "Life is what happens when you're busy making other plans.", author: "John Lennon" },
  { text: "You must be the change you wish to see in the world.", author: "Mahatma Gandhi" },
  { text: "Happiness is not something ready made. It comes from your own actions.", author: "Dalai Lama" },
  { text: "Stay hungry, stay foolish.", author: "Steve Jobs" },
];

type Theme = 'midnight' | 'ocean' | 'sunset' | 'forest' | 'rose' | 'dawn';

const themes: Record<Theme, { bg1: string; bg2: string; accent: string; text: string }> = {
  midnight: { bg1: '#0f0c29', bg2: '#302b63', accent: '#a855f7', text: '#ffffff' },
  ocean: { bg1: '#0f2027', bg2: '#2c5364', accent: '#38bdf8', text: '#ffffff' },
  sunset: { bg1: '#ee9ca7', bg2: '#ffdde1', accent: '#be185d', text: '#1a1a2e' },
  forest: { bg1: '#134e5e', bg2: '#71b280', accent: '#fbbf24', text: '#ffffff' },
  rose: { bg1: '#360033', bg2: '#0b8793', accent: '#f472b6', text: '#ffffff' },
  dawn: { bg1: '#2c3e50', bg2: '#fd746c', accent: '#fef08a', text: '#ffffff' },
};

const STORAGE_KEY = 'dailyQuoteFavorites';
const THEME_KEY = 'dailyQuoteTheme';

export default function DailyQuote() {
  const [currentQuote, setCurrentQuote] = useState<Quote>(quotes[0]);
  const [favorites, setFavorites] = useState<Quote[]>([]);
  const [theme, setTheme] = useState<Theme>('midnight');
  const [showPanel, setShowPanel] = useState(false);
  const [toast, setToast] = useState('');
  const [animKey, setAnimKey] = useState(0);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const touchStartX = useRef(0);

  useEffect(() => {
    const savedFavorites = localStorage.getItem(STORAGE_KEY);
    if (savedFavorites) setFavorites(JSON.parse(savedFavorites));
    
    const savedTheme = localStorage.getItem(THEME_KEY) as Theme;
    if (savedTheme && themes[savedTheme]) setTheme(savedTheme);
    
    getRandomQuote();
  }, []);

  const getRandomQuote = useCallback(() => {
    const newQuote = quotes[Math.floor(Math.random() * quotes.length)];
    setCurrentQuote(newQuote);
    setAnimKey(k => k + 1);
  }, []);

  const showToast = (message: string) => {
    setToast(message);
    setTimeout(() => setToast(''), 2000);
  };

  const toggleFavorite = () => {
    const exists = favorites.some(f => f.text === currentQuote.text);
    let newFavorites: Quote[];
    
    if (exists) {
      newFavorites = favorites.filter(f => f.text !== currentQuote.text);
      showToast('Removed from favorites');
    } else {
      newFavorites = [currentQuote, ...favorites];
      showToast('Added to favorites');
    }
    
    setFavorites(newFavorites);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newFavorites));
  };

  const changeTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    localStorage.setItem(THEME_KEY, newTheme);
  };

  const isFavorited = favorites.some(f => f.text === currentQuote.text);
  const colors = themes[theme];

  const shareQuote = async () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = 1080;
    canvas.height = 1080;

    const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
    gradient.addColorStop(0, colors.bg1);
    gradient.addColorStop(1, colors.bg2);
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = colors.text;
    ctx.globalAlpha = 0.1;
    ctx.font = 'italic 300px Georgia';
    ctx.fillText('"', 80, 280);
    ctx.globalAlpha = 1;

    ctx.font = 'italic 48px Georgia';
    ctx.fillStyle = colors.text;

    const words = currentQuote.text.split(' ');
    const lines: string[] = [];
    let currentLine = '';
    const maxWidth = 900;

    words.forEach(word => {
      const testLine = currentLine + word + ' ';
      const metrics = ctx.measureText(testLine);
      if (metrics.width > maxWidth && currentLine) {
        lines.push(currentLine.trim());
        currentLine = word + ' ';
      } else {
        currentLine = testLine;
      }
    });
    lines.push(currentLine.trim());

    const lineHeight = 70;
    const startY = (canvas.height - lines.length * lineHeight) / 2;

    lines.forEach((line, i) => {
      ctx.fillText(line, 90, startY + i * lineHeight);
    });

    ctx.font = '28px Arial';
    ctx.globalAlpha = 0.7;
    ctx.fillText('— ' + currentQuote.author, 90, startY + lines.length * lineHeight + 60);

    ctx.globalAlpha = 0.4;
    ctx.font = '20px Arial';
    ctx.fillText('DAILY SPARK', 90, canvas.height - 60);

    try {
      const blob = await new Promise<Blob | null>(resolve => canvas.toBlob(resolve, 'image/png'));
      if (blob && navigator.share) {
        const file = new File([blob], 'quote.png', { type: 'image/png' });
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({ files: [file], title: 'Daily Spark' });
          return;
        }
      }
      const link = document.createElement('a');
      link.download = 'daily-spark-quote.png';
      link.href = canvas.toDataURL('image/png');
      link.click();
      showToast('Image downloaded');
    } catch {
      if (navigator.clipboard) {
        navigator.clipboard.writeText(`"${currentQuote.text}" - ${currentQuote.author}`);
        showToast('Quote copied to clipboard');
      }
    }
  };

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.code === 'Space' && e.target === document.body) {
      e.preventDefault();
      getRandomQuote();
    }
  }, [getRandomQuote]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div
      style={{
        minHeight: '100vh',
        background: `linear-gradient(135deg, ${colors.bg1} 0%, ${colors.bg2} 100%)`,
        color: colors.text,
        fontFamily: "'Inter', system-ui, sans-serif",
        padding: 20,
        transition: 'background 0.8s ease',
      }}
      onTouchStart={e => (touchStartX.current = e.touches[0].clientX)}
      onTouchEnd={e => {
        const diff = touchStartX.current - e.changedTouches[0].clientX;
        if (Math.abs(diff) > 50) getRandomQuote();
      }}
    >
      <div style={{ maxWidth: 900, margin: '0 auto' }}>
        {/* Header */}
        <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px 0' }}>
          <span style={{ fontSize: '0.9rem', letterSpacing: 3, opacity: 0.7, fontWeight: 300 }}>DAILY SPARK</span>
          <div style={{ display: 'flex', gap: 10 }}>
            <button onClick={() => setShowPanel(true)} style={iconBtnStyle(colors.text)}>&#9829;</button>
            <button onClick={() => setShowPanel(true)} style={iconBtnStyle(colors.text)}>&#9681;</button>
          </div>
        </header>

        {/* Quote Card */}
        <section style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', textAlign: 'center' }}>
          <div style={{ maxWidth: 700, padding: '60px 40px', position: 'relative' }}>
            <span style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: '8rem', position: 'absolute', top: -20, left: 0, opacity: 0.1, lineHeight: 1, color: colors.accent }}>"</span>
            <p key={animKey} style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontSize: 'clamp(1.8rem, 5vw, 2.8rem)', fontWeight: 400, lineHeight: 1.5, marginBottom: 30, fontStyle: 'italic', animation: 'fadeUp 0.6s ease' }}>
              {currentQuote.text}
            </p>
            <p style={{ fontSize: '1rem', letterSpacing: 2, opacity: 0.7, fontWeight: 300 }}>— {currentQuote.author}</p>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 20, marginTop: 50, flexWrap: 'wrap', justifyContent: 'center' }}>
            <button onClick={toggleFavorite} style={{ ...secondaryBtnStyle(colors.text), ...(isFavorited ? { background: 'rgba(233,69,96,0.2)', borderColor: colors.accent, color: colors.accent } : {}) }}>
              {isFavorited ? '♥' : '♡'} Save
            </button>
            <button onClick={getRandomQuote} style={primaryBtnStyle(colors.accent)}>New Quote</button>
            <button onClick={shareQuote} style={secondaryBtnStyle(colors.text)}>↗ Share</button>
          </div>

          <p style={{ textAlign: 'center', opacity: 0.4, fontSize: '0.8rem', marginTop: 30, letterSpacing: 1 }}>Swipe or press Space for new quote</p>
        </section>
      </div>

      {/* Panel Overlay */}
      {showPanel && <div onClick={() => setShowPanel(false)} style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 50 }} />}

      {/* Side Panel */}
      <div style={{ position: 'fixed', top: 0, right: showPanel ? 0 : -300, width: 280, height: '100vh', background: 'rgba(0,0,0,0.95)', padding: 30, transition: 'right 0.3s', zIndex: 100, overflowY: 'auto', color: '#fff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 30 }}>
          <span style={{ fontSize: '0.9rem', letterSpacing: 2, opacity: 0.7 }}>THEMES</span>
          <button onClick={() => setShowPanel(false)} style={{ background: 'none', border: 'none', color: 'white', fontSize: '1.5rem', cursor: 'pointer' }}>&times;</button>
        </div>
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 15 }}>
          {(Object.keys(themes) as Theme[]).map(t => (
            <div key={t} onClick={() => changeTheme(t)} style={{ height: 80, borderRadius: 12, cursor: 'pointer', border: theme === t ? '2px solid white' : '2px solid transparent', background: `linear-gradient(135deg, ${themes[t].bg1}, ${themes[t].bg2})`, position: 'relative', transition: 'transform 0.3s' }}>
              <span style={{ position: 'absolute', bottom: 8, left: 10, fontSize: '0.7rem', letterSpacing: 1, textShadow: '0 1px 3px rgba(0,0,0,0.5)' }}>{t.charAt(0).toUpperCase() + t.slice(1)}</span>
            </div>
          ))}
        </div>

        <div style={{ marginTop: 40, borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: 20 }}>
          <div style={{ fontSize: '0.9rem', letterSpacing: 2, opacity: 0.7, marginBottom: 15 }}>SAVED QUOTES</div>
          {favorites.length === 0 ? (
            <div style={{ textAlign: 'center', opacity: 0.5, padding: 30, fontSize: '0.85rem' }}>No saved quotes yet</div>
          ) : (
            favorites.map((q, i) => (
              <div key={i} onClick={() => { setCurrentQuote(q); setAnimKey(k => k + 1); setShowPanel(false); }} style={{ padding: 15, background: 'rgba(255,255,255,0.05)', borderRadius: 10, marginBottom: 10, cursor: 'pointer' }}>
                <div style={{ fontFamily: "'Cormorant Garamond', Georgia, serif", fontStyle: 'italic', fontSize: '0.95rem', lineHeight: 1.4, marginBottom: 8 }}>
                  "{q.text.substring(0, 60)}{q.text.length > 60 ? '...' : ''}"
                </div>
                <div style={{ fontSize: '0.75rem', opacity: 0.6 }}>- {q.author}</div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Toast */}
      {toast && (
        <div style={{ position: 'fixed', bottom: 30, left: '50%', transform: 'translateX(-50%)', background: 'rgba(0,0,0,0.9)', color: 'white', padding: '15px 30px', borderRadius: 50, zIndex: 200 }}>{toast}</div>
      )}

      <canvas ref={canvasRef} style={{ display: 'none' }} />

      <style>{`
        @keyframes fadeUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}

const iconBtnStyle = (color: string): React.CSSProperties => ({
  width: 44,
  height: 44,
  borderRadius: '50%',
  border: '1px solid rgba(255,255,255,0.2)',
  background: 'rgba(255,255,255,0.05)',
  color,
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: '1.2rem',
});

const primaryBtnStyle = (accent: string): React.CSSProperties => ({
  padding: '16px 32px',
  borderRadius: 50,
  border: 'none',
  fontSize: '0.95rem',
  cursor: 'pointer',
  background: accent,
  color: 'white',
  fontWeight: 500,
});

const secondaryBtnStyle = (color: string): React.CSSProperties => ({
  padding: '16px 32px',
  borderRadius: 50,
  border: '1px solid rgba(255,255,255,0.2)',
  fontSize: '0.95rem',
  cursor: 'pointer',
  background: 'rgba(255,255,255,0.1)',
  color,
});
