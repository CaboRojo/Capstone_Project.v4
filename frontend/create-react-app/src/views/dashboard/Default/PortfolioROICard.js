import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';
import { useTheme, styled } from '@mui/material/styles';
import { Avatar, Box, Grid, Typography } from '@mui/material';
import axios from 'axios';

const CardWrapper = styled(Box)(({ theme }) => ({
    backgroundColor: theme.palette.primary.dark,
    color: '#fff',
    overflow: 'hidden',
    position: 'relative',
    '&>div': {
        position: 'relative',
        zIndex: 5
    },
    '&:after': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: theme.palette.primary[800],
        borderRadius: '50%',
        zIndex: 1,
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
        zIndex: 1,
        width: 210,
        height: 210,
        background: theme.palette.primary[800],
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

const PortfolioROICard = ({ isLoading }) => {
    const theme = useTheme();
    const [roi, setRoi] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchROI = async () => {
            const userId = localStorage.getItem('userId');
            const token = localStorage.getItem('token');

            if (!token || !userId) {
                setError('Token or User ID not found');
                return;
            }

            try {
                const response = await axios.get(`/api/portfolio/${userId}/roi`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (response.data && response.status === 200) {
                    setRoi(response.data.roi);
                } else {
                    throw new Error('Failed to fetch ROI data');
                }
            } catch (error) {
                setError(error.response?.data?.message || "An unexpected error occurred");
            }
        };

        if (!isLoading) {
            fetchROI();
        }
    }, [isLoading]);

    return (
        <CardWrapper>
            <Box sx={{ p: 2.25 }}>
                <Grid container direction="column">
                    <Grid item>
                        <Avatar
                            variant="rounded"
                            sx={{
                                ...theme.typography.commonAvatar,
                                ...theme.typography.largeAvatar,
                                backgroundColor: theme.palette.primary[800],
                                color: '#fff',
                                mt: 1
                            }}
                        >
                            {/* Icon placement if needed */}
                        </Avatar>
                    </Grid>
                    <Grid item sx={{ mb: 0.75 }}>
                        {error ? (
                            <Typography color="error">{error}</Typography>
                        ) : (
                            <Typography sx={{ fontSize: '2.125rem', fontWeight: 500, mt: 1.75, mb: 0.75 }}>
                                {isLoading ? "Loading..." : `ROI: ${roi?.toFixed(2) || 'N/A'}%`}
                            </Typography>
                        )}
                    </Grid>
                </Grid>
            </Box>
        </CardWrapper>
    );
};

PortfolioROICard.propTypes = {
    isLoading: PropTypes.bool
};

export default PortfolioROICard;
