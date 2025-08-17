/**
 * Quality Score Analytics Card
 * Displays 5-dimensional AI quality metrics
 * Based on Phase 2.1.6 AI Analytics completion
 */
import React, { useState, useEffect } from 'react';
import { Card, Progress, Statistic, Row, Col, Spin, Alert } from 'antd';
import { TrophyOutlined, BarChartOutlined } from '@ant-design/icons';

const QualityScoreCard = ({ userId, timeRange = 30 }) => {
    const [qualityData, setQualityData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchQualityScores();
    }, [userId, timeRange]);

    const fetchQualityScores = async () => {
        setLoading(true);
        setError(null);
        
        try {
            const response = await fetch(
                `/api/ai/analytics/user/${userId}/quality-scores?days=${timeRange}`,
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
                setQualityData(result.data);
            } else {
                throw new Error(result.message || 'Failed to fetch quality scores');
            }
        } catch (error) {
            console.error('Error fetching quality scores:', error);
            setError(error.message);
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score) => {
        if (score >= 0.9) return '#52c41a'; // Excellent - Green
        if (score >= 0.8) return '#1890ff'; // Good - Blue
        if (score >= 0.7) return '#faad14'; // Fair - Orange
        if (score >= 0.6) return '#fa8c16'; // Poor - Dark Orange
        return '#f5222d'; // Very Poor - Red
    };

    const getScoreLabel = (score) => {
        if (score >= 0.9) return 'Excellent';
        if (score >= 0.8) return 'Good';
        if (score >= 0.7) return 'Fair';
        if (score >= 0.6) return 'Poor';
        return 'Needs Improvement';
    };

    const formatScore = (score) => {
        return (score * 100).toFixed(1);
    };

    if (loading) {
        return (
            <Card 
                title="AI Quality Analytics" 
                className="quality-score-card"
                style={{ minHeight: 400 }}
            >
                <div style={{ textAlign: 'center', padding: '50px 0' }}>
                    <Spin size="large" />
                    <p style={{ marginTop: 16, color: '#666' }}>Loading quality metrics...</p>
                </div>
            </Card>
        );
    }

    if (error) {
        return (
            <Card 
                title="AI Quality Analytics" 
                className="quality-score-card"
            >
                <Alert
                    message="Error Loading Quality Data"
                    description={error}
                    type="error"
                    showIcon
                    action={
                        <button onClick={fetchQualityScores} style={{ border: 'none', background: 'none', color: '#1890ff', cursor: 'pointer' }}>
                            Retry
                        </button>
                    }
                />
            </Card>
        );
    }

    return (
        <Card 
            title={
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <TrophyOutlined style={{ color: '#faad14' }} />
                    AI Quality Analytics
                </div>
            }
            className="quality-score-card"
            extra={
                <div style={{ fontSize: '12px', color: '#666' }}>
                    {qualityData?.period}
                </div>
            }
            style={{ height: '100%' }}
        >
            <Row gutter={[16, 24]}>
                {/* Overall Quality Score - Prominent Display */}
                <Col span={24}>
                    <div style={{ textAlign: 'center', marginBottom: 24 }}>
                        <Statistic
                            title="Overall Quality Score"
                            value={formatScore(qualityData?.overall || 0)}
                            precision={1}
                            suffix="%"
                            valueStyle={{ 
                                color: getScoreColor(qualityData?.overall || 0),
                                fontSize: '2.5rem',
                                fontWeight: 'bold'
                            }}
                        />
                        <div style={{ 
                            marginTop: 8,
                            padding: '4px 12px',
                            backgroundColor: getScoreColor(qualityData?.overall || 0),
                            color: 'white',
                            borderRadius: '12px',
                            display: 'inline-block',
                            fontSize: '12px',
                            fontWeight: 'bold'
                        }}>
                            {getScoreLabel(qualityData?.overall || 0)}
                        </div>
                    </div>
                </Col>
                
                {/* 5-Dimensional Quality Metrics */}
                <Col span={12}>
                    <div className="quality-metric">
                        <div className="metric-label" style={{ 
                            fontSize: '14px', 
                            fontWeight: '500', 
                            marginBottom: '8px',
                            color: '#262626'
                        }}>
                            📊 Relevance
                        </div>
                        <Progress
                            percent={Math.round((qualityData?.relevance || 0) * 100)}
                            strokeColor={getScoreColor(qualityData?.relevance || 0)}
                            trailColor="#f0f0f0"
                            strokeWidth={12}
                            format={() => `${formatScore(qualityData?.relevance || 0)}%`}
                            style={{ fontSize: '12px' }}
                        />
                    </div>
                </Col>
                
                <Col span={12}>
                    <div className="quality-metric">
                        <div className="metric-label" style={{ 
                            fontSize: '14px', 
                            fontWeight: '500', 
                            marginBottom: '8px',
                            color: '#262626'
                        }}>
                            🎯 Accuracy
                        </div>
                        <Progress
                            percent={Math.round((qualityData?.accuracy || 0) * 100)}
                            strokeColor={getScoreColor(qualityData?.accuracy || 0)}
                            trailColor="#f0f0f0"
                            strokeWidth={12}
                            format={() => `${formatScore(qualityData?.accuracy || 0)}%`}
                        />
                    </div>
                </Col>
                
                <Col span={12}>
                    <div className="quality-metric">
                        <div className="metric-label" style={{ 
                            fontSize: '14px', 
                            fontWeight: '500', 
                            marginBottom: '8px',
                            color: '#262626'
                        }}>
                            ✅ Completeness
                        </div>
                        <Progress
                            percent={Math.round((qualityData?.completeness || 0) * 100)}
                            strokeColor={getScoreColor(qualityData?.completeness || 0)}
                            trailColor="#f0f0f0"
                            strokeWidth={12}
                            format={() => `${formatScore(qualityData?.completeness || 0)}%`}
                        />
                    </div>
                </Col>
                
                <Col span={12}>
                    <div className="quality-metric">
                        <div className="metric-label" style={{ 
                            fontSize: '14px', 
                            fontWeight: '500', 
                            marginBottom: '8px',
                            color: '#262626'
                        }}>
                            💡 Clarity
                        </div>
                        <Progress
                            percent={Math.round((qualityData?.clarity || 0) * 100)}
                            strokeColor={getScoreColor(qualityData?.clarity || 0)}
                            trailColor="#f0f0f0"
                            strokeWidth={12}
                            format={() => `${formatScore(qualityData?.clarity || 0)}%`}
                        />
                    </div>
                </Col>
                
                <Col span={24}>
                    <div className="quality-metric">
                        <div className="metric-label" style={{ 
                            fontSize: '14px', 
                            fontWeight: '500', 
                            marginBottom: '8px',
                            color: '#262626'
                        }}>
                            🤝 Helpfulness
                        </div>
                        <Progress
                            percent={Math.round((qualityData?.helpfulness || 0) * 100)}
                            strokeColor={getScoreColor(qualityData?.helpfulness || 0)}
                            trailColor="#f0f0f0"
                            strokeWidth={12}
                            format={() => `${formatScore(qualityData?.helpfulness || 0)}%`}
                        />
                    </div>
                </Col>
            </Row>
            
            {/* Footer Information */}
            <div style={{ 
                marginTop: 24,
                padding: '12px 16px',
                backgroundColor: '#fafafa',
                borderRadius: '6px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                fontSize: '12px',
                color: '#666'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <BarChartOutlined />
                    <span>Based on {qualityData?.interactions_analyzed || 0} interactions</span>
                </div>
                <div>
                    Last updated: {new Date().toLocaleTimeString()}
                </div>
            </div>
            
            {/* Quality Insights */}
            {qualityData?.overall && (
                <div style={{ marginTop: 16 }}>
                    <div style={{ fontSize: '13px', fontWeight: '500', marginBottom: 8, color: '#262626' }}>
                        💡 Quality Insights
                    </div>
                    <div style={{ fontSize: '12px', color: '#666', lineHeight: '1.5' }}>
                        {qualityData.overall >= 0.9 && "🎉 Excellent! Your AI interactions are of exceptional quality."}
                        {qualityData.overall >= 0.8 && qualityData.overall < 0.9 && "👍 Great job! Your AI interactions show strong quality metrics."}
                        {qualityData.overall >= 0.7 && qualityData.overall < 0.8 && "📈 Good progress! Consider focusing on areas with lower scores."}
                        {qualityData.overall < 0.7 && "🎯 Room for improvement. Try asking more specific questions for better results."}
                    </div>
                </div>
            )}
        </Card>
    );
};

export default QualityScoreCard;