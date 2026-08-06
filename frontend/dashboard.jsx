import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';

const Dashboard = () => {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await axios.get('/api/evaluation');
                setData(response.data);
            } catch (err) {
                setError('Error fetching data');
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>{error}</div>;

    const chartData = {
        labels: data.map(item => item.query),
        datasets: [
            {
                label: 'Relevance Score',
                data: data.map(item => item.relevanceScore),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
            },
            {
                label: 'Accuracy Score',
                data: data.map(item => item.accuracyScore),
                backgroundColor: 'rgba(153, 102, 255, 0.6)',
            },
        ],
    };

    return (
        <div>
            <h2>Evaluation Dashboard</h2>
            <Bar data={chartData} options={{ responsive: true }} />
        </div>
    );
};

export default Dashboard;