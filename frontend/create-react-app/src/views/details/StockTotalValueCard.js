import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { Avatar, Box, Grid, Typography, CircularProgress } from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';
import MainCard from 'ui-component/cards/MainCard';
import axios from 'axios';

const CardWrapper = styled(MainCard)(({ theme }) => ({
    backgroundColor: theme.palette.secondary.dark,
    color: '#fff',
    overflow: 'hidden',
    position: 'relative',
}));

const StockTotalValueCard = ({ symbol, userId }) => {
    const theme = useTheme();
    const [details, setDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchDetails = async () => {
            setIsLoading(true);
            try {
                const response = await axios.get(`/api/user/${userId}/portfolio/stock/${encodeURIComponent(symbol)}/details`);
                if (response.status === 200) {
                    setDetails(response.data);
                } else {
                    setError('Failed to fetch stock details');
                }
            } catch (error) {
                console.error('Error fetching stock details:', error);
                setError('Error fetching stock details');
            } finally {
                setIsLoading(false);
            }
        };

        fetchDetails();
    }, [symbol, userId]);

    return (
        <>
            {isLoading ? (
                <CircularProgress color="inherit" />
            ) : error ? (
                <Typography color="error">{error}</Typography>
            ) : (
                <CardWrapper border={false} content={false}>
                    <Box sx={{ p: 2.25 }}>
                        <Grid container direction="column">
                            <Grid item>
                                <Avatar
                                    variant="rounded"
                                    sx={{
                                        ...theme.typography.commonAvatar,
                                        ...theme.typography.largeAvatar,
                                        backgroundColor: theme.palette.secondary[800],
                                        mt: 1,
                                    }}
                                >
                                    {/* Use a relevant icon or image */}
                                </Avatar>
                            </Grid>
                            <Grid item>
                                <Typography sx={{ fontSize: '2.125rem', fontWeight: 500, mt: 1.75, mb: 0.75 }}>
                                    {`${symbol}: ${details.quantity} shares`}
                                </Typography>
                                <Typography sx={{ fontSize: '1.5rem', fontWeight: 500 }}>
                                    Current Value: ${details.totalValue.toLocaleString()}
                                </Typography>
                            </Grid>
                        </Grid>
                    </Box>
                </CardWrapper>
            )}
        </>
    );
};

StockTotalValueCard.propTypes = {
    symbol: PropTypes.string.isRequired,
    userId: PropTypes.string.isRequired,
};

export default StockTotalValueCard;

