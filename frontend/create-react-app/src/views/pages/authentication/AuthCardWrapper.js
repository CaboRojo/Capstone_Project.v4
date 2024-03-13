import PropTypes from 'prop-types';
import { Box } from '@mui/material';
import MainCard from 'ui-component/cards/MainCard';

// Assuming MainCard is your styled component. Adjust it if needed.
const AuthCardWrapper = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
      <MainCard
        sx={{
          maxWidth: { xs: 400, lg: 475 },
          margin: { xs: 2.5, md: 3 },
          '& > *': {
            flexGrow: 1,
            flexBasis: '50%'
          }
        }}
        content={false}
      >
        <Box sx={{ p: { xs: 2, sm: 3, xl: 5 } }}>{children}</Box>
      </MainCard>
    </Box>
  );
};

AuthCardWrapper.propTypes = {
  children: PropTypes.node.isRequired
};

export default AuthCardWrapper;
