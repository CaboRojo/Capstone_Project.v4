import PropTypes from 'prop-types';
import { forwardRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useTheme } from '@mui/material/styles';
import { Avatar, Chip, ListItemButton, ListItemIcon, ListItemText, Typography, useMediaQuery } from '@mui/material';

// Project imports
import { MENU_OPEN, SET_MENU } from 'store/actions';

// Assets
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';

const NavItem = forwardRef(({ item, level }, ref) => {
  const theme = useTheme();
  const dispatch = useDispatch();
  const customization = useSelector((state) => state.customization);
  const matchesSM = useMediaQuery(theme.breakpoints.down('lg'));

  const isActive = customization.isOpen.findIndex((id) => id === item?.id) > -1;

  const handleClick = () => {
    if (item.url) {
      dispatch({ type: MENU_OPEN, id: item?.id });
      if (matchesSM) dispatch({ type: SET_MENU, opened: false });
    }
  };

  useEffect(() => {
    // Your code using props, state, or dispatch here
    // This code will run only once after the initial render
  }, []);

  return (
    <ListItemButton
      ref={ref}
      component={item.url ? Link : 'button'}
      to={item.url}
      target={item?.target}
      onClick={handleClick}
      selected={isActive}
      sx={{
        borderRadius: `${customization.borderRadius}px`,
        mb: 0.5,
        alignItems: 'flex-start',
        backgroundColor: level > 1 ? 'transparent !important' : 'inherit',
        py: level > 1 ? 1 : 1.25,
        pl: `${level * 24}px`
      }}
    >
      <ListItemIcon sx={{ my: 'auto', minWidth: 36 }}>
        <FiberManualRecordIcon
          sx={{
            width: customization.isOpen.findIndex((id) => id === item?.id) > -1 ? 8 : 6,
            height: customization.isOpen.findIndex((id) => id === item?.id) > -1 ? 8 : 6
          }}
          fontSize={level > 0 ? 'inherit' : 'medium'}
        />
      </ListItemIcon>
      <ListItemText
        primary={
          <Typography variant={isActive ? 'h5' : 'body1'} color="inherit">
            {item?.title}
          </Typography>
        }
        secondary={
          item?.caption && (
            <Typography variant="caption" sx={{ ...theme.typography.subMenuCaption }} display="block" gutterBottom>
              {item.caption}
            </Typography>
          )
        }
      />
      {item?.chip && (
        <Chip
          color={item.chip.color}
          variant={item.chip.variant}
          size={item.chip.size}
          label={item.chip.label}
          avatar={item.chip.avatar && <Avatar>{item.chip.avatar}</Avatar>}
        />
      )}
    </ListItemButton>
  );
});

NavItem.propTypes = {
  item: PropTypes.shape({
    id: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    url: PropTypes.string,
    target: PropTypes.string,
    disabled: PropTypes.bool,
    caption: PropTypes.string,
    chip: PropTypes.shape({
      color: PropTypes.oneOf([
        'default',
        'inherit',
        'primary',
        'secondary',
        'error',
        'info',
        'success',
        'warning'
      ]),
      variant: PropTypes.oneOf(['default', 'outlined', 'soft']),
      size: PropTypes.oneOf(['small', 'medium', 'large']),
      label: PropTypes.node,
      avatar: PropTypes.node
    })
  }),
  level: PropTypes.number.isRequired
};

NavItem.defaultProps = {
  item: {
    id: '',
    title: '',
    url: '',
    target: '_self',
    disabled: false,
    caption: '',
    chip: {
      color: 'default',
      variant: 'default',
      size: 'medium',
      label: '',
      avatar: null
    }
  }
};

export default NavItem;