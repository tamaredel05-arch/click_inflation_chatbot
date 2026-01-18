import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ReferenceLine,
  BarChart,
  Bar
} from 'recharts';

export default function AnomalyDashboard({ data: propData, media }) {
  const [currentLevel, setCurrentLevel] = useState(1);
  const [selectedMediaSource, setSelectedMediaSource] = useState(null);
  const [selectedHour, setSelectedHour] = useState(null);

  // Function to determine row style by severity (cv - coefficient of variation)
  const getRowStyle = (cv) => {
    if (cv >= 2.0) {
      return {
        background: 'linear-gradient(90deg, #f3e5f5 0%, #e1bee7 50%, #ce93d8 100%)',
        borderRight: '4px solid #9c27b0'
      };
    }
    if (cv >= 1.0) {
      return {
        background: 'linear-gradient(90deg, #f0f9ff 0%, #e0f2fe 50%, #bae6fd 100%)',
        borderRight: '4px solid #2196f3'
      };
    }
    return {
      background: 'linear-gradient(90deg, #fafafa 0%, #ffffff 50%, #f5f5f5 100%)'
    };
  };

  return (
    <div style={{ 
      direction: 'ltr', 
      fontFamily: 'Arial, sans-serif',
      width: '100%',
      maxWidth: '100%',
      overflow: 'auto',
      maxHeight: '80vh'
    }}>
      {currentLevel === 1 && <Level1View media={media} />}
      {currentLevel === 2 && <Level2View  media={media} />}
      {currentLevel === 3 && <Level3View media={media} />}
    </div>
  );

  // =====================
  // LEVEL 1: Top 10 Table
  // =====================
  function Level1View({ media }) {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
      const fetchData = async () => {
        try {
          setLoading(true);
          const response = await fetch(`http://127.0.0.1:8000/api/anomalies/top10?media=${media}`);
          if (!response.ok) {
            throw new Error('Failed to fetch data');
          }
          const jsonData = await response.json();
          setData(jsonData);
        } catch (err) {
          setError(err.message);

        } finally {
          setLoading(false);
        }
      };
      
      fetchData();
    }, [media]);

    if (loading) return <div style={{ padding: '40px', textAlign: 'center', fontSize: '18px' }}>Loading data...</div>;
    if (error) return <div style={{ padding: '40px', textAlign: 'center', fontSize: '18px', color: '#d32f2f' }}>Error: {error}</div>;


    console.log('data - LevelView1 --> ', data)
    return (
      <div style={{
        background: 'linear-gradient(120deg, #e3f7ff 0%, #f5faff 40%, #e3f7ff 100%)',
        borderRadius: '20px',
        boxShadow: '0 8px 32px 0 #00eaff33, 0 1.5px 12px #7f00ff22',
        overflow: 'hidden',
        marginBottom: '32px',
        marginTop: '10px',
        padding: 0,
        position: 'relative',
      }}>
        {/* Top blue header */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '14px 24px',
          borderRadius: '16px',
          textAlign: 'center',
          boxShadow: '0 4px 16px rgba(102, 126, 234, 0.5)',
          marginBottom: '20px',
        }}>
          <h1 style={{
            fontSize: '16px',
            fontWeight: '600',
            margin: '0',
            letterSpacing: '0.4px',
            textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
          }}>
            Abnormal click traffic on {media === 'partner' ? 'Partner' : 'Media Sources'}
          </h1>
        </div>

        {/* Table body */}
        <div style={{
          background: 'rgba(255,255,255,0.95)',
          padding: '20px',
          borderRadius: '0 0 12px 12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        }}>

          {/* Table wrapper with overflow */}
          <div style={{
            overflowX: 'auto',
            maxWidth: '100%',
            WebkitOverflowScrolling: 'touch'
          }}>
            {/* The table */}
            <table style={{
              width: '100%',
              minWidth: '600px',
              borderCollapse: 'separate',
              borderSpacing: '0 8px',
              backgroundColor: 'transparent',
              tableLayout: 'fixed'
            }}>
            {/* Column headers */}
            <thead>
              <tr style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.3)',
              }}>
                <th style={{
                  padding: '14px 8px',
                  textAlign: 'center',
                  fontWeight: '700',
                  fontSize: '12px',
                  color: 'white',
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                  borderRight: '1px solid rgba(255, 255, 255, 0.15)',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                  width: '6%',
                  whiteSpace: 'nowrap',
                  borderTopLeftRadius: '12px',
                  borderBottomLeftRadius: '12px'
                }}>#</th>
                <th style={{
                  padding: '14px 8px',
                  textAlign: 'left',
                  fontWeight: '700',
                  fontSize: '12px',
                  color: 'white',
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                  borderRight: '1px solid rgba(255, 255, 255, 0.15)',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                  width: '26%',
                  whiteSpace: 'nowrap'
                }}>{media === 'partner' ? 'Partner' : 'Media Source'}</th>
                <th style={{
                  padding: '14px 8px',
                  textAlign: 'center',
                  fontWeight: '700',
                  fontSize: '12px',
                  color: 'white',
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                  borderRight: '1px solid rgba(255, 255, 255, 0.15)',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                  width: '10%',
                  whiteSpace: 'nowrap'
                }}>Hour</th>
                <th style={{
                  padding: '14px 8px',
                  textAlign: 'center',
                  fontWeight: '700',
                  fontSize: '12px',
                  color: 'white',
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                  borderRight: '1px solid rgba(255, 255, 255, 0.15)',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                  width: '13%',
                  whiteSpace: 'nowrap'
                }}>Average</th>
                <th style={{
                  padding: '14px 8px',
                  textAlign: 'center',
                  fontWeight: '700',
                  fontSize: '12px',
                  color: 'white',
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                  borderRight: '1px solid rgba(255, 255, 255, 0.15)',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                  width: '13%',
                  whiteSpace: 'nowrap'
                }}>CV Rate</th>
                <th style={{
                  padding: '14px 8px',
                  textAlign: 'center',
                  fontWeight: '700',
                  fontSize: '12px',
                  color: 'white',
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                  borderRight: '1px solid rgba(255, 255, 255, 0.15)',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                  width: '13%',
                  whiteSpace: 'nowrap'
                }}>Std Dev</th>
                <th style={{
                  padding: '14px 8px',
                  textAlign: 'center',
                  fontWeight: '700',
                  fontSize: '12px',
                  color: 'white',
                  letterSpacing: '1px',
                  textTransform: 'uppercase',
                  textShadow: '0 1px 2px rgba(0, 0, 0, 0.3)',
                  width: '19%',
                  whiteSpace: 'nowrap',
                  borderTopRightRadius: '12px',
                  borderBottomRightRadius: '12px'
                }}>Action</th>
              </tr>
            </thead>

            {/* Data rows */}
            <tbody>
              {data.level1.media_sources.map((source, index) => {
                const rowStyle = getRowStyle(source.cv);
                
                return (
                  <tr 
                    key={source.id}
                    style={{
                      ...rowStyle,
                      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
                      borderRadius: '10px',
                      transition: 'all 0.3s ease',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.background = 'linear-gradient(90deg, #f8f7ff 0%, #ede9fe 50%, #ddd6fe 100%)';
                      e.currentTarget.style.boxShadow = '0 6px 20px rgba(107, 33, 168, 0.2)';
                      e.currentTarget.style.transform = 'translateY(-2px)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.background = rowStyle.background;
                      e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
                      e.currentTarget.style.transform = 'translateY(0)';
                    }}
                  >
                    {/* Column 1: Serial number */}
                    <td style={{
                      padding: '12px 8px',
                      textAlign: 'center',
                      fontWeight: 'bold',
                      color: '#666',
                      fontSize: '13px',
                      borderTopLeftRadius: '10px',
                      borderBottomLeftRadius: '10px'
                    }}>
                      {index + 1}
                    </td>

                    {/* Column 2: Media source name */}
                    <td style={{
                      padding: '12px 8px',
                      textAlign: 'left',
                      fontFamily: 'Courier New, monospace',
                      fontSize: '12px',
                      color: '#333',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      fontWeight: '500'
                    }}>
                      {source.media_source}
                    </td>

                    {/* Column 3: Hour */}
                    <td style={{
                      padding: '12px 8px',
                      textAlign: 'center',
                      fontSize: '13px',
                      color: '#333',
                      fontWeight: 'bold'
                    }}>
                      {source.hr}:00
                    </td>

                    {/* Column 4: Average */}
                    <td style={{
                      padding: '12px 8px',
                      textAlign: 'center',
                      fontSize: '13px',
                      color: '#333',
                      fontWeight: '500'
                    }}>
                      {source.mean_3d.toFixed(2)}
                    </td>

                    {/* Column 5: Coefficient of variation */}
                    <td style={{
                      padding: '12px 8px',
                      textAlign: 'center'
                    }}>
                      <span style={{
                        color: source.cv >= 2.0 ? '#e53935' : 
                               source.cv >= 1.0 ? '#fb8c00' : '#43a047',
                        fontWeight: 'bold',
                        fontSize: '14px'
                      }}>
                        {/* Icon by severity */}
                        {source.cv >= 2.0 ? '🔥 ' : 
                         source.cv >= 1.0 ? '⚠️ ' : ''}
                        {source.cv.toFixed(2)}
                      </span>
                    </td>

                    {/* Column 6: Standard deviation */}
                    <td style={{
                      padding: '12px 8px',
                      textAlign: 'center',
                      fontWeight: '600',
                      color: '#666',
                      fontSize: '13px'
                    }}>
                      {source.std_3d.toFixed(2)}
                    </td>

                    {/* Column 7: Action button */}
                    <td style={{
                      padding: '12px 8px',
                      textAlign: 'center',
                      borderTopRightRadius: '10px',
                      borderBottomRightRadius: '10px'
                    }}>
                      <button
                        onClick={() => {
                          setSelectedMediaSource(source.media_source);
                          setCurrentLevel(2);
                        }}
                        style={{
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          color: 'white',
                          border: 'none',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          cursor: 'pointer',
                          fontWeight: 'bold',
                          fontSize: '12px',
                          boxShadow: '0 2px 8px rgba(102, 126, 234, 0.4)',
                          transition: 'all 0.3s ease',
                          whiteSpace: 'nowrap'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.transform = 'translateY(-2px)';
                          e.target.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.8)';
                          e.target.style.background = 'linear-gradient(135deg, #7c8df8 0%, #8b5cf6 100%)';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.transform = 'translateY(0)';
                          e.target.style.boxShadow = '0 2px 8px rgba(102, 126, 234, 0.4)';
                          e.target.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
                        }}
                      >
                        View →
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          </div>
        </div>
      </div>
    );
  }


  // =====================
  // LEVEL 2: LineChart Graph
  // =====================
  function Level2View({ media }) {
    const [data, setData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
      const fetchData = async () => {
        try {
          setLoading(true);
          const response = await fetch(`http://127.0.0.1:8000/api/anomalies/all-clicks?media=${media}`);
          if (!response.ok) {
            throw new Error('Failed to fetch data');
          }
          const jsonData = await response.json();
          setData(jsonData);
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      };
      
      fetchData();
    }, [media]);

    if (loading) return <div style={{ padding: '40px', textAlign: 'center', fontSize: '18px' }}>Loading data...</div>;
    if (error) return <div style={{ padding: '40px', textAlign: 'center', fontSize: '18px', color: '#d32f2f' }}>Error: {error}</div>;

    // Find data for the selected media source
    const rawData = data.level2?.[selectedMediaSource] || [];
    
    // Sort data by date and hour
    const sortedData = [...rawData].sort((a, b) => {
      if (a.event_date !== b.event_date) {
        return a.event_date.localeCompare(b.event_date);
      }
      return a.event_hour - b.event_hour;
    });
    
    console.log('data - LevelView2 --> ', data)
    console.log('sortedData length:', sortedData.length);

    // Create array of 72 points (3 days × 24 hours) - auto-fill
    const chartData = [];
    
    if (sortedData.length > 0) {
      // Get the first date
      const firstDate = new Date(sortedData[0].event_date);
      
      // Create 72 points (3 days)
      for (let dayOffset = 0; dayOffset < 3; dayOffset++) {
        for (let hour = 0; hour < 24; hour++) {
          const currentDate = new Date(firstDate);
          currentDate.setDate(firstDate.getDate() + dayOffset);
          const dateStr = currentDate.toISOString().split('T')[0];
          
          // Search for existing data for this date and hour
          const existingData = sortedData.find(
            item => item.event_date === dateStr && item.event_hour === hour
          );
          
          const index = dayOffset * 24 + hour;
          const hourDisplay = `${String(hour).padStart(2, '0')}:00`;
          
          chartData.push({
            index: index,
            hourDisplay: hourDisplay,
            clicks: existingData ? existingData.total_clicks : 0,
            hour: hour,
            date: dateStr,
            dayNum: dayOffset + 1
          });
        }
      }
    }
    
    console.log('chartData length (should be 72):', chartData.length);
    
    // Custom Tooltip
    const CustomTooltip = ({ active, payload }) => {
      if (active && payload && payload.length) {
        return (
          <div style={{
            backgroundColor: 'white',
            padding: '10px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          }}>
            <p style={{ margin: '0 0 5px 0', fontWeight: 'bold' }}>
              {payload[0].payload.date} - {payload[0].payload.hourDisplay}
            </p>
            <p style={{ margin: 0, color: '#2196f3' }}>
              Clicks: {payload[0].value.toLocaleString()}
            </p>
          </div>
        );
      }
      return null;
    };
    
    return (
      <div style={{
        backgroundColor: 'rgba(255,255,255,0.95)',
        padding: '20px',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        width: '100%',
        maxWidth: '100%',
        overflow: 'hidden',
        boxSizing: 'border-box'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '14px 24px',
          borderRadius: '16px',
          marginBottom: '20px',
          boxShadow: '0 4px 16px rgba(102, 126, 234, 0.3)',
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '10px',
          width: '100%',
          boxSizing: 'border-box'
        }}>
          <h2 style={{ 
            color: 'white',
            fontSize: '16px',
            margin: 0,
            fontWeight: '600',
            letterSpacing: '0.4px',
            textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
          }}>
            Click Traffic - {selectedMediaSource}
          </h2>
          <button
            onClick={() => setCurrentLevel(1)}
            style={{
              background: 'white',
              color: '#667eea',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              padding: '8px 16px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '13px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={e => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
            }}
            onMouseLeave={e => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
            }}
          >
            ← Back
          </button>
        </div>

        {/* Message */}
        <div style={{
          textAlign: 'left',
          padding: '8px 16px',
          marginTop: '12px',
          marginBottom: '15px',
          background: 'linear-gradient(135deg, #f0f4ff 0%, #e8efff 100%)',
          borderRadius: '8px',
          border: '1px solid #d0deff',
          width: '100%',
          boxSizing: 'border-box'
        }}>
          <p style={{
            margin: 0,
            fontSize: '12px',
            fontWeight: '500',
            color: '#4a5568',
            letterSpacing: '0.2px'
          }}>
            💡 To view application data, select the anomaly hour
          </p>
        </div>

        {/* Chart */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
          overflowX: 'auto',
          overflowY: 'hidden',
          maxWidth: '100%',
          WebkitOverflowScrolling: 'touch'
        }}>
          <div style={{ minWidth: '1200px', width: '100%' }}>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="index"
                  tickFormatter={(index) => chartData[index]?.hourDisplay || ''}
                  angle={-45}
                  textAnchor="end"
                  height={80}
                  tick={{ fontSize: 10 }}
                  interval={3}
                />
                <YAxis 
                  label={{ value: 'Clicks', angle: -90, position: 'insideLeft' }}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                {/* Lines separating days */}
                <ReferenceLine x={23} stroke="#7f00ff" strokeWidth={2} strokeDasharray="5 5" label={{ value: 'Day 2', position: 'top', fill: '#7f00ff', fontSize: 12 }} />
                <ReferenceLine x={47} stroke="#7f00ff" strokeWidth={2} strokeDasharray="5 5" label={{ value: 'Day 3', position: 'top', fill: '#7f00ff', fontSize: 12 }} />
                <Line 
                  type="monotone" 
                  dataKey="clicks" 
                  stroke="#2196f3" 
                  strokeWidth={2}
                  dot={{ r: 4 }}
                  activeDot={{ 
                    r: 8,
                    cursor: 'pointer',
                    onClick: (e, payload) => {
                      setSelectedHour({
                        date: payload.payload.date,
                        hour: payload.payload.hour
                      });
                      setCurrentLevel(3);
                    }
                  }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Data information */}
        <div style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          textAlign: 'left',
          fontSize: '14px',
          color: '#666'
        }}>
          <strong>Data:</strong> {chartData.length} data points 
          {chartData.length > 0 && ` (${chartData[0]?.date} to ${chartData[chartData.length - 1]?.date})`}
        </div>
      </div>
    );
  }

  // =====================
  // LEVEL 3: Bar Chart - App Breakdown
  // =====================
  function Level3View({media}) {
    const [data, setData] = useState({});
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
      const fetchData = async () => {
        try {
          setLoading(true);
          const response = await fetch(`http://127.0.0.1:8000/api/anomalies/app-breakdown?media=${media}`);
          if (!response.ok) {
            throw new Error('Failed to fetch data');
          }
          const jsonData = await response.json();
          setData(jsonData);
        } catch (err) {
          setError(err.message);
        } finally {
          setLoading(false);
        }
      };
      
      fetchData();
    }, [media]);
    console.log('data - LevelView2 --> ', data)
    if (loading) return <div style={{ padding: '40px', textAlign: 'center', fontSize: '18px' }}>Loading data...</div>;
    if (error) return <div style={{ padding: '40px', textAlign: 'center', fontSize: '18px', color: '#d32f2f' }}>Error: {error}</div>;

    // Build the key to get app data for the selected media_source + date + hour
    const key = selectedHour 
      ? `${selectedMediaSource}_${selectedHour.date}_${selectedHour.hour}`
      : null;
    
    console.log("=== Level3 Debug ===");
    console.log("selectedMediaSource:", selectedMediaSource);
    console.log("selectedHour:", selectedHour);
    console.log("Key built:", key);
    console.log("data.level3:", data.level3);
    console.log("Available keys:", data.level3 ? Object.keys(data.level3).slice(0, 10) : []);
    
    const appsData = key ? (data.level3?.[key] || []) : [];
    console.log("appsData found:", appsData.length);
    
    // Sort by total_clicks descending and take top 15
    const sortedApps = [...appsData]
      .sort((a, b) => b.total_clicks - a.total_clicks)
      .slice(0, 15);
    
    return (
      <div style={{
        backgroundColor: 'rgba(255,255,255,0.95)',
        padding: '20px',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
        width: '100%',
        maxWidth: '100%',
        overflow: 'hidden',
        boxSizing: 'border-box'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '14px 24px',
          borderRadius: '16px',
          marginBottom: '20px',
          boxShadow: '0 4px 16px rgba(102, 126, 234, 0.3)',
          display: 'flex',
          flexWrap: 'wrap',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '10px',
          width: '100%',
          boxSizing: 'border-box'
        }}>
          <h2 style={{ 
            color: 'white',
            fontSize: '16px',
            margin: 0,
            fontWeight: '600',
            letterSpacing: '0.4px',
            textShadow: '0 2px 8px rgba(0, 0, 0, 0.3)',
          }}>
            App Breakdown - {selectedMediaSource}
          </h2>
          <button
            onClick={() => setCurrentLevel(2)}
            style={{
              background: 'white',
              color: '#667eea',
              border: '2px solid rgba(255, 255, 255, 0.3)',
              padding: '8px 16px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '13px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
              transition: 'all 0.3s ease'
            }}
            onMouseEnter={(e) => {
              e.target.style.transform = 'translateY(-2px)';
              e.target.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)';
            }}
          >
            ← Back
          </button>
        </div>

        {/* Message */}
        <div style={{
          textAlign: 'left',
          padding: '8px 16px',
          marginTop: '12px',
          marginBottom: '15px',
          background: 'linear-gradient(135deg, #f0f4ff 0%, #e8efff 100%)',
          borderRadius: '8px',
          border: '1px solid #d0deff',
          width: '100%',
          boxSizing: 'border-box'
        }}>
          <p style={{
            margin: 0,
            fontSize: '12px',
            fontWeight: '500',
            color: '#4a5568',
            letterSpacing: '0.2px'
          }}>
            📅 {selectedHour?.date} at {String(selectedHour?.hour).padStart(2, '0')}:00 - Top Apps by Click Volume
          </p>
        </div>

        {/* Chart */}
        {sortedApps.length > 0 ? (
          <div style={{
            background: 'white',
            borderRadius: '12px',
            padding: '20px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.08)',
            overflowX: 'auto',
            overflowY: 'hidden',
            maxWidth: '100%',
            WebkitOverflowScrolling: 'touch'
          }}>
            <div style={{
              minWidth: 'min(800px, 100%)',
              width: sortedApps.length > 8 ? `${sortedApps.length * 80}px` : '100%',
              maxWidth: '100%'
            }}>
              <ResponsiveContainer width="100%" height={420}>
                <BarChart data={sortedApps} barCategoryGap={"10%"}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
                  <XAxis 
                    dataKey="app_id" 
                    angle={-45}
                    textAnchor="end"
                    height={120}
                    tick={{ fontSize: 11, fill: '#4a5568', fontFamily: 'Consolas, monospace' }}
                  />
                  <YAxis 
                    label={{ value: 'Total Clicks', angle: -90, position: 'insideLeft', style: { fill: '#667eea', fontWeight: 600 } }}
                    tick={{ fill: '#4a5568', fontSize: 12 }}
                  />
                  <Tooltip 
                    contentStyle={{
                      background: 'white',
                      border: '2px solid #667eea',
                      borderRadius: '10px',
                      boxShadow: '0 4px 18px rgba(102, 126, 234, 0.3)',
                      color: '#4a5568',
                      fontWeight: 500
                    }}
                    labelStyle={{ color: '#667eea', fontWeight: 700 }}
                    formatter={(value) => [value.toLocaleString(), 'Clicks']}
                    cursor={{ fill: 'rgba(102, 126, 234, 0.1)' }}
                  />
                  <Legend 
                    wrapperStyle={{
                      paddingTop: '18px',
                      color: '#4a5568',
                      fontWeight: 600
                    }}
                  />
                  {/* Colored bars */}
                  <Bar 
                    dataKey="total_clicks" 
                    fill="url(#purpleBlueGradient)" 
                    name="Total Clicks"
                    radius={[8, 8, 0, 0]}
                    barSize={60}
                    activeBar={{ fill: 'url(#purpleBlueGradientHover)' }}
                  />
                  {/* Define purple-blue gradient */}
                  <defs>
                    <linearGradient id="purpleBlueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#667eea" stopOpacity={1}/>
                      <stop offset="100%" stopColor="#764ba2" stopOpacity={1}/>
                    </linearGradient>
                    <linearGradient id="purpleBlueGradientHover" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#7c8df8" stopOpacity={1}/>
                      <stop offset="100%" stopColor="#8b5cf6" stopOpacity={1}/>
                    </linearGradient>
                  </defs>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : (
          <div style={{
            padding: '60px',
            textAlign: 'center',
            background: 'linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%)',
            borderRadius: '12px',
            color: '#667eea',
            border: '2px dashed #d0deff',
            fontSize: '16px'
          }}>
            <p style={{ fontSize: '16px', margin: 0, fontWeight: '500' }}>
              📊 No app data available for this hour
            </p>
          </div>
        )}

        {/* Data information */}
        <div style={{
          marginTop: '20px',
          padding: '15px',
          background: 'linear-gradient(135deg, #e3f7ff 0%, #f5faff 100%)',
          borderLeft: '4px solid #00eaff',
          borderRadius: '8px',
          color: '#232b39',
          fontWeight: 500
        }}>
          <strong style={{ color: '#00eaff' }}>📊 Analysis:</strong>{' '}
          <span>
            Showing top {sortedApps.length} apps with highest click volume at {selectedHour?.date} {String(selectedHour?.hour).padStart(2, '0')}:00
          </span>
        </div>
      </div>
    );
  }
}
