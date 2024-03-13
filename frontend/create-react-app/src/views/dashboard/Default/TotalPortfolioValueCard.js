import PropTypes from 'prop-types';
import React, { useState, useEffect } from 'react';
import { Avatar, Box, Grid, Typography } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';
import MainCard from 'ui-component/cards/MainCard';
import SkeletonEarningCard from 'ui-component/cards/Skeleton/EarningCard';
import axios from 'axios'; // Ensure axios is installed for API requests

const CardWrapper = styled(MainCard)(({ theme }) => ({
    backgroundColor: theme.palette.secondary.dark,
    color: '#fff',
    overflow: 'hidden',
    position: 'relative',
    '&:after': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: theme.palette.secondary[800],
        borderRadius: '50%',
        top: -85,
        right: -95,
        [theme.breakpoints.down('sm')]: {
            top: -105,
            right: -140
        }
    },
    '&:before': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: theme.palette.secondary[800],
        borderRadius: '50%',
        top: -125,
        right: -15,
        opacity: 0.5,
        [theme.breakpoints.down('sm')]: {
            top: -155,
            right: -70
        }
    }
}));



const TotalPortfolioValueCard = ({ token, userId }) => {
    const theme = useTheme();
    const [totalPortfolioValue, setTotalPortfolioValue] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
  
    useEffect(() => {
      const fetchTotalPortfolioValue = async () => {
        setLoading(true);
        setError(null);
  
        try {
          if (!token || !userId) {
            setError('Token or user ID not found');
            return;
          }
  
          const response = await axios.get(`/api/portfolio/${userId}`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          const data = response.data;
          setTotalPortfolioValue(data.total_portfolio_value);
        } catch (error) {
          console.error("Error fetching total portfolio value:", error);
          setError('Error fetching total portfolio value');
        } finally {
          setLoading(false);
        }
      };
  
      fetchTotalPortfolioValue();
    }, []);

    if (loading) {
        return <SkeletonEarningCard />;
    }

    if(error) {
        return <Typography variant="h6" color="error">{error}</Typography>;
    }
    return (
        <CardWrapper border={false} content={false}>
            <Box sx={{ p: 2.25 }}>
                <Grid container direction="column">
                    <Grid item>
                        <Grid container justifyContent="space-between">
                            <Grid item>
                                <Avatar
                                    variant="rounded"
                                    sx={{
                                        ...theme.typography.commonAvatar,
                                        ...theme.typography.largeAvatar,
                        backgroundColor: theme.palette.secondary[800],
                        mt: 1
                    }}
                                >
                                    {/* Icon */}
                                </Avatar>
                            </Grid>
                        </Grid>
                    </Grid>
                    <Grid item>
                        <Typography sx={{ fontSize: '2.125rem', fontWeight: 500, mt: 1.75, mb: 0.75 }}>
                            ${totalPortfolioValue.toLocaleString()}
                        </Typography>
                    </Grid>
                    <Grid item>
                        <Typography
                            sx={{
                                fontSize: '1rem',
                                fontWeight: 500,
                                color: theme.palette.secondary[200]
                            }}
                        >
                            Total Portfolio Value
                        </Typography>
                    </Grid>
                </Grid>
            </Box>
        </CardWrapper>
    );

};

TotalPortfolioValueCard.propTypes = {
    token: PropTypes.string,
    userId: PropTypes.string,
  };

export default TotalPortfolioValueCard;