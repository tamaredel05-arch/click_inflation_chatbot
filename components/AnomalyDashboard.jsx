import React, { useState } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';

export default function AnomalyDashboard({ data }) {
  const [currentLevel, setCurrentLevel] = useState(1);
  const [selectedMediaSource, setSelectedMediaSource] = useState(null);
  const [selectedHour, setSelectedHour] = useState(null);

  // פונקציה לקביעת סטייל שורה לפי חומרה (cv - coefficient of variation)
  const getRowStyle = (cv) => {
    if (cv >= 2.0) {
      return {
        backgroundColor: '#ffebee',
        borderRight: '4px solid #e53935'
      };
    }
    if (cv >= 1.0) {
      return {
        backgroundColor: '#fff3e0',
        borderRight: '4px solid #fb8c00'
      };
    }
    return {
      backgroundColor: 'white'
    };
  };

  return (
    <div style={{ 
      direction: 'ltr', 
      fontFamily: 'Arial, sans-serif',
      maxWidth: '1200px',
      margin: '0 auto'
    }}>
      {currentLevel === 1 && <Level1View />}
      {currentLevel === 2 && <Level2View />}
      {currentLevel === 3 && <Level3View />}
    </div>
  );

  // =====================
  // LEVEL 1: טבלת Top 10
  // =====================
  function Level1View() {
    return (
      <div>
        {/* כותרת כחולה עליונה */}
        <div style={{
          background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)',
          color: 'white',
          padding: '30px',
          borderRadius: '15px 15px 0 0',
          textAlign: 'center',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)'
        }}>
          <h1 style={{
            fontSize: '28px',
            fontWeight: 'bold',
            margin: '0 0 10px 0'
          }}>
            Agent scanned 3,391,569 sources and found 20 anomalies
          </h1>
          <p style={{
            fontSize: '14px',
            opacity: 0.95,
            margin: 0
          }}>
            (Algorithm: Average + Standard Deviation by hour + Comparison to previous day)
          </p>
        </div>

        {/* גוף הטבלה */}
        <div style={{
          backgroundColor: 'white',
          padding: '30px',
          borderRadius: '0 0 15px 15px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
        }}>
          {/* כותרת משנה */}
          <h2 style={{
            color: '#d32f2f',
            fontSize: '22px',
            fontWeight: 'bold',
            marginBottom: '25px',
            paddingBottom: '15px',
            borderBottom: '2px solid #f0f0f0',
            textAlign: 'center'
          }}>
            Abnormal click traffic on media sources
          </h2>

          {/* הטבלה */}
          <table style={{
            width: '100%',
            borderCollapse: 'collapse',
            backgroundColor: 'white'
          }}>
            {/* כותרות עמודות */}
            <thead>
              <tr style={{
                backgroundColor: '#fafafa',
                borderBottom: '2px solid #e0e0e0'
              }}>
                <th style={{
                  padding: '15px',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  color: '#333'
                }}>#</th>
                <th style={{
                  padding: '15px',
                  textAlign: 'left',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  color: '#333'
                }}>Media Source</th>
                <th style={{
                  padding: '15px',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  color: '#333'
                }}>Hour</th>
                <th style={{
                  padding: '15px',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  color: '#333'
                }}>Average</th>
                <th style={{
                  padding: '15px',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  color: '#333'
                }}>CV Rate</th>
                <th style={{
                  padding: '15px',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  color: '#333'
                }}>Std Deviation</th>
                <th style={{
                  padding: '15px',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  color: '#333'
                }}>Action</th>
              </tr>
            </thead>

            {/* שורות הנתונים */}
            <tbody>
              {data.level1.media_sources.map((source, index) => {
                const rowStyle = getRowStyle(source.cv);
                
                return (
                  <tr 
                    key={source.id}
                    style={{
                      ...rowStyle,
                      borderBottom: '1px solid #f0f0f0',
                      transition: 'all 0.2s ease',
                      cursor: 'pointer'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#e3f2fd';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = rowStyle.backgroundColor;
                    }}
                  >
                    {/* עמודה 1: מספר סידורי */}
                    <td style={{
                      padding: '15px',
                      textAlign: 'center',
                      fontWeight: 'bold',
                      color: '#666',
                      fontSize: '14px'
                    }}>
                      {index + 1}
                    </td>

                    {/* עמודה 2: שם מקור המדיה */}
                    <td style={{
                      padding: '15px',
                      textAlign: 'left',
                      fontFamily: 'Courier New, monospace',
                      fontSize: '13px',
                      color: '#333'
                    }}>
                      {source.media_source}
                    </td>

                    {/* עמודה 3: שעה */}
                    <td style={{
                      padding: '15px',
                      textAlign: 'center',
                      fontSize: '14px',
                      color: '#333',
                      fontWeight: 'bold'
                    }}>
                      {source.hr}:00
                    </td>

                    {/* עמודה 4: ממוצע */}
                    <td style={{
                      padding: '15px',
                      textAlign: 'center',
                      fontSize: '14px',
                      color: '#333'
                    }}>
                      {source.mean_3d.toFixed(2)}
                    </td>

                    {/* עמודה 5: שיעור סטייה */}
                    <td style={{
                      padding: '15px',
                      textAlign: 'center'
                    }}>
                      <span style={{
                        color: source.cv >= 2.0 ? '#e53935' : 
                               source.cv >= 1.0 ? '#fb8c00' : '#43a047',
                        fontWeight: 'bold',
                        fontSize: '16px'
                      }}>
                        {/* אייקון לפי חומרה */}
                        {source.cv >= 2.0 ? '🔥 ' : 
                         source.cv >= 1.0 ? '⚠️ ' : ''}
                        {source.cv.toFixed(2)}
                      </span>
                    </td>

                    {/* עמודה 6: סטייה מהממוצע */}
                    <td style={{
                      padding: '15px',
                      textAlign: 'center',
                      fontWeight: 'bold',
                      color: '#666',
                      fontSize: '14px'
                    }}>
                      {source.std_3d.toFixed(2)}
                    </td>

                    {/* עמודה 7: כפתור פעולה */}
                    <td style={{
                      padding: '15px',
                      textAlign: 'center'
                    }}>
                      <button
                        onClick={() => {
                          setSelectedMediaSource(source.media_source);
                          setCurrentLevel(2);
                        }}
                        style={{
                          background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)',
                          color: 'white',
                          border: 'none',
                          padding: '10px 25px',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontWeight: 'bold',
                          fontSize: '14px',
                          boxShadow: '0 2px 6px rgba(0,0,0,0.2)',
                          transition: 'all 0.3s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.target.style.transform = 'translateY(-2px)';
                          e.target.style.boxShadow = '0 4px 10px rgba(0,0,0,0.3)';
                        }}
                        onMouseLeave={(e) => {
                          e.target.style.transform = 'translateY(0)';
                          e.target.style.boxShadow = '0 2px 6px rgba(0,0,0,0.2)';
                        }}
                      >
                        View Details →
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    );
  }


  // =====================
  // LEVEL 2: גרף LineChart
  // =====================
  function Level2View() {
    // מציאת הנתונים של המקור הנבחר
    const rawData = data.level2?.[selectedMediaSource] || [];
    
    // יצירת timestamp מ-event_date ו-event_hour
    const chartData = rawData.map((item, index) => {
      const dayNum = Math.floor(index / 24) + 1;
      const timestamp = `Day ${dayNum} ${String(item.event_hour).padStart(2, '0')}:00`;
      
      return {
        timestamp: timestamp,
        clicks: item.total_clicks,
        hour: item.event_hour,
        date: item.event_date
      };
    });
    
    return (
      <div style={{
        backgroundColor: 'white',
        padding: '30px',
        borderRadius: '15px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        {/* כותרת */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '30px'
        }}>
          <h2 style={{ 
            color: '#2196f3', 
            fontSize: '24px',
            margin: 0
          }}>
            Click Traffic - {selectedMediaSource}
          </h2>
          <button
            onClick={() => setCurrentLevel(1)}
            style={{
              background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)',
              color: 'white',
              border: 'none',
              padding: '10px 20px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontWeight: 'bold',
              fontSize: '14px'
            }}
          >
            ← Back to Table
          </button>
        </div>

        {/* גרף */}
        <div style={{
          overflowX: 'auto',
          overflowY: 'hidden',
          paddingBottom: '20px'
        }}>
          <div style={{ minWidth: '1800px' }}>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="timestamp" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  label={{ value: 'Clicks', angle: -90, position: 'insideLeft' }}
                />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="clicks" 
                  stroke="#2196f3" 
                  strokeWidth={2}
                  dot={{ r: 3 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* מידע על הדאטה */}
        <div style={{
          marginTop: '20px',
          padding: '15px',
          backgroundColor: '#f5f5f5',
          borderRadius: '8px',
          textAlign: 'left',
          fontSize: '14px',
          color: '#666'
        }}>
          <strong>Data:</strong> 3 days × 24 hours = 72 data points
        </div>
      </div>
    );
  }

  // =====================
  // LEVEL 3: Drill Down (בקרוב)
  // =====================
  function Level3View() {
    return (
      <div style={{
        backgroundColor: 'white',
        padding: '40px',
        borderRadius: '15px',
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ color: '#2196f3', fontSize: '24px' }}>
          Level 3: Drill Down
        </h2>
        <p style={{ color: '#666', fontSize: '16px', marginTop: '20px' }}>
          Coming soon: Detailed analysis
        </p>
      </div>
    );
  }
}
