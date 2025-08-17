/**
 * AI Provider Usage Analytics
 * Shows OpenAI, Claude, Gemini breakdown
 * Based on Phase 2.1.6 AI Analytics completion
 */
import React, { useState, useEffect } from 'react';
import { Card, Table, Tag, Statistic, Row, Col, Spin, Alert, Tooltip } from 'antd';
import { 
    PieChart, 
    Pie, 
    Cell, 
    ResponsiveContainer, 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    Tooltip as RechartsTooltip,
    LineChart,
    Line,
    Legend
} from 'recharts';
import { 
    RobotOutlined, 
    ThunderboltOutlined, 
    DollarOutlined, 
    BarChartOutlined,
    TrendingUpOutlined
} from '@ant-design/icons';

const ProviderBreakdown = ({ userId, timeRange = 30 }) => {
    const [providerData, setProviderData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchProviderData();
    }, [userId, timeRange]);

    const fetchProviderData = async () => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(
                `/api/ai/analytics/user/${userId}/provider-breakdown?days=${timeRange}`,
                {
                    headers: {
                        'Authorization': `Bearer ${localStorage.getItem('token')}`,
                        'Content-Type': 'application/json'
                    }
                }
            );
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            if (result.success) {
                setProviderData(result.data);
            } else {
                throw new Error(result.message || 'Failed to fetch provider data');
            }
        } catch (error) {
            console.error('Error fetching provider data:', error);
            setError(error.message);
            
            // Mock data for development/demo purposes
            setProviderData({
                provider_breakdown: [
                    {
                        provider: 'openai',
                        model: 'gpt-4',
                        interactions: 150,
                        tokens_used: 45000,
                        avg_tokens: 300,
                        cost: 23.50,
                        success_rate: 99.2
                    },
                    {
                        provider: 'claude',
                        model: 'claude-3-sonnet',
                        interactions: 89,
                        tokens_used: 28500,
                        avg_tokens: 320,
                        cost: 15.20,
                        success_rate: 98.8
                    },
                    {
                        provider: 'gemini',
                        model: 'gemini-pro',
                        interactions: 76,
                        tokens_used: 22100,
                        avg_tokens: 291,
                        cost: 8.90,
                        success_rate: 97.9
                    }
                ],
                summary: {
                    total_interactions: 315,
                    total_tokens_used: 95600,
                    avg_tokens_per_interaction: 303,
                    total_cost: 47.60,
                    period: `Last ${timeRange} days`
                }
            });
        } finally {
            setLoading(false);
        }
    };

    const getProviderColor = (provider) => {
        const colors = {
            'openai': '#00D4AA',
            'claude': '#FF6B35', 
            'gemini': '#4285F4'
        };
        return colors[provider.toLowerCase()] || '#8884d8';
    };

    const getProviderIcon = (provider) => {
        const icons = {
            'openai': '🤖',
            'claude': '🧠',
            'gemini': '💎'
        };
        return icons[provider.toLowerCase()] || '🔮';
    };

    const formatCurrency = (amount) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    };

    const formatNumber = (num) => {
        return new Intl.NumberFormat('en-US').format(num);
    };

    const columns = [
        {
            title: 'Provider',
            dataIndex: 'provider',
            key: 'provider',
            render: (provider) => (
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontSize: '16px' }}>{getProviderIcon(provider)}</span>
                    <Tag 
                        color={getProviderColor(provider)}
                        style={{ 
                            fontWeight: 'bold',
                            fontSize: '12px',
                            padding: '2px 8px'
                        }}
                    >
                        {provider.toUpperCase()}
                    </Tag>
                </div>
            )
        },
        {
            title: 'Model',
            dataIndex: 'model',
            key: 'model',
            render: (model) => (
                <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>
                    {model}
                </span>
            )
        },
        {
            title: 'Interactions',
            dataIndex: 'interactions',
            key: 'interactions',
            render: (interactions) => (
                <Statistic 
                    value={interactions} 
                    valueStyle={{ fontSize: '14px' }}
                />
            ),
            sorter: (a, b) => a.interactions - b.interactions,
            sortDirections: ['descend', 'ascend']
        },
        {
            title: 'Tokens Used',
            dataIndex: 'tokens_used',
            key: 'tokens_used',
            render: (tokens) => (
                <Tooltip title={`${formatNumber(tokens)} tokens`}>
                    <span style={{ fontSize: '13px', fontWeight: '500' }}>
                        {formatNumber(tokens)}
                    </span>
                </Tooltip>
            ),
            sorter: (a, b) => a.tokens_used - b.tokens_used,
            sortDirections: ['descend', 'ascend']
        },
        {
            title: 'Avg Tokens',
            dataIndex: 'avg_tokens',
            key: 'avg_tokens',
            render: (avg) => (
                <span style={{ fontSize: '13px' }}>
                    {Math.round(avg || 0)}
                </span>
            ),
            sorter: (a, b) => a.avg_tokens - b.avg_tokens
        },
        {
            title: 'Cost',
            dataIndex: 'cost',
            key: 'cost',
            render: (cost) => (
                <span style={{ 
                    fontSize: '13px', 
                    fontWeight: '600',
                    color: '#fa8c16'
                }}>
                    {formatCurrency(cost)}
                </span>
            ),
            sorter: (a, b) => a.cost - b.cost,
            sortDirections: ['descend', 'ascend']
        },
        {
            title: 'Success Rate',
            dataIndex: 'success_rate',
            key: 'success_rate',
            render: (rate) => (
                <Tag color={rate >= 99 ? 'green' : rate >= 98 ? 'orange' : 'red'}>
                    {rate}%
                </Tag>
            ),
            sorter: (a, b) => a.success_rate - b.success_rate,
            sortDirections: ['descend', 'ascend']
        }
    ];

    if (loading) {
        return (
            <Card 
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <RobotOutlined style={{ color: '#1890ff' }} />
                        AI Provider Analytics
                    </div>
                }
                className="provider-breakdown"
            >
                <div style={{ textAlign: 'center', padding: '60px 0' }}>
                    <Spin size="large" />
                    <p style={{ marginTop: 16, color: '#666' }}>
                        Loading provider analytics...
                    </p>
                </div>
            </Card>
        );
    }

    if (error) {
        return (
            <Card 
                title={
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <RobotOutlined style={{ color: '#ff4d4f' }} />
                        AI Provider Analytics
                    </div>
                }
                className="provider-breakdown"
            >
                <Alert
                    message="Error Loading Provider Data"
                    description={error}
                    type="error"
                    showIcon
                    action={
                        <button 
                            onClick={fetchProviderData} 
                            style={{ 
                                border: 'none', 
                                background: 'none', 
                                color: '#1890ff', 
                                cursor: 'pointer',
                                textDecoration: 'underline'
                            }}
                        >
                            Retry
                        </button>
                    }
                />
            </Card>
        );
    }

    const summary = providerData?.summary || {};
    const breakdown = providerData?.provider_breakdown || [];

    // Prepare chart data
    const pieData = breakdown.map(item => ({
        name: item.provider.toUpperCase(),
        value: item.interactions,
        color: getProviderColor(item.provider),
        percentage: ((item.interactions / summary.total_interactions) * 100).toFixed(1)
    }));

    const costData = breakdown.map(item => ({
        name: item.provider.toUpperCase(),
        cost: item.cost,
        interactions: item.interactions,
        efficiency: (item.cost / item.interactions).toFixed(3)
    }));

    return (
        <Card 
            title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <RobotOutlined style={{ color: '#1890ff' }} />
                    AI Provider Analytics
                </div>
            }
            className="provider-breakdown"
            extra={
                <div style={{ fontSize: '12px', color: '#666' }}>
                    {summary.period}
                </div>
            }
            style={{ height: '100%' }}
        >
            {/* Summary Statistics */}
            <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
                <Col span={6}>
                    <div style={{ textAlign: 'center' }}>
                        <Statistic
                            title="Total Interactions"
                            value={summary.total_interactions || 0}
                            prefix={<ThunderboltOutlined style={{ color: '#1890ff' }} />}
                            valueStyle={{ color: '#1890ff', fontSize: '1.2rem' }}
                        />
                    </div>
                </Col>
                <Col span={6}>
                    <div style={{ textAlign: 'center' }}>
                        <Statistic
                            title="Total Tokens"
                            value={summary.total_tokens_used || 0}
                            formatter={(value) => formatNumber(value)}
                            prefix={<BarChartOutlined style={{ color: '#52c41a' }} />}
                            valueStyle={{ color: '#52c41a', fontSize: '1.2rem' }}
                        />
                    </div>
                </Col>
                <Col span={6}>
                    <div style={{ textAlign: 'center' }}>
                        <Statistic
                            title="Avg Tokens/Chat"
                            value={Math.round(summary.avg_tokens_per_interaction || 0)}
                            prefix={<TrendingUpOutlined style={{ color: '#faad14' }} />}
                            valueStyle={{ color: '#faad14', fontSize: '1.2rem' }}
                        />
                    </div>
                </Col>
                <Col span={6}>
                    <div style={{ textAlign: 'center' }}>
                        <Statistic
                            title="Total Cost"
                            value={summary.total_cost || 0}
                            formatter={(value) => formatCurrency(value)}
                            prefix={<DollarOutlined style={{ color: '#fa8c16' }} />}
                            valueStyle={{ color: '#fa8c16', fontSize: '1.2rem' }}
                        />
                    </div>
                </Col>
            </Row>

            {/* Charts Section */}
            <Row gutter={[24, 24]} style={{ marginBottom: 24 }}>
                <Col span={12}>
                    <div style={{ height: 280 }}>
                        <h4 style={{ textAlign: 'center', marginBottom: 16 }}>
                            🥧 Usage Distribution
                        </h4>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={80}
                                    dataKey="value"
                                    label={({ name, percentage }) => `${name}\n${percentage}%`}
                                    labelLine={false}
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <RechartsTooltip 
                                    formatter={(value, name) => [
                                        `${value} interactions (${((value / summary.total_interactions) * 100).toFixed(1)}%)`,
                                        name
                                    ]}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </Col>
                
                <Col span={12}>
                    <div style={{ height: 280 }}>
                        <h4 style={{ textAlign: 'center', marginBottom: 16 }}>
                            💰 Cost Efficiency Analysis
                        </h4>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={costData}>
                                <XAxis 
                                    dataKey="name" 
                                    tick={{ fontSize: 12 }}
                                />
                                <YAxis 
                                    tick={{ fontSize: 12 }}
                                />
                                <RechartsTooltip 
                                    formatter={(value, name) => [
                                        name === 'cost' ? formatCurrency(value) : value,
                                        name === 'cost' ? 'Total Cost' : 'Cost per Interaction'
                                    ]}
                                />
                                <Bar 
                                    dataKey="cost" 
                                    fill="#fa8c16"
                                    radius={[4, 4, 0, 0]}
                                />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Col>
            </Row>

            {/* Detailed Table */}
            <div style={{ marginTop: 24 }}>
                <h4 style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 8,
                    marginBottom: 16 
                }}>
                    📊 Detailed Provider Breakdown
                </h4>
                <Table
                    columns={columns}
                    dataSource={breakdown}
                    rowKey={(record) => `${record.provider}-${record.model}`}
                    pagination={false}
                    size="small"
                    scroll={{ x: 800 }}
                    style={{ 
                        backgroundColor: '#fafafa',
                        borderRadius: '8px',
                        padding: '16px'
                    }}
                />
            </div>

            {/* Performance Insights */}
            <div style={{ 
                marginTop: 24,
                padding: '16px',
                backgroundColor: '#f6ffed',
                borderRadius: '8px',
                border: '1px solid #b7eb8f'
            }}>
                <div style={{ 
                    fontSize: '14px', 
                    fontWeight: '600', 
                    marginBottom: 8,
                    color: '#389e0d',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6
                }}>
                    💡 Provider Performance Insights
                </div>
                <div style={{ fontSize: '13px', color: '#666', lineHeight: '1.6' }}>
                    {breakdown.length > 0 && (
                        <>
                            <div>
                                🏆 <strong>Most Used:</strong> {breakdown.sort((a, b) => b.interactions - a.interactions)[0]?.provider.toUpperCase()} 
                                ({breakdown.sort((a, b) => b.interactions - a.interactions)[0]?.interactions} interactions)
                            </div>
                            <div style={{ marginTop: 4 }}>
                                💸 <strong>Most Cost-Effective:</strong> {breakdown.sort((a, b) => (a.cost/a.interactions) - (b.cost/b.interactions))[0]?.provider.toUpperCase()}
                                ({formatCurrency(breakdown.sort((a, b) => (a.cost/a.interactions) - (b.cost/b.interactions))[0]?.cost / breakdown.sort((a, b) => (a.cost/a.interactions) - (b.cost/b.interactions))[0]?.interactions)} per interaction)
                            </div>
                            <div style={{ marginTop: 4 }}>
                                🎯 <strong>Highest Success Rate:</strong> {breakdown.sort((a, b) => b.success_rate - a.success_rate)[0]?.provider.toUpperCase()}
                                ({breakdown.sort((a, b) => b.success_rate - a.success_rate)[0]?.success_rate}% success rate)
                            </div>
                        </>
                    )}
                </div>
            </div>
        </Card>
    );
};

export default ProviderBreakdown;