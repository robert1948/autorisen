import { BrowserRouter, Route, Routes } from "react-router-dom";

import Home from "./pages/Home";
import Register from "./pages/Register";
import OnboardingCustomer from "./pages/onboarding/Customer";
import OnboardingDeveloper from "./pages/onboarding/Developer";

const App = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/register" element={<Register />} />
      <Route path="/onboarding/customer" element={<OnboardingCustomer />} />
      <Route path="/onboarding/developer" element={<OnboardingDeveloper />} />
    </Routes>
  </BrowserRouter>
);

export default App;
