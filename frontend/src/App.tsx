import { BrowserRouter, Routes, Route } from "react-router-dom";
import "./App.css";

import HomePage from "./pages/home";
import LoginPage from "./pages/Login";
import SignupPage from "./pages/Signup";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
