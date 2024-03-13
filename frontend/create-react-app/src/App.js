import React from 'react';
import { ThemeProvider, StyledEngineProvider, CssBaseline } from '@mui/material';
import { theme as getTheme } from './themes'; // Ensure this import path is correct
import MainRoutes from './routes/MainRoutes'; // Ensure this path matches your file structure

// Assuming customization is needed; if not, this could be an empty object or tailored to your needs
const customization = {}; // Define any customization options here
const theme = getTheme(customization); // Generate the theme using your dynamic setup

const App = () => {
  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}> {/* Apply the generated theme */}
        <CssBaseline />
        <MainRoutes />
      </ThemeProvider>
    </StyledEngineProvider>
  );
};

export default App;
