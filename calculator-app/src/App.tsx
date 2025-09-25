import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary';
import Calculator from './components/Calculator/Calculator';
import './App.css';

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Calculator</h1>
        <p>A modern calculator built with React and TypeScript</p>
      </header>
      
      <main className="app-main">
        <ErrorBoundary>
          <Calculator />
        </ErrorBoundary>
      </main>
      
      <footer className="app-footer">
        <p>Use keyboard or click buttons. Press Escape to clear.</p>
      </footer>
    </div>
  );
}

export default App
