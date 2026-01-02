'use client';

import { createClient } from '@supabase/supabase-js';
import { useEffect, useState } from 'react';
// 1. IMPORT THE CHARTING LIBRARY
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

export default function Home() {
  // State for the "Live Number"
  const [latestScore, setLatestScore] = useState<number | null>(null);
  const [status, setStatus] = useState<string>('waiting');
  
  // State for the "Graph History"
  const [history, setHistory] = useState<any[]>([]);
  
  // User Input
  const [apiKey, setApiKey] = useState<string>('');

  async function fetchHealth() {
    if (!apiKey) return;

    const { data, error } = await supabase
      .from('health_metrics')
      .select('*')
      .eq('api_key', apiKey)
      .order('created_at', { ascending: false }) // oldest last, and then we reverse it when mapping
      .limit(20);

    if (data && data.length > 0) {
      // 3. THE TRANSFORMATION: Clean up the data for the graph
      const formattedHistory = data.slice().reverse().map(item => ({ // we use slice as .reverse modifies the original array
        time: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        // Convert 0.2 -> 20 (Percent)
        score: item.score * 100 
      }));
      
      setHistory(formattedHistory);

      // Set the "Big Number" to the very last item in the list
      const lastItem = data[0];
      setLatestScore(lastItem.score);
      setStatus(lastItem.status);
    } else {
      setStatus('nodata');
      setHistory([]); // Clear graph if no data
    }
  }

  // Auto-refresh every 2 seconds for that "Live Trading" feel
  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 2000);
    return () => clearInterval(interval);
  }, [apiKey]);

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 text-white p-4 font-sans">
      <div className="w-full max-w-2xl space-y-6">
        
        {/* HEADER */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400">
              Alti Guard
            </h1>
            <p className="text-xs text-zinc-500">Live Observability Platform</p>
          </div>
          <input 
            type="text" 
            placeholder="Enter API Key..."
            className="bg-zinc-900 border border-zinc-800 rounded px-3 py-2 text-sm focus:border-blue-500 outline-none w-48 transition-all"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
          />
        </div>

        {/* MAIN DASHBOARD CARD */}
        <div className={`relative overflow-hidden rounded-xl border p-6 transition-all duration-500 ${
          status === 'critical' ? 'border-red-500/50 bg-red-500/5 shadow-lg shadow-red-500/20' :
          status === 'healthy' ? 'border-emerald-500/50 bg-emerald-500/5 shadow-lg shadow-emerald-500/20' :
          'border-zinc-800 bg-zinc-900'
        }`}>
          
          {/* Top Row: Score and Status */}
          <div className="flex justify-between items-start mb-8">
            <div>
              <p className="text-xs font-medium text-zinc-500 uppercase tracking-widest">Refusal Score</p>
              <h2 className="text-6xl font-bold font-mono mt-2">
                {latestScore !== null ? (latestScore * 100).toFixed(0) : '--'}
                <span className="text-2xl text-zinc-600">%</span>
              </h2>
            </div>
            <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
               status === 'critical' ? 'bg-red-500 text-white' :
               status === 'healthy' ? 'bg-emerald-500 text-white' :
               'bg-zinc-800 text-zinc-500'
            }`}>
              {status}
            </span>
          </div>

          {/* 4. THE GRAPH: This is the visual magic */}
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                  labelStyle={{ color: '#71717a' }}
                />
                <XAxis dataKey="time" hide />
                <YAxis domain={[0, 100]} hide />
                <Line 
                  type="monotone" 
                  dataKey="score" 
                  stroke={status === 'critical' ? '#ef4444' : '#10b981'} 
                  strokeWidth={3}
                  dot={false}
                  activeDot={{ r: 6, fill: '#fff' }}
                  isAnimationActive={false} // Disable animation for smoother "real-time" updates
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          
        </div>
      </div>
    </main>
  );
}