// MenuList/index.js
import React from 'react';
import List from '@mui/material/List';
import NavItem from './NavItem';
import Typography from '@mui/material/Typography';

// Add imports for your icons
import DashboardIcon from '@mui/icons-material/Dashboard';
// ... other icons

const MenuList = () => {
  return (
    <List>
      <Typography variant="h6" sx={{ px: 2, py: 1 }}>Portfolio</Typography>
      <NavItem
        level={1}
        title="Portfolio Overview"
        href="/dashboard/default"
        icon={<DashboardIcon />}
      />
      {/* Remove NavItem for Asset Details */}
      {/* Other NavItems as needed */}
    </List>
  );
};

export default MenuList;
