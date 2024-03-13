import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import axios from 'axios';
import { useTheme, styled } from '@mui/material/styles';
import { Avatar, Box, Grid, Typography, CircularProgress } from '@mui/material';
import MainCard from 'ui-component/cards/MainCard'; // Adjust import path as necessary
import LocalMallOutlinedIcon from '@mui/icons-material/LocalMallOutlined';

const CardWrapper = styled(MainCard)(({ theme }) => ({
    backgroundColor: theme.palette.primary.dark,
    color: '#fff',
    overflow: 'hidden',
    position: 'relative',
    '&>div': {
        position: 'relative',
        zIndex: 5,
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
            right: -140,
        },
    },
    '&:before': {
        content: '""',
        position: 'absolute',
        width: 210,
        height: 210,
        background: theme.palette.primary[800],
        borderRadius: '50%',
        top: -125,
        right: -15,
        opacity: 0.5,
        [theme.breakpoints.down('sm')]: {
            top: -155,
            right: -70,
        },
    },
}));

const IndividualROICard = ({ symbol, userId }) => {
    const theme = useTheme();
    const [roi, setRoi] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchROI = async () => {
            setIsLoading(true);
            try {
                const response = await axios.get(`/api/user/${userId}/portfolio/stock/${encodeURIComponent(symbol)}/roi`);
                if (response.status === 200 && response.data.roi !== undefined) {
                    setRoi(response.data.roi);
                    setError('');
                } else {
                    setError('Failed to fetch ROI');
                }
            } catch (error) {
                setError('Failed to fetch ROI');
            } finally {
                setIsLoading(false);
            }
        };

        fetchROI();
    }, [symbol, userId]);

    return (
        <CardWrapper border={false} content={false}>
            <Box sx={{ p: 2.25 }}>
                <Grid container direction="column">
                    <Grid item>
                        <Avatar variant="rounded" sx={{
                            ...theme.typography.commonAvatar,
                            ...theme.typography.largeAvatar,
                            backgroundColor: theme.palette.primary[800],
                            color: '#fff',
                            mt: 1,
                        }}>
                            <LocalMallOutlinedIcon fontSize="inherit" />
                        </Avatar>
                    </Grid>
                    <Grid item sx={{ mb: 0.75 }}>
                        {isLoading ? (
                            <CircularProgress color="inherit" />
                        ) : error ? (
                            <Typography color="error">{error}</Typography>
                        ) : (
                            <Typography sx={{ fontSize: '2.125rem', fontWeight: 500, mt: 1.75, mb: 0.75 }}>
                                ROI: {`${roi.toFixed(2)}%`}
                            </Typography>
                        )}
                    </Grid>
                </Grid>
            </Box>
        </CardWrapper>
    );
};

IndividualROICard.propTypes = {
    symbol: PropTypes.string.isRequired,
    userId: PropTypes.string.isRequired,
};

export default IndividualROICard;
