// Sample JavaScript code for testing

import React, { useState, useEffect } from 'react';
import axios from 'axios';

class DataService {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async fetchData(endpoint) {
        try {
            const response = await axios.get(`${this.baseUrl}${endpoint}`);
            return response.data;
        } catch (error) {
            console.error('Error fetching data:', error);
            throw error;
        }
    }
}

const useDataHook = (endpoint) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const service = new DataService('https://api.example.com');
        
        service.fetchData(endpoint)
            .then(data => {
                setData(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err);
                setLoading(false);
            });
    }, [endpoint]);
    
    return { data, loading, error };
};

export function DataComponent({ endpoint }) {
    const { data, loading, error } = useDataHook(endpoint);
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    
    return (
        <div>
            <h1>Data</h1>
            <pre>{JSON.stringify(data, null, 2)}</pre>
        </div>
    );
}

export default DataComponent;
